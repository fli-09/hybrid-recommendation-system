import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.dataset_loader import DatasetLoader
from src.data.preprocessing import filter_interactions, assign_confidence_weights


def test_dataset_loader():
    loader = DatasetLoader()
    interactions = loader.load_interactions()
    assert isinstance(interactions, pd.DataFrame)
    assert not interactions.empty
    assert "visitorid" in interactions.columns
    assert "itemid" in interactions.columns


def test_preprocessing_filtering():
    df = pd.DataFrame({
        "visitorid": [1, 1, 1, 2, 3],
        "itemid": [10, 20, 30, 10, 40],
        "event": ["view", "view", "transaction", "view", "view"]
    })
    filtered = filter_interactions(df, min_user_interactions=2)
    assert len(filtered) == 3
    assert set(filtered["visitorid"].unique()) == {1}


def test_confidence_weighting():
    df = pd.DataFrame({"event": ["view", "addtocart", "transaction"]})
    weighted = assign_confidence_weights(df)
    assert weighted["confidence"].tolist() == [1.0, 3.0, 5.0]
