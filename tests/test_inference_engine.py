import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.recommend import InferenceEngine


@pytest.fixture(scope="module")
def engine():
    return InferenceEngine()


def test_active_user_recommendations(engine):
    active_user_id = 1150086
    top_n = 10

    recommendations = engine.recommend(user_id=active_user_id, top_n=top_n)

    assert isinstance(recommendations, list)
    assert len(recommendations) <= top_n
    assert len(recommendations) > 0

    for rec in recommendations:
        assert isinstance(rec, dict)
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert rec["source"] == "Hybrid"
        assert isinstance(rec["item_id"], int)
        assert isinstance(rec["score"], float)

    print(f"\nActive User ({active_user_id}) Top {top_n} Recommendations:")
    for rec in recommendations:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_unknown_user_cold_start_fallback(engine):
    unknown_user_id = -999999
    top_n = 10

    recommendations = engine.recommend(user_id=unknown_user_id, top_n=top_n)

    assert isinstance(recommendations, list)
    assert len(recommendations) == top_n  # Popular fallback must return top_n products
    assert len(recommendations) > 0       # Must NOT be empty!

    for rec in recommendations:
        assert isinstance(rec, dict)
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert rec["source"] == "Popular"
        assert isinstance(rec["item_id"], int)
        assert isinstance(rec["score"], float)

    print(f"\nUnknown User ({unknown_user_id}) Popular Fallback Top {top_n} Recommendations:")
    for rec in recommendations:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_output_schema_verification(engine):
    for user_id in [1150086, -999999]:
        recs = engine.recommend(user_id=user_id, top_n=5)
        assert len(recs) == 5
        for rec in recs:
            assert set(rec.keys()) == {"item_id", "score", "source"}
            assert isinstance(rec["item_id"], int)
            assert isinstance(rec["score"], float)
            assert isinstance(rec["source"], str)


if __name__ == "__main__":
    engine = InferenceEngine()

    test_active_user_recommendations(engine)
    test_unknown_user_cold_start_fallback(engine)
    test_output_schema_verification(engine)
