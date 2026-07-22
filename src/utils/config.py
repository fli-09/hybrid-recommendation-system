"""
Configuration loading and validation for the Hybrid Recommendation System.

Provides:
    - load_config(): Simple dict-based access to all configuration.
    - ConfigManager: Structured class with accessor methods for each component.
    - get_project_root(): Resolves the absolute path to the project root.

Usage:
    config = load_config()
    config["hybrid"]["default_als_weight"]
    config["als"]["latent_dim"]
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

import yaml

logger = logging.getLogger(__name__)

# ────────────────────────────── Required config keys ──────────────────────────────
REQUIRED_MODEL_KEYS: Dict[str, List[str]] = {
    "als": ["artifacts_dir", "user_factors_file", "item_factors_file"],
    "content": ["artifacts_dir", "vectorizer_file", "matrix_file", "similarity_file"],
    "hybrid": ["default_als_weight", "default_content_weight"],
}

REQUIRED_DATA_KEYS: List[str] = [
    "mappings_dir",
    "user_mapping_file",
    "item_mapping_file",
]


# ────────────────────────────── Path resolution ──────────────────────────────────

def get_project_root() -> str:
    """
    Returns the absolute path to the project root directory.
    Assumes this file lives at ``<project_root>/src/utils/config.py``.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, "..", ".."))


# ────────────────────────────── File loaders ─────────────────────────────────────

def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Loads and parses a YAML configuration file.

    Args:
        config_path: Relative (to project root) or absolute path.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: File does not exist.
        yaml.YAMLError: File cannot be parsed.
    """
    if not os.path.isabs(config_path):
        config_path = os.path.join(get_project_root(), config_path)

    if not os.path.exists(config_path):
        logger.error(f"YAML config not found: {config_path}")
        raise FileNotFoundError(f"YAML config not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
        logger.info(f"Loaded YAML config: {config_path}")
        return config or {}
    except yaml.YAMLError as exc:
        logger.error(f"Failed to parse YAML {config_path}: {exc}")
        raise


def load_json_config(config_path: str) -> Dict[str, Any]:
    """
    Loads and parses a JSON configuration file.

    Args:
        config_path: Relative (to project root) or absolute path.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: File does not exist.
        json.JSONDecodeError: File cannot be parsed.
    """
    if not os.path.isabs(config_path):
        config_path = os.path.join(get_project_root(), config_path)

    if not os.path.exists(config_path):
        logger.error(f"JSON config not found: {config_path}")
        raise FileNotFoundError(f"JSON config not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = json.load(fh)
        logger.info(f"Loaded JSON config: {config_path}")
        return config or {}
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse JSON {config_path}: {exc}")
        raise


# ────────────────────────────── Validation ───────────────────────────────────────

def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validates that required top-level sections and keys are present.

    Raises:
        ValueError: If any required key is missing.
    """
    missing: List[str] = []

    for section, keys in REQUIRED_MODEL_KEYS.items():
        if section not in config:
            missing.append(f"Section [{section}]")
            continue
        for key in keys:
            if key not in config[section]:
                missing.append(f"[{section}].{key}")

    data_section = config.get("data", {})
    for key in REQUIRED_DATA_KEYS:
        if key not in data_section:
            missing.append(f"[data].{key}")

    if missing:
        msg = "Configuration validation failed. Missing keys: " + ", ".join(missing)
        logger.error(msg)
        raise ValueError(msg)

    logger.info("Configuration validation passed.")


# ────────────────────────────── Public API ───────────────────────────────────────

def load_config(
    model_config_path: str = "configs/model_config.yaml",
    data_config_path: str = "configs/data_config.yaml",
    validate: bool = True,
) -> Dict[str, Any]:
    """
    Loads and merges model + data configuration into a single dictionary.

    Usage::

        config = load_config()
        config["hybrid"]["default_als_weight"]   # 0.5
        config["als"]["latent_dim"]               # 64
        config["data"]["mappings_dir"]            # "data/processed/mappings"

    Args:
        model_config_path: Path to the model YAML config file.
        data_config_path:  Path to the data YAML config file.
        validate: Whether to validate required keys after loading.

    Returns:
        Merged configuration dictionary.
    """
    model_cfg = load_yaml_config(model_config_path)
    data_cfg = load_yaml_config(data_config_path)

    # Merge data config under the top-level "data" key
    merged: Dict[str, Any] = {**model_cfg, **data_cfg}

    if validate:
        _validate_config(merged)

    return merged


# ────────────────────────────── ConfigManager class ──────────────────────────────

class ConfigManager:
    """
    Structured configuration accessor for the Hybrid Recommendation System.

    Provides typed getter methods for each configuration section and handles
    path resolution relative to the project root.

    Args:
        model_config_path: Relative or absolute path to model YAML file.
        data_config_path:  Relative or absolute path to data YAML file.
    """

    def __init__(
        self,
        model_config_path: str = "configs/model_config.yaml",
        data_config_path: str = "configs/data_config.yaml",
    ):
        self.root_dir: str = get_project_root()
        self.model_config_path: str = model_config_path
        self.data_config_path: str = data_config_path

        self.model_config: Dict[str, Any] = load_yaml_config(model_config_path)
        self.data_config: Dict[str, Any] = load_yaml_config(data_config_path)

        logger.info("ConfigManager initialized successfully.")

    # ── Section accessors ────────────────────────────────────────────────────

    def get_als_config(self) -> Dict[str, Any]:
        """Returns the ``als`` configuration section."""
        return self.model_config.get("als", {})

    def get_content_config(self) -> Dict[str, Any]:
        """Returns the ``content`` configuration section."""
        return self.model_config.get("content", {})

    def get_hybrid_config(self) -> Dict[str, Any]:
        """Returns the ``hybrid`` configuration section."""
        return self.model_config.get("hybrid", {})

    def get_inference_config(self) -> Dict[str, Any]:
        """Returns the ``inference`` configuration section."""
        return self.model_config.get("inference", {})

    def get_data_paths(self) -> Dict[str, Any]:
        """Returns the ``data`` paths configuration section."""
        return self.data_config.get("data", {})

    # ── Path resolution helpers ──────────────────────────────────────────────

    def resolve_path(self, relative_path: str) -> str:
        """Resolves a path relative to the project root into an absolute path."""
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self.root_dir, relative_path)
