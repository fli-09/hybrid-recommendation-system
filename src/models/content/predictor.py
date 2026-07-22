import logging
from typing import Dict, List, Tuple, Optional, Any, Set, Union
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

logger = logging.getLogger(__name__)


class ContentPredictor:
    """
    Production predictor class for Content-Based Filtering using TF-IDF feature representations,
    Nearest Neighbors cosine similarity, user interaction history aggregation, and text query matching.
    """

    def __init__(
        self,
        tfidf_vectorizer: TfidfVectorizer,
        tfidf_matrix: csr_matrix,
        similarity_model: NearestNeighbors,
        product_profiles_df: Optional[pd.DataFrame] = None,
        item_to_index: Optional[Dict[Any, int]] = None,
        index_to_item: Optional[Dict[int, Any]] = None,
    ):
        """
        Instantiates ContentPredictor using already loaded Content artifacts.

        Args:
            tfidf_vectorizer: Fitted TfidfVectorizer instance.
            tfidf_matrix: Sparse TF-IDF feature matrix.
            similarity_model: Fitted NearestNeighbors estimator.
            product_profiles_df: Optional product metadata DataFrame.
            item_to_index: Dictionary mapping item ID to matrix row index.
            index_to_item: Dictionary mapping matrix row index to item ID.
        """
        self.tfidf_vectorizer = tfidf_vectorizer
        self.tfidf_matrix = tfidf_matrix
        self.similarity_model = similarity_model
        self.product_profiles_df = product_profiles_df

        self.item_to_index: Dict[Any, int] = item_to_index or {}
        self.index_to_item: Dict[int, Any] = index_to_item or {}

        if not self.item_to_index and product_profiles_df is not None and "itemid" in product_profiles_df.columns:
            for row_idx, item_id in enumerate(product_profiles_df["itemid"]):
                self.item_to_index[item_id] = row_idx
                self.index_to_item[row_idx] = item_id

        # Maintain content_item_to_index for backward compatibility
        self.content_item_to_index = self.item_to_index
        self.content_index_to_item = self.index_to_item

    @classmethod
    def from_loader(
        cls,
        loader: Optional[Any] = None,
        item_to_index: Optional[Dict[Any, int]] = None,
        index_to_item: Optional[Dict[int, Any]] = None,
    ) -> "ContentPredictor":
        """Factory method to instantiate ContentPredictor using loader object."""
        if loader is None:
            from .loader import ContentModelLoader
            loader = ContentModelLoader()

        vec, mat, sim, df = loader.load_all()
        return cls(
            tfidf_vectorizer=vec,
            tfidf_matrix=mat,
            similarity_model=sim,
            product_profiles_df=df,
            item_to_index=item_to_index,
            index_to_item=index_to_item,
        )

    def recommend_similar_items(
        self,
        item_id: Any,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Finds items most content-similar to a target seed item ID.

        Args:
            item_id: Target item identifier.
            top_n: Number of recommendations to return. Default is 10.

        Returns:
            List of dictionaries formatted as:
            [
                {
                    "item_id": int,
                    "score": float,
                    "source": "Content"
                },
                ...
            ]
        """
        if item_id not in self.item_to_index:
            logger.warning(f"Item ID {item_id} not found in content item mapping. Returning empty list.")
            return []

        item_idx = self.item_to_index[item_id]
        if item_idx >= self.tfidf_matrix.shape[0]:
            logger.warning(f"Item index {item_idx} out of bounds for TF-IDF matrix.")
            return []

        item_vec = self.tfidf_matrix[item_idx]

        # Handle items with zero/empty feature vectors
        if item_vec.nnz == 0:
            logger.warning(f"Item ID {item_id} has empty/zero TF-IDF feature vector.")
            return []

        n_fetch = min(top_n + 1, self.tfidf_matrix.shape[0])
        try:
            distances, indices = self.similarity_model.kneighbors(item_vec, n_neighbors=n_fetch)
            distances = distances[0]
            indices = indices[0]
        except Exception as e:
            logger.error(f"Error querying similarity_model kneighbors: {e}")
            sim_vector = np.asarray(self.tfidf_matrix @ item_vec.T).ravel()
            top_indices = np.argsort(-sim_vector)[:n_fetch]
            distances = 1.0 - sim_vector[top_indices]
            indices = top_indices

        results = []
        for dist, idx in zip(distances, indices):
            target_item_id = self.index_to_item.get(idx)
            if target_item_id is None or target_item_id == item_id:
                continue
            similarity = float(max(0.0, 1.0 - dist))
            results.append({
                "item_id": int(target_item_id),
                "score": similarity,
                "source": "Content"
            })
            if len(results) >= top_n:
                break

        return results

    def recommend_for_user_history(
        self,
        history_item_ids: List[Any],
        top_n: int = 10,
        seen_items: Optional[Union[Set[Any], List[Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates content recommendations based on user interaction history.

        Args:
            history_item_ids: List of item IDs interacted with by the user.
            top_n: Number of recommendations to return. Default is 10.
            seen_items: Optional set or list of item IDs to exclude.

        Returns:
            List of dictionaries formatted as:
            [
                {
                    "item_id": int,
                    "score": float,
                    "source": "Content"
                },
                ...
            ]
        """
        if not history_item_ids:
            return []

        valid_indices = [
            self.item_to_index[iid]
            for iid in history_item_ids
            if iid in self.item_to_index and self.item_to_index[iid] < self.tfidf_matrix.shape[0]
        ]

        if not valid_indices:
            logger.warning("No valid interacted items found in content matrix.")
            return []

        # Mean profile vector across user history
        user_profile_vec = self.tfidf_matrix[valid_indices].mean(axis=0)

        # Compute cosine similarity across all catalog products
        scores = np.asarray(self.tfidf_matrix @ user_profile_vec.T).ravel()

        exclude_set = set(history_item_ids)
        if seen_items:
            exclude_set.update(seen_items)

        for iid in exclude_set:
            if iid in self.item_to_index:
                idx = self.item_to_index[iid]
                if idx < len(scores):
                    scores[idx] = -np.inf

        num_items = len(scores)
        n = min(top_n, num_items)
        if n <= 0:
            return []

        top_indices = np.argpartition(scores, -n)[-n:]
        top_indices = top_indices[np.argsort(-scores[top_indices])]

        results = []
        for idx in top_indices:
            score = scores[idx]
            if np.isneginf(score):
                continue
            item_id = self.index_to_item.get(idx)
            if item_id is not None:
                results.append({
                    "item_id": int(item_id),
                    "score": float(max(0.0, score)),
                    "source": "Content"
                })

        return results

    def search_text_query(
        self,
        query: str,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Recommends products matching a raw text query using the TF-IDF vectorizer.

        Args:
            query: Raw text search string.
            top_n: Number of recommendations to return. Default is 10.

        Returns:
            List of dictionaries formatted as:
            [
                {
                    "item_id": int,
                    "score": float,
                    "source": "Content"
                },
                ...
            ]
        """
        if not query or not query.strip():
            return []

        query_vec = self.tfidf_vectorizer.transform([query])
        if query_vec.nnz == 0:
            logger.warning(f"Query '{query}' contains no vocabulary terms.")
            return []

        scores = (self.tfidf_matrix @ query_vec.T).toarray().ravel()

        num_items = len(scores)
        n = min(top_n, num_items)
        if n <= 0:
            return []

        top_indices = np.argpartition(scores, -n)[-n:]
        top_indices = top_indices[np.argsort(-scores[top_indices])]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0.0:
                continue
            item_id = self.index_to_item.get(idx)
            if item_id is not None:
                results.append({
                    "item_id": int(item_id),
                    "score": score,
                    "source": "Content"
                })

        return results

    def recommend_for_text_query(
        self,
        query_text: str,
        top_n: int = 10,
        seen_item_ids: Optional[Set[Any]] = None,
    ) -> List[Tuple[Any, float]]:
        """Backward compatible tuple-based method."""
        recs = self.search_text_query(query=query_text, top_n=top_n)
        return [(r["item_id"], r["score"]) for r in recs]

    def search_by_text(
        self,
        query: str,
        top_n: int = 10,
    ) -> List[Tuple[Any, float]]:
        """Backward compatible tuple-based method."""
        recs = self.search_text_query(query=query, top_n=top_n)
        return [(r["item_id"], r["score"]) for r in recs]

    def compute_content_similarity(self, item_id_a: Any, item_id_b: Any) -> Optional[float]:
        """Computes cosine similarity between two item TF-IDF feature vectors."""
        if item_id_a not in self.item_to_index or item_id_b not in self.item_to_index:
            return None

        idx_a = self.item_to_index[item_id_a]
        idx_b = self.item_to_index[item_id_b]

        if idx_a >= self.tfidf_matrix.shape[0] or idx_b >= self.tfidf_matrix.shape[0]:
            return None

        vec_a = self.tfidf_matrix[idx_a]
        vec_b = self.tfidf_matrix[idx_b]

        sim = float((vec_a @ vec_b.T).toarray()[0, 0])
        return max(0.0, sim)

    def get_item_features(self, item_id: Any) -> Optional[str]:
        """Retrieves raw text features string from product profiles for an item ID."""
        if self.product_profiles_df is None or "itemid" not in self.product_profiles_df.columns:
            return None

        if item_id not in self.item_to_index:
            return None

        idx = self.item_to_index[item_id]
        if idx < len(self.product_profiles_df) and "feature" in self.product_profiles_df.columns:
            return str(self.product_profiles_df.iloc[idx]["feature"])

        return None
