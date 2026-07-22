import os
import pickle
import logging
from typing import Tuple, Optional, Dict, Any
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from ...utils.config import ConfigManager, get_project_root

logger = logging.getLogger(__name__)


class ContentModelLoader:
    """
    Dedicated model loader for Content-Based Filtering artifacts.
    Loads TF-IDF vectorizer, sparse matrix, similarity model, and product profiles.
    """

    def __init__(
        self,
        artifacts_dir: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        self.config_manager = config_manager or ConfigManager()
        project_root = get_project_root()

        content_cfg = self.config_manager.get_content_config()
        rel_artifacts = artifacts_dir or content_cfg.get("artifacts_dir", "artifacts/models/content")

        self.artifacts_dir = rel_artifacts if os.path.isabs(rel_artifacts) else os.path.join(project_root, rel_artifacts)

        self.vectorizer_file = content_cfg.get("vectorizer_file", "tfidf_vectorizer.pkl")
        self.matrix_file = content_cfg.get("matrix_file", "tfidf_matrix.pkl")
        self.similarity_file = content_cfg.get("similarity_file", "similarity_model.pkl")
        self.profiles_file = content_cfg.get("profiles_file", "product_profiles.csv")

    def load_vectorizer(self) -> TfidfVectorizer:
        """Loads fitted TfidfVectorizer from pickle file."""
        vec_path = os.path.join(self.artifacts_dir, self.vectorizer_file)
        if not os.path.exists(vec_path):
            raise FileNotFoundError(f"TF-IDF vectorizer missing at: {vec_path}")

        logger.info(f"Loading TF-IDF vectorizer from {vec_path}...")
        with open(vec_path, "rb") as f:
            return pickle.load(f)

    def load_tfidf_matrix(self) -> csr_matrix:
        """Loads CSR sparse TF-IDF matrix from pickle file."""
        mat_path = os.path.join(self.artifacts_dir, self.matrix_file)
        if not os.path.exists(mat_path):
            raise FileNotFoundError(f"TF-IDF matrix missing at: {mat_path}")

        logger.info(f"Loading TF-IDF sparse matrix from {mat_path}...")
        with open(mat_path, "rb") as f:
            return pickle.load(f)

    def load_similarity_model(self) -> NearestNeighbors:
        """Loads NearestNeighbors similarity estimator from pickle file."""
        sim_path = os.path.join(self.artifacts_dir, self.similarity_file)
        if not os.path.exists(sim_path):
            raise FileNotFoundError(f"Similarity model missing at: {sim_path}")

        logger.info(f"Loading similarity model from {sim_path}...")
        with open(sim_path, "rb") as f:
            return pickle.load(f)

    def load_product_profiles(self) -> Optional[pd.DataFrame]:
        """Loads product profiles metadata CSV if present."""
        profiles_path = os.path.join(self.artifacts_dir, self.profiles_file)
        if not os.path.exists(profiles_path):
            logger.warning(f"Product profiles CSV not found at: {profiles_path}")
            return None

        logger.info(f"Loading product profiles CSV from {profiles_path}...")
        try:
            return pd.read_csv(profiles_path)
        except Exception as e:
            logger.error(f"Failed to parse product profiles CSV: {e}")
            return None

    def load_all(self) -> Tuple[TfidfVectorizer, csr_matrix, NearestNeighbors, Optional[pd.DataFrame]]:
        """
        Loads all Content model artifacts.

        Returns:
            Tuple of (tfidf_vectorizer, tfidf_matrix, similarity_model, product_profiles_df)
        """
        vectorizer = self.load_vectorizer()
        tfidf_matrix = self.load_tfidf_matrix()
        similarity_model = self.load_similarity_model()
        product_profiles_df = self.load_product_profiles()

        return vectorizer, tfidf_matrix, similarity_model, product_profiles_df


def load_content_artifacts(
    artifacts_dir: Optional[str] = None
) -> Tuple[TfidfVectorizer, csr_matrix, NearestNeighbors, Optional[pd.DataFrame]]:
    """Convenience function to load all Content filtering artifacts."""
    loader = ContentModelLoader(artifacts_dir=artifacts_dir)
    return loader.load_all()
