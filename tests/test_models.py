import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.recommend import InferenceEngine


@pytest.fixture(scope="module")
def engine():
    return InferenceEngine()


def test_als_recommendation(engine):
    recs = engine.recommend_als(user_id=1, top_n=5)
    assert isinstance(recs, list)
    assert len(recs) <= 5
    for item_id, score in recs:
        assert isinstance(item_id, (int, str, np.integer))
        assert isinstance(score, (float, np.floating))


def test_content_user_recommendation(engine):
    recs = engine.recommend_content_user(user_id=1, top_n=5)
    assert isinstance(recs, list)
    assert len(recs) <= 5
    for item_id, score in recs:
        assert isinstance(item_id, (int, str, np.integer))
        assert isinstance(score, (float, np.floating))


def test_hybrid_recommendation(engine):
    recs = engine.recommend_hybrid(user_id=1, top_n=5)
    assert isinstance(recs, list)
    assert len(recs) <= 5
    for item_id, score in recs:
        assert isinstance(item_id, (int, str, np.integer))
        assert isinstance(score, (float, np.floating))


def test_cold_start_fallback(engine):
    # Non-existent user ID should invoke cold-start handling cleanly
    recs = engine.recommend_hybrid(user_id=-999999, top_n=5)
    assert isinstance(recs, list)
    assert len(recs) <= 5

