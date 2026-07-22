import logging
from typing import List, Tuple, Optional, Any, Set, Dict
from ..als.predict import ALSPredictor
from ..als.loader import ALSModelLoader
from ..content.predict import ContentPredictor
from ..content.loader import ContentModelLoader
from .scorer import normalize_scores
from .ranker import fuse_and_rank

logger = logging.getLogger(__name__)


class HybridRecommender:
    """
    Orchestrator class for Hybrid Recommendations combining Collaborative Filtering (ALS)
    and Content-Based Filtering with configurable normalization and fusion strategies.
    """

    def __init__(
        self,
        als_predictor: ALSPredictor,
        content_predictor: ContentPredictor,
        default_als_weight: float = 0.5,
        default_content_weight: float = 0.5,
        default_normalization: str = "minmax",
        default_fusion_strategy: str = "weighted_sum",
    ):
        self.als_predictor = als_predictor
        self.content_predictor = content_predictor
        self.default_als_weight = default_als_weight
        self.default_content_weight = default_content_weight
        self.default_normalization = default_normalization
        self.default_fusion_strategy = default_fusion_strategy

    @classmethod
    def from_loaders(
        cls,
        als_loader: Optional[ALSModelLoader] = None,
        content_loader: Optional[ContentModelLoader] = None,
        default_als_weight: float = 0.5,
        default_content_weight: float = 0.5,
    ) -> "HybridRecommender":
        """
        Factory method to instantiate HybridRecommender using ALSModelLoader and ContentModelLoader.
        """
        als_predictor = ALSPredictor.from_loader(loader=als_loader)
        content_predictor = ContentPredictor.from_loader(
            loader=content_loader,
            item_to_index=als_predictor.item_to_index,
            index_to_item=als_predictor.index_to_item,
        )
        return cls(
            als_predictor=als_predictor,
            content_predictor=content_predictor,
            default_als_weight=default_als_weight,
            default_content_weight=default_content_weight,
        )

    def recommend(
        self,
        user_id: Any,
        user_history_item_ids: Optional[List[Any]] = None,
        top_n: int = 10,
        als_weight: Optional[float] = None,
        content_weight: Optional[float] = None,
        seen_item_ids: Optional[Set[Any]] = None,
        normalization: Optional[str] = None,
        fusion_strategy: Optional[str] = None,
    ) -> List[Tuple[Any, float]]:
        """
        Generates hybrid recommendations for a user.

        Args:
            user_id: User identifier.
            user_history_item_ids: Optional list of item IDs user interacted with.
            top_n: Number of recommendations to return.
            als_weight: Override weight for ALS scores.
            content_weight: Override weight for Content scores.
            seen_item_ids: Set of item IDs to filter out.
            normalization: 'minmax', 'zscore', or 'softmax'.
            fusion_strategy: 'weighted_sum', 'reciprocal_rank', or 'max'.

        Returns:
            List of (item_id, float_hybrid_score) ordered descending.
        """
        w_als = als_weight if als_weight is not None else self.default_als_weight
        w_content = content_weight if content_weight is not None else self.default_content_weight
        norm_method = normalization or self.default_normalization
        strategy = fusion_strategy or self.default_fusion_strategy

        # Combine seen items from explicit parameter and user history
        all_seen = set()
        if seen_item_ids:
            all_seen.update(seen_item_ids)
        if user_history_item_ids:
            all_seen.update(user_history_item_ids)

        # 1. Fetch ALS recommendations candidate pool
        candidate_k = max(top_n * 3, 50)
        als_recs = self.als_predictor.predict_for_user(
            user_id=user_id,
            top_n=candidate_k,
            seen_item_ids=all_seen,
        )

        # 2. Fetch Content recommendations candidate pool
        content_recs: List[Tuple[Any, float]] = []
        if user_history_item_ids:
            content_recs = self.content_predictor.recommend_for_user_history(
                interacted_item_ids=user_history_item_ids,
                top_n=candidate_k,
                seen_item_ids=all_seen,
            )
        elif als_recs:
            # Seed content model with top ALS item if no explicit user history provided
            top_seed_item = als_recs[0][0]
            content_recs = self.content_predictor.recommend_similar_items(
                item_id=top_seed_item,
                top_n=candidate_k,
            )

        # 3. Handle Fallbacks
        if als_recs and not content_recs:
            logger.info("Using pure ALS recommendations (Content candidate pool empty).")
            return als_recs[:top_n]

        if content_recs and not als_recs:
            logger.info("Using pure Content recommendations (ALS candidate pool empty / Cold user).")
            return content_recs[:top_n]

        if not als_recs and not content_recs:
            logger.warning(f"No recommendations could be generated for user {user_id}.")
            return []

        # 4. Normalize and Fuse
        als_norm = normalize_scores(als_recs, method=norm_method)
        content_norm = normalize_scores(content_recs, method=norm_method)

        hybrid_recs = fuse_and_rank(
            als_norm=als_norm,
            content_norm=content_norm,
            als_weight=w_als,
            content_weight=w_content,
            top_n=top_n,
            fusion_strategy=strategy,
        )

        return hybrid_recs

    def explain_recommendation(
        self,
        user_id: Any,
        item_id: Any,
        user_history_item_ids: Optional[List[Any]] = None,
        als_weight: Optional[float] = None,
        content_weight: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Provides a detailed breakdown explanation for why an item was recommended.

        Returns:
            Dict containing ALS score, Content score, component weights, and final score.
        """
        w_als = als_weight if als_weight is not None else self.default_als_weight
        w_content = content_weight if content_weight is not None else self.default_content_weight

        als_score = self.als_predictor.predict_score(user_id=user_id, item_id=item_id)

        content_sim = None
        if user_history_item_ids:
            # Pairwise max similarity against user history items
            sims = [
                self.content_predictor.compute_content_similarity(hist_item, item_id)
                for hist_item in user_history_item_ids
            ]
            valid_sims = [s for s in sims if s is not None]
            content_sim = max(valid_sims) if valid_sims else None

        return {
            "user_id": user_id,
            "item_id": item_id,
            "als_score": als_score,
            "content_similarity": content_sim,
            "als_weight": w_als,
            "content_weight": w_content,
            "item_features": self.content_predictor.get_item_features(item_id),
        }

    def predict(
        self,
        user_id: Any,
        user_history_item_ids: Optional[List[Any]] = None,
        top_n: int = 10,
        als_weight: Optional[float] = None,
        content_weight: Optional[float] = None,
        seen_items: Optional[Set[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates hybrid recommendations for a user returning structured dicts.

        Returns:
            List of dicts formatted as:
            [
                {
                    "item_id": int,
                    "score": float,
                    "source": "Hybrid"
                },
                ...
            ]
        """
        recs = self.recommend(
            user_id=user_id,
            user_history_item_ids=user_history_item_ids,
            top_n=top_n,
            als_weight=als_weight,
            content_weight=content_weight,
            seen_item_ids=seen_items,
        )
        return [
            {
                "item_id": int(item_id),
                "score": float(score),
                "source": "Hybrid"
            }
            for item_id, score in recs
        ]

