import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.load_models import get_model_registry, ModelRegistry
from src.models.hybrid.recommender import HybridRecommender


@pytest.fixture(scope="module")
def hybrid_recommender():
    return get_model_registry().hybrid_recommender


def test_existing_user_hybrid_recommendation(hybrid_recommender):
    visitorid = 1150086
    top_n = 5

    recs = hybrid_recommender.predict(user_id=visitorid, top_n=top_n)

    assert isinstance(recs, list)
    assert len(recs) <= top_n
    assert len(recs) > 0

    for rec in recs:
        assert isinstance(rec, dict)
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert rec["source"] == "Hybrid"
        assert isinstance(rec["item_id"], int)
        assert isinstance(rec["score"], float)

    print(f"\nExisting User ({visitorid}) Hybrid Recommendations:")
    for rec in recs:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_cold_start_user_fallback(hybrid_recommender):
    cold_user_id = -999999
    top_n = 5

    recs = hybrid_recommender.predict(user_id=cold_user_id, top_n=top_n)

    assert isinstance(recs, list)
    # Cold start with no history or fallback candidate pool returns []
    assert len(recs) == 0
    print(f"\nCold-Start User ({cold_user_id}) Recommendations: {recs} (Clean fallback)")


def test_explanation(hybrid_recommender):
    visitorid = 1150086
    item_id = 143866

    explanation = hybrid_recommender.explain_recommendation(user_id=visitorid, item_id=item_id)

    assert isinstance(explanation, dict)
    assert explanation["user_id"] == visitorid
    assert explanation["item_id"] == item_id
    assert "als_score" in explanation
    assert "als_weight" in explanation
    assert "content_weight" in explanation

    print(f"\nRecommendation Explanation for User {visitorid}, Item {item_id}:")
    print(f"  ALS Score: {explanation['als_score']}")
    print(f"  ALS Weight: {explanation['als_weight']}")
    print(f"  Content Weight: {explanation['content_weight']}")


if __name__ == "__main__":
    recommender = get_model_registry().hybrid_recommender

    test_existing_user_hybrid_recommendation(recommender)
    test_cold_start_user_fallback(recommender)
    test_explanation(recommender)
