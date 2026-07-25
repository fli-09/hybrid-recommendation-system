import os
import json
import logging
from typing import List, Tuple, Optional, Any, Set, Dict
from .load_models import get_model_registry, ModelRegistry
from ..utils.config import get_project_root

logger = logging.getLogger(__name__)


class InferenceEngine:
    """
    Production recommendation engine interface for real-time inference serving.
    Orchestrates ALS, Content, and Hybrid recommendation pipelines with cold-start fallbacks.
    """

    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        base_dir: str = ".",
        popular_items_path: Optional[str] = None,
    ):
        self.registry: ModelRegistry = registry or get_model_registry(base_dir=base_dir)
        self.project_root: str = get_project_root()

        # Popular items fallback loading
        rel_popular = popular_items_path or "artifacts/models/hybrid/popular_items.json"
        self.popular_items_path = rel_popular if os.path.isabs(rel_popular) else os.path.join(self.project_root, rel_popular)
        self.popular_items: List[Dict[str, Any]] = self._load_popular_items()

    def _load_popular_items(self) -> List[Dict[str, Any]]:
        """Loads precomputed top popular items for cold-start fallback."""
        if not os.path.exists(self.popular_items_path):
            logger.warning(f"Popular items fallback file not found at: {self.popular_items_path}")
            return []

        try:
            with open(self.popular_items_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            logger.info(f"Loaded {len(items)} popular fallback items from {self.popular_items_path}")
            return items
        except Exception as e:
            logger.error(f"Failed to parse popular items fallback JSON: {e}")
            return []

    def recommend(
        self,
        user_id: Any,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Single public entrypoint for user recommendations.

        For known users:
            Generates hybrid recommendations (ALS + Content score fusion).
            Output source: 'Hybrid'

        For unknown users (cold start):
            Falls back to pre-computed popular products.
            Output source: 'Popular'

        Args:
            user_id: User identifier.
            top_n: Number of recommendations to return. Default is 10.

        Returns:
            List of dicts formatted as:
            [
                {
                    "item_id": int,
                    "score": float,
                    "source": "Hybrid" | "Popular"
                },
                ...
            ]
        """
        # Check if user is known in ALS mapping
        is_known = False
        if self.registry.als_predictor and user_id in self.registry.als_predictor.user_to_index:
            is_known = True

        if is_known and self.registry.hybrid_recommender:
            recs = self.registry.hybrid_recommender.predict(user_id=user_id, top_n=top_n)
            if recs:
                return recs

        # Fallback to Popular Items for unknown/cold-start users
        logger.info(f"User ID {user_id} not found or has no candidates. Serving {top_n} popular items fallback.")
        fallback_recs = []
        for item in self.popular_items[:top_n]:
            fallback_recs.append({
                "item_id": int(item["item_id"]),
                "score": float(item.get("score", 1.0)),
                "source": "Popular"
            })

        return fallback_recs

    # ── Backward-compatible helper methods ──────────────────────────────────

    def recommend_for_user(
        self,
        user_id: Any,
        user_history_item_ids: Optional[List[Any]] = None,
        top_n: int = 10,
        strategy: str = "hybrid",
        als_weight: Optional[float] = None,
        content_weight: Optional[float] = None,
        seen_item_ids: Optional[Set[Any]] = None,
    ) -> List[Tuple[Any, float]]:
        """Main recommendation entrypoint returning tuples for legacy callers."""
        strategy = strategy.lower()

        if strategy == "als":
            return self.registry.als_predictor.predict_for_user(
                user_id=user_id,
                top_n=top_n,
                seen_item_ids=seen_item_ids,
            )
        elif strategy == "content":
            if user_history_item_ids:
                recs = self.registry.content_predictor.recommend_for_user_history(
                    history_item_ids=user_history_item_ids,
                    top_n=top_n,
                    seen_items=seen_item_ids,
                )
                return [(r["item_id"], r["score"]) if isinstance(r, dict) else r for r in recs]

            als_recs = self.registry.als_predictor.predict_for_user(
                user_id=user_id,
                top_n=1,
            )
            if not als_recs:
                return []

            seed_item_id = als_recs[0][0]
            recs = self.registry.content_predictor.recommend_similar_items(
                item_id=seed_item_id,
                top_n=top_n,
            )
            return [(r["item_id"], r["score"]) if isinstance(r, dict) else r for r in recs]
        elif strategy == "hybrid":
            is_known = (
                self.registry.als_predictor is not None
                and user_id in self.registry.als_predictor.user_to_index
            )
            if is_known:
                recs = self.registry.hybrid_recommender.recommend(
                    user_id=user_id,
                    user_history_item_ids=user_history_item_ids,
                    top_n=top_n,
                    als_weight=als_weight,
                    content_weight=content_weight,
                    seen_item_ids=seen_item_ids,
                )
                if recs:
                    return recs

            logger.info(
                f"User ID {user_id} not found or has no hybrid candidates. "
                f"Serving {top_n} popular items fallback."
            )
            return [
                (int(item["item_id"]), float(item.get("score", 1.0)))
                for item in self.popular_items[:top_n]
            ]
        else:
            raise ValueError(f"Unknown strategy: '{strategy}'. Choose 'hybrid', 'als', or 'content'.")

    def recommend_similar_items(
        self,
        item_id: Any,
        top_n: int = 10,
    ) -> List[Tuple[Any, float]]:
        """Retrieves top-N items similar to a target item ID."""
        recs = self.registry.content_predictor.recommend_similar_items(item_id=item_id, top_n=top_n)
        return [(r["item_id"], r["score"]) if isinstance(r, dict) else r for r in recs]

    def recommend_hybrid(
        self,
        user_id: Any,
        top_n: int = 10,
        weights: Optional[dict] = None,
        user_history_item_ids: Optional[List[Any]] = None,
        seen_item_ids: Optional[Set[Any]] = None,
    ) -> List[Tuple[Any, float]]:
        als_w = weights.get("als") if weights else None
        content_w = weights.get("content") if weights else None
        return self.recommend_for_user(
            user_id=user_id,
            user_history_item_ids=user_history_item_ids,
            top_n=top_n,
            strategy="hybrid",
            als_weight=als_w,
            content_weight=content_w,
            seen_item_ids=seen_item_ids,
        )

    def recommend_als(
        self,
        user_id: Any,
        top_n: int = 10,
        seen_item_ids: Optional[Set[Any]] = None,
    ) -> List[Tuple[Any, float]]:
        return self.recommend_for_user(
            user_id=user_id,
            top_n=top_n,
            strategy="als",
            seen_item_ids=seen_item_ids,
        )

    def recommend_content_user(
        self,
        user_id: Any,
        top_n: int = 10,
        user_history_item_ids: Optional[List[Any]] = None,
        seen_item_ids: Optional[Set[Any]] = None,
    ) -> List[Tuple[Any, float]]:
        return self.recommend_for_user(
            user_id=user_id,
            user_history_item_ids=user_history_item_ids,
            top_n=top_n,
            strategy="content",
            seen_item_ids=seen_item_ids,
        )

    def recommend_text_search(
        self,
        query: str,
        top_n: int = 10,
    ) -> List[Tuple[Any, float]]:
        recs = self.registry.content_predictor.search_text_query(query=query, top_n=top_n)
        return [(r["item_id"], r["score"]) if isinstance(r, dict) else r for r in recs]
