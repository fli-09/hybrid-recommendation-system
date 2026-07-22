import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.load_models import ModelRegistry
from src.models.content.predictor import ContentPredictor


@pytest.fixture(scope="module")
def content_predictor():
    registry = ModelRegistry()
    content_art = registry.get_content_artifacts()

    return ContentPredictor(
        tfidf_vectorizer=content_art.tfidf_vectorizer,
        tfidf_matrix=content_art.tfidf_matrix,
        similarity_model=content_art.similarity_model,
        product_profiles_df=content_art.product_profiles_df,
        item_to_index=content_art.item_to_index,
        index_to_item=content_art.index_to_item,
    )


def test_popular_item_recommendation(content_predictor):
    popular_item_id = 187946
    top_n = 5

    recs = content_predictor.recommend_similar_items(item_id=popular_item_id, top_n=top_n)

    assert isinstance(recs, list)
    assert len(recs) <= top_n
    assert len(recs) > 0

    for rec in recs:
        assert isinstance(rec, dict)
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert rec["source"] == "Content"
        assert isinstance(rec["item_id"], int)
        assert isinstance(rec["score"], float)

    print(f"\nPopular Item ({popular_item_id}) Top {top_n} Similar Recommendations:")
    for rec in recs:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_random_item_recommendation(content_predictor):
    random_item_id = 460188
    top_n = 5

    recs = content_predictor.recommend_similar_items(item_id=random_item_id, top_n=top_n)

    assert isinstance(recs, list)
    assert len(recs) <= top_n
    assert len(recs) > 0

    for rec in recs:
        assert isinstance(rec, dict)
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert rec["source"] == "Content"
        assert isinstance(rec["item_id"], int)
        assert isinstance(rec["score"], float)

    print(f"\nRandom Item ({random_item_id}) Top {top_n} Similar Recommendations:")
    for rec in recs:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_invalid_item_recommendation(content_predictor):
    invalid_item_id = -999999
    top_n = 5

    recs = content_predictor.recommend_similar_items(item_id=invalid_item_id, top_n=top_n)

    assert isinstance(recs, list)
    assert len(recs) == 0
    print(f"\nInvalid Item ({invalid_item_id}) Recommendations: {recs} (Clean fallback)")


def test_user_history_recommendation(content_predictor):
    history_ids = [187946, 460188]
    top_n = 5

    recs = content_predictor.recommend_for_user_history(history_item_ids=history_ids, top_n=top_n)

    assert isinstance(recs, list)
    assert len(recs) <= top_n
    assert len(recs) > 0

    for rec in recs:
        assert isinstance(rec, dict)
        assert rec["source"] == "Content"

    print(f"\nUser History ({history_ids}) Content Recommendations:")
    for rec in recs:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


def test_text_search_query(content_predictor):
    query = "shirt phone case"
    top_n = 5

    recs = content_predictor.search_text_query(query=query, top_n=top_n)

    assert isinstance(recs, list)
    assert len(recs) <= top_n

    for rec in recs:
        assert isinstance(rec, dict)
        assert rec["source"] == "Content"

    print(f"\nText Search Query ('{query}') Results:")
    for rec in recs:
        print(f"  Item ID: {rec['item_id']:8d} | Score: {rec['score']:.4f} | Source: {rec['source']}")


if __name__ == "__main__":
    registry = ModelRegistry()
    content_art = registry.get_content_artifacts()

    predictor = ContentPredictor(
        tfidf_vectorizer=content_art.tfidf_vectorizer,
        tfidf_matrix=content_art.tfidf_matrix,
        similarity_model=content_art.similarity_model,
        product_profiles_df=content_art.product_profiles_df,
        item_to_index=content_art.item_to_index,
        index_to_item=content_art.index_to_item,
    )

    test_popular_item_recommendation(predictor)
    test_random_item_recommendation(predictor)
    test_invalid_item_recommendation(predictor)
    test_user_history_recommendation(predictor)
    test_text_search_query(predictor)
