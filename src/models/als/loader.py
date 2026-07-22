import os
import pickle
import logging
from typing import Dict, Tuple, Optional, Any
import numpy as np

from ...utils.config import ConfigManager, get_project_root

logger = logging.getLogger(__name__)


class ALSModelLoader:
    """
    Dedicated model loader for ALS Collaborative Filtering artifacts.
    Loads user/item latent factor arrays and user/item identifier mappings.
    """

    def __init__(
        self,
        artifacts_dir: Optional[str] = None,
        mappings_dir: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        self.config_manager = config_manager or ConfigManager()
        project_root = get_project_root()

        als_cfg = self.config_manager.get_als_config()
        data_cfg = self.config_manager.get_data_paths()

        rel_artifacts = artifacts_dir or als_cfg.get("artifacts_dir", "artifacts/models/als")
        rel_mappings = mappings_dir or data_cfg.get("mappings_dir", "data/processed/mappings")

        self.artifacts_dir = rel_artifacts if os.path.isabs(rel_artifacts) else os.path.join(project_root, rel_artifacts)
        self.mappings_dir = rel_mappings if os.path.isabs(rel_mappings) else os.path.join(project_root, rel_mappings)

        self.user_factors_file = als_cfg.get("user_factors_file", "user_factors.npy")
        self.item_factors_file = als_cfg.get("item_factors_file", "item_factors.npy")
        self.user_mapping_file = data_cfg.get("user_mapping_file", "user_mapping.pkl")
        self.item_mapping_file = data_cfg.get("item_mapping_file", "item_mapping.pkl")

    def load_embeddings(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Loads user_factors.npy and item_factors.npy.

        Returns:
            Tuple of (user_factors, item_factors) numpy arrays.
        """
        user_path = os.path.join(self.artifacts_dir, self.user_factors_file)
        item_path = os.path.join(self.artifacts_dir, self.item_factors_file)

        if not os.path.exists(user_path):
            raise FileNotFoundError(f"ALS User factors array missing at: {user_path}")
        if not os.path.exists(item_path):
            raise FileNotFoundError(f"ALS Item factors array missing at: {item_path}")

        logger.info(f"Loading ALS embeddings from {self.artifacts_dir}...")
        user_factors = np.load(user_path)
        item_factors = np.load(item_path)

        return user_factors, item_factors

    def load_mappings(self) -> Tuple[Dict[Any, int], Dict[int, Any], Dict[Any, int], Dict[int, Any]]:
        """
        Loads user and item mappings and constructs inverse index dictionaries.

        Returns:
            Tuple of (user_to_index, index_to_user, item_to_index, index_to_item).
        """
        user_map_path = os.path.join(self.mappings_dir, self.user_mapping_file)
        item_map_path = os.path.join(self.mappings_dir, self.item_mapping_file)

        if not os.path.exists(user_map_path):
            raise FileNotFoundError(f"User mapping pickle missing at: {user_map_path}")
        if not os.path.exists(item_map_path):
            raise FileNotFoundError(f"Item mapping pickle missing at: {item_map_path}")

        logger.info(f"Loading user & item mappings from {self.mappings_dir}...")
        with open(user_map_path, "rb") as f:
            user_to_index: Dict[Any, int] = pickle.load(f)

        with open(item_map_path, "rb") as f:
            item_to_index: Dict[Any, int] = pickle.load(f)

        # Build inverse mappings for O(1) index -> raw ID resolution
        index_to_user: Dict[int, Any] = {idx: uid for uid, idx in user_to_index.items()}
        index_to_item: Dict[int, Any] = {idx: iid for iid, idx in item_to_index.items()}

        return user_to_index, index_to_user, item_to_index, index_to_item

    def load_all(self) -> Dict[str, Any]:
        """
        Loads all ALS artifacts and mappings into a unified dictionary.
        """
        user_factors, item_factors = self.load_embeddings()
        u2idx, idx2u, i2idx, idx2i = self.load_mappings()

        return {
            "user_factors": user_factors,
            "item_factors": item_factors,
            "user_to_index": u2idx,
            "index_to_user": idx2u,
            "item_to_index": i2idx,
            "index_to_item": idx2i,
        }


def load_als_artifacts(
    artifacts_dir: Optional[str] = None,
    mappings_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience function to load all ALS model artifacts."""
    loader = ALSModelLoader(artifacts_dir=artifacts_dir, mappings_dir=mappings_dir)
    return loader.load_all()
