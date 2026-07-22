from typing import Dict, Tuple, Any, Optional
import numpy as np
from .loader import ALSModelLoader


def load_als_embeddings(
    artifacts_dir: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Loads user and item factor matrices using ALSModelLoader.
    """
    loader = ALSModelLoader(artifacts_dir=artifacts_dir)
    return loader.load_embeddings()


def load_mappings(
    mappings_dir: Optional[str] = None
) -> Tuple[Dict[Any, int], Dict[int, Any], Dict[Any, int], Dict[int, Any]]:
    """
    Loads user and item mappings using ALSModelLoader.
    """
    loader = ALSModelLoader(mappings_dir=mappings_dir)
    return loader.load_mappings()
