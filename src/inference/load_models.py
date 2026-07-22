"""
Model Registry — Centralized artifact loading and caching layer.

Provides:
    - ALSArtifacts:     Dataclass holding ALS user/item factor arrays.
    - ContentArtifacts: Dataclass holding TF-IDF matrix, vectorizer, similarity model.
    - MappingArtifacts: Dataclass holding user/item ID-to-index mappings.
    - ModelRegistry:    Singleton that loads, validates, and caches all artifacts.
    - get_model_registry(): Module-level accessor for the singleton instance.

Usage::

    registry = ModelRegistry()

    als      = registry.get_als_artifacts()
    content  = registry.get_content_artifacts()
    mappings = registry.get_mappings()

    als.user_factors.shape        # (1_407_580, 64)
    content.tfidf_matrix.shape    # (235_061, 50_000)
    mappings.item_to_index[67045] # 0
"""

import os
import json
import pickle
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from ..utils.config import ConfigManager, get_project_root, load_config

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Artifact dataclasses
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ALSArtifacts:
    """Container for ALS Collaborative Filtering artifacts."""

    user_factors: np.ndarray
    """User latent factor matrix, shape ``(n_users, latent_dim)``."""

    item_factors: np.ndarray
    """Item latent factor matrix, shape ``(n_items, latent_dim)``."""

    latent_dim: int = 0
    """Number of latent dimensions (auto-populated from factor shape)."""

    def __post_init__(self) -> None:
        self.latent_dim = self.user_factors.shape[1]

    def validate(self) -> None:
        """Checks internal consistency of factor arrays."""
        if self.user_factors.shape[1] != self.item_factors.shape[1]:
            raise ValueError(
                f"Latent dimension mismatch: user_factors has {self.user_factors.shape[1]} "
                f"but item_factors has {self.item_factors.shape[1]}"
            )
        logger.info(
            f"ALS artifacts validated: users={self.user_factors.shape[0]:,}, "
            f"items={self.item_factors.shape[0]:,}, dim={self.latent_dim}"
        )


@dataclass
class ContentArtifacts:
    """Container for Content-Based Filtering artifacts."""

    tfidf_vectorizer: TfidfVectorizer
    """Fitted TF-IDF vectorizer instance."""

    tfidf_matrix: csr_matrix
    """Sparse TF-IDF feature matrix, shape ``(n_items, vocab_size)``."""

    similarity_model: NearestNeighbors
    """Fitted NearestNeighbors cosine similarity model."""

    item_to_index: Dict[int, int]
    """Mapping from original item ID to content matrix row index."""

    index_to_item: Dict[int, int]
    """Mapping from content matrix row index to original item ID."""

    product_profiles_df: Optional[pd.DataFrame] = None
    """Optional product metadata DataFrame (itemid, feature)."""

    def validate(self) -> None:
        """Checks internal consistency of content artifacts."""
        n_rows = self.tfidf_matrix.shape[0]
        if n_rows != len(self.item_to_index):
            raise ValueError(
                f"TF-IDF matrix rows ({n_rows:,}) != item_to_index entries ({len(self.item_to_index):,})"
            )
        if n_rows != len(self.index_to_item):
            raise ValueError(
                f"TF-IDF matrix rows ({n_rows:,}) != index_to_item entries ({len(self.index_to_item):,})"
            )
        logger.info(
            f"Content artifacts validated: items={n_rows:,}, "
            f"vocab={self.tfidf_matrix.shape[1]:,}"
        )


@dataclass
class MappingArtifacts:
    """Container for user/item identifier mappings."""

    user_to_index: Dict[Any, int]
    """Mapping from raw user ID → contiguous integer index."""

    index_to_user: Dict[int, Any]
    """Mapping from contiguous index → raw user ID."""

    item_to_index: Dict[Any, int]
    """Mapping from raw item ID → contiguous integer index."""

    index_to_item: Dict[int, Any]
    """Mapping from contiguous index → raw item ID."""

    def validate(self, n_users: Optional[int] = None, n_items: Optional[int] = None) -> None:
        """
        Checks internal consistency and optional alignment with factor dimensions.

        Args:
            n_users: Expected number of users (e.g. from ``user_factors.shape[0]``).
            n_items: Expected number of items (e.g. from ``item_factors.shape[0]``).
        """
        if len(self.user_to_index) != len(self.index_to_user):
            raise ValueError("user_to_index and index_to_user have different lengths")
        if len(self.item_to_index) != len(self.index_to_item):
            raise ValueError("item_to_index and index_to_item have different lengths")

        if n_users is not None and len(self.user_to_index) != n_users:
            raise ValueError(
                f"user_to_index ({len(self.user_to_index):,}) != expected users ({n_users:,})"
            )
        if n_items is not None and len(self.item_to_index) != n_items:
            raise ValueError(
                f"item_to_index ({len(self.item_to_index):,}) != expected items ({n_items:,})"
            )

        logger.info(
            f"Mapping artifacts validated: users={len(self.user_to_index):,}, "
            f"items={len(self.item_to_index):,}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Model Registry
# ═══════════════════════════════════════════════════════════════════════════════

class ModelRegistry:
    """
    Centralized loading and caching layer for all ML artifacts.

    Loads each artifact group (ALS, Content, Mappings) exactly once on first
    access and caches the result for subsequent calls.  No recommendation logic
    lives here — only raw artifact I/O and validation.

    Usage::

        registry = ModelRegistry()

        als      = registry.get_als_artifacts()       # ALSArtifacts
        content  = registry.get_content_artifacts()    # ContentArtifacts
        mappings = registry.get_mappings()             # MappingArtifacts
    """

    _instance: Optional["ModelRegistry"] = None

    def __init__(
        self,
        base_dir: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        self._base_dir: str = base_dir or get_project_root()
        self._config: ConfigManager = config_manager or ConfigManager()

        # Cached artifact containers (populated on first access)
        self._als_artifacts: Optional[ALSArtifacts] = None
        self._content_artifacts: Optional[ContentArtifacts] = None
        self._mapping_artifacts: Optional[MappingArtifacts] = None

        # Backward-compatible predictor slots (populated by load_all)
        self.als_predictor: Optional[Any] = None
        self.content_predictor: Optional[Any] = None
        self.hybrid_recommender: Optional[Any] = None
        self.weights_config: Dict[str, float] = {"als_weight": 0.5, "content_weight": 0.5}

        self._is_loaded: bool = False

    # ── Path helpers ─────────────────────────────────────────────────────────

    def _resolve(self, rel_path: str) -> str:
        """Resolves a relative path against the project root."""
        if os.path.isabs(rel_path):
            return rel_path
        return os.path.join(self._base_dir, rel_path)

    # ── ALS artifacts ────────────────────────────────────────────────────────

    def get_als_artifacts(self, force_reload: bool = False) -> ALSArtifacts:
        """
        Returns cached ALS artifacts.  Loads from disk on first call.

        Returns:
            ALSArtifacts dataclass containing user_factors and item_factors.

        Raises:
            FileNotFoundError: If ``.npy`` files are missing.
        """
        if self._als_artifacts is not None and not force_reload:
            return self._als_artifacts

        als_cfg = self._config.get_als_config()
        artifacts_dir = self._resolve(als_cfg.get("artifacts_dir", "artifacts/models/als"))

        user_path = os.path.join(artifacts_dir, als_cfg.get("user_factors_file", "user_factors.npy"))
        item_path = os.path.join(artifacts_dir, als_cfg.get("item_factors_file", "item_factors.npy"))

        if not os.path.exists(user_path):
            raise FileNotFoundError(f"ALS user_factors not found: {user_path}")
        if not os.path.exists(item_path):
            raise FileNotFoundError(f"ALS item_factors not found: {item_path}")

        logger.info(f"Loading ALS user factors from {user_path}")
        user_factors = np.load(user_path)
        logger.info(f"Loading ALS item factors from {item_path}")
        item_factors = np.load(item_path)

        self._als_artifacts = ALSArtifacts(
            user_factors=user_factors,
            item_factors=item_factors,
        )
        self._als_artifacts.validate()
        return self._als_artifacts

    # ── Mapping artifacts ────────────────────────────────────────────────────

    def get_mappings(self, force_reload: bool = False) -> MappingArtifacts:
        """
        Returns cached mapping artifacts.  Loads from disk on first call.

        Returns:
            MappingArtifacts dataclass with user/item forward and inverse maps.

        Raises:
            FileNotFoundError: If ``.pkl`` mapping files are missing.
        """
        if self._mapping_artifacts is not None and not force_reload:
            return self._mapping_artifacts

        data_cfg = self._config.get_data_paths()
        mappings_dir = self._resolve(data_cfg.get("mappings_dir", "data/processed/mappings"))

        user_map_file = data_cfg.get("user_mapping_file", "user_mapping.pkl")
        item_map_file = data_cfg.get("item_mapping_file", "item_mapping.pkl")

        user_map_path = os.path.join(mappings_dir, user_map_file)
        item_map_path = os.path.join(mappings_dir, item_map_file)

        if not os.path.exists(user_map_path):
            raise FileNotFoundError(f"User mapping not found: {user_map_path}")
        if not os.path.exists(item_map_path):
            raise FileNotFoundError(f"Item mapping not found: {item_map_path}")

        logger.info(f"Loading user mapping from {user_map_path}")
        with open(user_map_path, "rb") as fh:
            user_to_index: Dict[Any, int] = pickle.load(fh)

        logger.info(f"Loading item mapping from {item_map_path}")
        with open(item_map_path, "rb") as fh:
            item_to_index: Dict[Any, int] = pickle.load(fh)

        index_to_user = {idx: uid for uid, idx in user_to_index.items()}
        index_to_item = {idx: iid for iid, idx in item_to_index.items()}

        self._mapping_artifacts = MappingArtifacts(
            user_to_index=user_to_index,
            index_to_user=index_to_user,
            item_to_index=item_to_index,
            index_to_item=index_to_item,
        )
        self._mapping_artifacts.validate()
        return self._mapping_artifacts

    # ── Content artifacts ────────────────────────────────────────────────────

    def get_content_artifacts(self, force_reload: bool = False) -> ContentArtifacts:
        """
        Returns cached content-based filtering artifacts.  Loads from disk on first call.

        Returns:
            ContentArtifacts dataclass with TF-IDF matrix, vectorizer,
            similarity model, and item index mappings.

        Raises:
            FileNotFoundError: If required ``.pkl`` files are missing.
        """
        if self._content_artifacts is not None and not force_reload:
            return self._content_artifacts

        content_cfg = self._config.get_content_config()
        artifacts_dir = self._resolve(content_cfg.get("artifacts_dir", "artifacts/models/content"))
        mappings_dir = self._resolve(
            self._config.get_data_paths().get("mappings_dir", "data/processed/mappings")
        )

        # File paths
        vec_path = os.path.join(artifacts_dir, content_cfg.get("vectorizer_file", "tfidf_vectorizer.pkl"))
        mat_path = os.path.join(artifacts_dir, content_cfg.get("matrix_file", "tfidf_matrix.pkl"))
        sim_path = os.path.join(artifacts_dir, content_cfg.get("similarity_file", "similarity_model.pkl"))
        profiles_path = os.path.join(artifacts_dir, content_cfg.get("profiles_file", "product_profiles.csv"))

        i2idx_path = os.path.join(mappings_dir, "item_to_index.pkl")
        idx2i_path = os.path.join(mappings_dir, "index_to_item.pkl")

        # Validate existence
        for label, path in [
            ("TF-IDF vectorizer", vec_path),
            ("TF-IDF matrix", mat_path),
            ("Similarity model", sim_path),
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{label} not found: {path}")

        # Load pickle artifacts
        logger.info(f"Loading TF-IDF vectorizer from {vec_path}")
        with open(vec_path, "rb") as fh:
            tfidf_vectorizer: TfidfVectorizer = pickle.load(fh)

        logger.info(f"Loading TF-IDF matrix from {mat_path}")
        with open(mat_path, "rb") as fh:
            tfidf_matrix: csr_matrix = pickle.load(fh)

        logger.info(f"Loading similarity model from {sim_path}")
        with open(sim_path, "rb") as fh:
            similarity_model: NearestNeighbors = pickle.load(fh)

        # Item-to-index / index-to-item mappings
        if os.path.exists(i2idx_path) and os.path.exists(idx2i_path):
            logger.info(f"Loading item_to_index from {i2idx_path}")
            with open(i2idx_path, "rb") as fh:
                item_to_index: Dict[int, int] = pickle.load(fh)
            logger.info(f"Loading index_to_item from {idx2i_path}")
            with open(idx2i_path, "rb") as fh:
                index_to_item: Dict[int, int] = pickle.load(fh)
        else:
            # Fall back to deriving from item_mapping.pkl
            logger.warning("Standalone item_to_index/index_to_item not found; deriving from item_mapping.")
            mappings = self.get_mappings()
            item_to_index = mappings.item_to_index
            index_to_item = mappings.index_to_item

        # Optional product profiles
        product_profiles_df: Optional[pd.DataFrame] = None
        if os.path.exists(profiles_path):
            logger.info(f"Loading product profiles from {profiles_path}")
            product_profiles_df = pd.read_csv(profiles_path)

        self._content_artifacts = ContentArtifacts(
            tfidf_vectorizer=tfidf_vectorizer,
            tfidf_matrix=tfidf_matrix,
            similarity_model=similarity_model,
            item_to_index=item_to_index,
            index_to_item=index_to_item,
            product_profiles_df=product_profiles_df,
        )
        self._content_artifacts.validate()
        return self._content_artifacts

    # ── Full loading (backward compatible) ───────────────────────────────────

    def load_all(self, force_reload: bool = False) -> None:
        """
        Loads all artifact groups and instantiates predictor / recommender objects.

        This method exists for backward compatibility with ``InferenceEngine``
        and ``recommend.py``.  New code should prefer the individual
        ``get_*`` accessor methods.
        """
        if self._is_loaded and not force_reload:
            logger.info("ModelRegistry already loaded — skipping.")
            return

        logger.info("ModelRegistry: Loading all artifacts...")

        # Import here to avoid circular imports at module level
        from ..models.als import ALSPredictor, ALSModelLoader
        from ..models.content import ContentPredictor, ContentModelLoader
        from ..models.hybrid import HybridRecommender

        # 1. Load raw artifacts via the clean API
        als = self.get_als_artifacts(force_reload=force_reload)
        mappings = self.get_mappings(force_reload=force_reload)
        content = self.get_content_artifacts(force_reload=force_reload)

        # 2. Cross-validate dimensions
        mappings.validate(
            n_users=als.user_factors.shape[0],
            n_items=als.item_factors.shape[0],
        )

        # 3. Instantiate predictors from raw artifacts
        self.als_predictor = ALSPredictor(
            user_factors=als.user_factors,
            item_factors=als.item_factors,
            user_to_index=mappings.user_to_index,
            index_to_user=mappings.index_to_user,
            item_to_index=mappings.item_to_index,
            index_to_item=mappings.index_to_item,
        )

        self.content_predictor = ContentPredictor(
            tfidf_vectorizer=content.tfidf_vectorizer,
            tfidf_matrix=content.tfidf_matrix,
            similarity_model=content.similarity_model,
            product_profiles_df=content.product_profiles_df,
            item_to_index=content.item_to_index,
            index_to_item=content.index_to_item,
        )

        # 4. Load hybrid weights
        hybrid_cfg = self._config.get_hybrid_config()
        weights_file = hybrid_cfg.get("weights_file", "artifacts/models/hybrid/hybrid_weights.json")
        weights_path = self._resolve(weights_file)

        if os.path.exists(weights_path):
            try:
                with open(weights_path, "r", encoding="utf-8") as fh:
                    w = json.load(fh)
                self.weights_config["als_weight"] = float(w.get("als_weight", 0.5))
                self.weights_config["content_weight"] = float(w.get("content_weight", 0.5))
                logger.info(f"Loaded hybrid weights: {self.weights_config}")
            except Exception as exc:
                logger.warning(f"Could not parse hybrid weights, using defaults: {exc}")

        # 5. Instantiate hybrid recommender
        self.hybrid_recommender = HybridRecommender(
            als_predictor=self.als_predictor,
            content_predictor=self.content_predictor,
            default_als_weight=self.weights_config["als_weight"],
            default_content_weight=self.weights_config["content_weight"],
        )

        self._is_loaded = True
        logger.info("ModelRegistry: All artifacts loaded and predictors initialized.")

    def is_loaded(self) -> bool:
        """Returns True if ``load_all()`` has completed successfully."""
        return self._is_loaded


# ═══════════════════════════════════════════════════════════════════════════════
# Module-level singleton accessor
# ═══════════════════════════════════════════════════════════════════════════════

_global_registry: Optional[ModelRegistry] = None


def get_model_registry(base_dir: Optional[str] = None) -> ModelRegistry:
    """
    Returns the global singleton ``ModelRegistry`` instance.

    On first call the registry is created and ``load_all()`` is executed to
    populate predictor objects for backward compatibility.
    """
    global _global_registry
    if _global_registry is None:
        logger.info("Instantiating global ModelRegistry singleton...")
        _global_registry = ModelRegistry(base_dir=base_dir)
        _global_registry.load_all()
    return _global_registry
