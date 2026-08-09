import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.app import app

client = TestClient(app)


def test_existing_user_recommendation_endpoint():
    user_id = 1150086
    top_n = 5
    response = client.get(f"/api/v1/recommend/{user_id}?top_n={top_n}")

    assert response.status_code == 200
    json_data = response.json()

    assert "user_id" in json_data
    assert "recommendations" in json_data
    assert json_data["user_id"] == user_id
    assert len(json_data["recommendations"]) == top_n

    for item in json_data["recommendations"]:
        assert "item_id" in item
        assert "score" in item
        assert "source" in item
        assert item["source"] == "Hybrid"
        assert isinstance(item["item_id"], int)
        assert isinstance(item["score"], float)

    print(f"\nAPI GET /recommend/{user_id}?top_n={top_n} Response:")
    print(json_data)


def test_unknown_user_recommendation_endpoint():
    unknown_user_id = -999999
    top_n = 5
    response = client.get(f"/api/v1/recommend/{unknown_user_id}?top_n={top_n}")

    assert response.status_code == 200
    json_data = response.json()

    assert "user_id" in json_data
    assert "recommendations" in json_data
    assert json_data["user_id"] == unknown_user_id
    assert len(json_data["recommendations"]) == top_n

    for item in json_data["recommendations"]:
        assert "item_id" in item
        assert "score" in item
        assert "source" in item
        assert item["source"] == "Popular"
        assert isinstance(item["item_id"], int)
        assert isinstance(item["score"], float)

    print(f"\nAPI GET /recommend/{unknown_user_id}?top_n={top_n} Response:")
    print(json_data)


def test_response_schema_validation():
    user_id = 1150086
    response = client.get(f"/api/v1/recommend/{user_id}")

    assert response.status_code == 200
    json_data = response.json()

    assert isinstance(json_data["user_id"], int)
    assert isinstance(json_data["recommendations"], list)
    assert len(json_data["recommendations"]) == 10  # Default top_n = 10

    for rec in json_data["recommendations"]:
        assert "item_id" in rec
        assert "score" in rec
        assert "source" in rec
        assert "product_name" in rec
        assert "category" in rec
        assert "brand" in rec
        assert "price" in rec
        assert "image_url" in rec
        assert "description" in rec


if __name__ == "__main__":
    test_existing_user_recommendation_endpoint()
    test_unknown_user_recommendation_endpoint()
    test_response_schema_validation()
