import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.load_models import ModelRegistry
from src.models.als.predictor import ALSPredictor


@pytest.fixture(scope="module")
def als_predictor():
    registry = ModelRegistry()
    als_art = registry.get_als_artifacts()
    mappings = registry.get_mappings()

    return ALSPredictor(
        user_factors=als_art.user_factors,
        item_factors=als_art.item_factors,
        user_to_index=mappings.user_to_index,
        index_to_user=mappings.index_to_user,
        item_to_index=mappings.item_to_index,
        index_to_item=mappings.index_to_item,
    )


def test_existing_active_user(als_predictor):
    visitorid = 1150086
    top_n = 10

    recommendations = als_predictor.predict(user_id=visitorid, top_n=top_n)

    assert isinstance(recommendations, list)
    assert len(recommendations) <= top_n
    assert len(recommendations) > 0

    for rec in recommendations:
        assert isinstance(rec, dict)
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert rec["source"] == "ALS"
        assert isinstance(rec["item_id"], int)
        assert isinstance(rec["score"], float)

    print(f"\nActive User ({visitorid}) Top {top_n} Recommendations:")
    for rec in recommendations:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_unknown_user(als_predictor):
    unknown_visitorid = -999999
    top_n = 10

    recommendations = als_predictor.predict(user_id=unknown_visitorid, top_n=top_n)

    assert isinstance(recommendations, list)
    assert len(recommendations) == 0
    print(f"\nUnknown User ({unknown_visitorid}) Recommendations: {recommendations} (Clean fallback)")


def test_seen_items_filtering(als_predictor):
    visitorid = 1150086
    initial_recs = als_predictor.predict(user_id=visitorid, top_n=5)
    seen_item_ids = {r["item_id"] for r in initial_recs}

    filtered_recs = als_predictor.predict(user_id=visitorid, top_n=5, seen_items=seen_item_ids)

    filtered_item_ids = {r["item_id"] for r in filtered_recs}
    assert len(seen_item_ids.intersection(filtered_item_ids)) == 0


if __name__ == "__main__":
    registry = ModelRegistry()
    als_art = registry.get_als_artifacts()
    mappings = registry.get_mappings()

    predictor = ALSPredictor(
        user_factors=als_art.user_factors,
        item_factors=als_art.item_factors,
        user_to_index=mappings.user_to_index,
        index_to_user=mappings.index_to_user,
        item_to_index=mappings.item_to_index,
        index_to_item=mappings.index_to_item,
    )

    test_existing_active_user(predictor)
    test_unknown_user(predictor)
    test_seen_items_filtering(predictor)
