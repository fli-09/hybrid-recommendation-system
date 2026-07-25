import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["models_loaded"] is True


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hybrid Recommendation API running"}


def test_hybrid_recommend_endpoint():
    response = client.post(
        "/api/v1/recommend/hybrid",
        json={"user_id": 1, "top_n": 5}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["model_used"] == "HybridRecommender"
    assert len(json_data["recommendations"]) <= 5


def test_als_recommend_endpoint():
    response = client.post(
        "/api/v1/recommend/als",
        json={"user_id": 1, "top_n": 5}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["model_used"] == "ALSPredictor"


def test_content_recommend_endpoint():
    response = client.post(
        "/api/v1/recommend/content",
        json={"user_id": 1, "top_n": 5}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["model_used"] == "ContentPredictor"
