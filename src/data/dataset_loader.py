import os
import logging
from typing import Optional
import pandas as pd

from ..utils.config import ConfigManager, get_project_root

logger = logging.getLogger(__name__)


class DatasetLoader:
    """
    Loads raw and processed datasets for the recommendation system.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self.project_root = get_project_root()
        self.data_paths = self.config_manager.get_data_paths()

    def _resolve_path(self, rel_path: str) -> str:
        if os.path.isabs(rel_path):
            return rel_path
        return os.path.join(self.project_root, rel_path)

    def load_interactions(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Loads the user-item interactions CSV.

        Returns:
            DataFrame with user-item interaction records.
        """
        path = self._resolve_path(
            filepath or self.data_paths.get("interactions_file", "data/processed/interactions/user_item_interactions.csv")
        )
        if not os.path.exists(path):
            raise FileNotFoundError(f"Interactions file not found at: {path}")

        logger.info(f"Loading interactions from {path}...")
        return pd.read_csv(path)

    def load_item_features(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Loads the cleaned item properties/features CSV.

        Returns:
            DataFrame with item feature records.
        """
        path = self._resolve_path(
            filepath or self.data_paths.get("features_file", "data/processed/features/item_properties_clean.csv")
        )
        if not os.path.exists(path):
            raise FileNotFoundError(f"Item features file not found at: {path}")

        logger.info(f"Loading item features from {path}...")
        return pd.read_csv(path)

    def load_raw_events(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """Loads raw events CSV from data/raw/."""
        path = self._resolve_path(filepath or "data/raw/events.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raw events file not found at: {path}")

        logger.info(f"Loading raw events from {path}...")
        return pd.read_csv(path)

    def load_category_tree(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """Loads raw category tree CSV from data/raw/."""
        path = self._resolve_path(filepath or "data/raw/category_tree.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Category tree file not found at: {path}")

        logger.info(f"Loading category tree from {path}...")
        return pd.read_csv(path)
