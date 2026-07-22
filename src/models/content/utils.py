from typing import Tuple, Optional
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from .loader import ContentModelLoader


def load_content_artifacts(
    artifacts_dir: Optional[str] = None
) -> Tuple[TfidfVectorizer, csr_matrix, NearestNeighbors, Optional[pd.DataFrame]]:
    """
    Loads pre-trained content model artifacts using ContentModelLoader.
    """
    loader = ContentModelLoader(artifacts_dir=artifacts_dir)
    return loader.load_all()
