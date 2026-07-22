import logging
from typing import Dict, List, Tuple, Optional, Any, Set, Union
import numpy as np

logger = logging.getLogger(__name__)


class ALSPredictor:
    """
    Production predictor class for Alternating Least Squares (ALS) Collaborative Filtering.
    Generates user recommendations and preference scores using pre-computed latent factor matrices.
    """

    def __init__(
        self,
        user_factors: np.ndarray,
        item_factors: np.ndarray,
        user_to_index: Dict[Any, int],
        index_to_user: Dict[int, Any],
        item_to_index: Dict[Any, int],
        index_to_item: Dict[int, Any],
    ):
        """
        Instantiates ALSPredictor using already loaded ALS artifacts and mappings.

        Args:
            user_factors: Pre-computed user factor matrix, shape (num_users, latent_dim).
            item_factors: Pre-computed item factor matrix, shape (num_items, latent_dim).
            user_to_index: Dictionary mapping user ID to factor matrix row index.
            index_to_user: Dictionary mapping factor matrix row index to user ID.
            item_to_index: Dictionary mapping item ID to factor matrix row index.
            index_to_item: Dictionary mapping factor matrix row index to item ID.
        """
        self.user_factors = user_factors
        self.item_factors = item_factors
        self.user_to_index = user_to_index
        self.index_to_user = index_to_user
        self.item_to_index = item_to_index
        self.index_to_item = index_to_item

        # Compute normalized item factor embeddings for cosine similarity lookups
        norms = np.linalg.norm(item_factors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        self.normalized_item_factors = item_factors / norms

    @classmethod
    def from_loader(cls, loader: Optional[Any] = None) -> "ALSPredictor":
        """
        Factory method to instantiate ALSPredictor using loader object.
        """
        if loader is None:
            from .loader import ALSModelLoader
            loader = ALSModelLoader()

        artifacts = loader.load_all()
        return cls(
            user_factors=artifacts["user_factors"],
            item_factors=artifacts["item_factors"],
            user_to_index=artifacts["user_to_index"],
            index_to_user=artifacts["index_to_user"],
            item_to_index=artifacts["item_to_index"],
            index_to_item=artifacts["index_to_item"],
        )

    def predict(
        self,
        user_id: Any,
        top_n: int = 10,
        seen_items: Optional[Union[Set[Any], List[Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates top-N recommendations for a user using dot product scoring (user_embedding @ item_embeddings.T).

        Args:
            user_id: User identifier.
            top_n: Number of recommendations to return. Default is 10.
            seen_items: Optional set or list of item IDs to filter out.

        Returns:
            List of dictionaries formatted as:
            [
                {
                    "item_id": int,
                    "score": float,
                    "source": "ALS"
                },
                ...
            ]
        """
        if user_id not in self.user_to_index:
            logger.warning(f"User ID {user_id} not found in ALS user mapping (Cold Start). Returning empty recommendations.")
            return []

        user_idx = self.user_to_index[user_id]
        user_vec = self.user_factors[user_idx]  # Shape: (latent_dim,)

        # Dot-product score: user_embedding @ item_embeddings.T
        scores = np.dot(self.item_factors, user_vec)  # Shape: (num_items,)

        # Mask previously seen / interacted items if provided
        if seen_items:
            for item_id in seen_items:
                if item_id in self.item_to_index:
                    item_idx = self.item_to_index[item_id]
                    if item_idx < len(scores):
                        scores[item_idx] = -np.inf

        num_items = len(scores)
        n = min(top_n, num_items)
        if n <= 0:
            return []

        # Find top N item indices efficiently using argpartition
        if n < num_items:
            top_indices = np.argpartition(scores, -n)[-n:]
            top_indices = top_indices[np.argsort(-scores[top_indices])]
        else:
            top_indices = np.argsort(-scores)

        recommendations = []
        for idx in top_indices:
            score = scores[idx]
            if np.isneginf(score):
                continue
            item_id = self.index_to_item.get(idx)
            if item_id is not None:
                recommendations.append({
                    "item_id": int(item_id),
                    "score": float(score),
                    "source": "ALS"
                })

        return recommendations

    def predict_for_user(
        self,
        user_id: Any,
        top_n: int = 10,
        seen_item_ids: Optional[Union[Set[Any], List[Any]]] = None,
    ) -> List[Tuple[Any, float]]:
        """
        Backward-compatible entrypoint returning List of (item_id, score) tuples.
        """
        recs = self.predict(user_id=user_id, top_n=top_n, seen_items=seen_item_ids)
        return [(r["item_id"], r["score"]) for r in recs]

    def predict_score(self, user_id: Any, item_id: Any) -> Optional[float]:
        """
        Estimates the preference score for a specific (user_id, item_id) pair.
        """
        if user_id not in self.user_to_index or item_id not in self.item_to_index:
            return None

        u_idx = self.user_to_index[user_id]
        i_idx = self.item_to_index[item_id]

        return float(np.dot(self.user_factors[u_idx], self.item_factors[i_idx]))

    def get_similar_items_by_embedding(
        self, item_id: Any, top_n: int = 10
    ) -> List[Tuple[Any, float]]:
        """
        Finds items with similar ALS latent feature representations.
        """
        if item_id not in self.item_to_index:
            logger.warning(f"Item ID {item_id} not found in ALS item mapping.")
            return []

        item_idx = self.item_to_index[item_id]
        target_vec = self.normalized_item_factors[item_idx]

        similarities = np.dot(self.normalized_item_factors, target_vec)
        similarities[item_idx] = -np.inf

        num_items = len(similarities)
        n = min(top_n, num_items)
        if n <= 0:
            return []

        top_indices = np.argpartition(similarities, -n)[-n:]
        top_indices = top_indices[np.argsort(-similarities[top_indices])]

        results = []
        for idx in top_indices:
            sim = similarities[idx]
            if np.isneginf(sim):
                continue
            similar_item_id = self.index_to_item.get(idx)
            if similar_item_id is not None:
                results.append((int(similar_item_id), float(sim)))

        return results
