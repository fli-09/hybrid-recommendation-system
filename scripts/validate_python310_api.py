"""Run end-to-end API validation in a Python 3.10 environment.

Usage:
    python scripts/validate_python310_api.py

The script starts Uvicorn locally, validates API imports and route registration,
then exercises every public recommendation endpoint over HTTP.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8000"


def request(path, method="GET", payload=None, timeout=300):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    http_request = Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    with urlopen(http_request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def wait_for_server():
    for _ in range(30):
        try:
            status, response = request("/", timeout=5)
            if status == 200:
                return response
        except URLError:
            time.sleep(2)
    raise RuntimeError("Uvicorn did not become ready within 60 seconds.")


def assert_recommendations(payload, expected_user_id=None, expected_source=None):
    if expected_user_id is not None:
        assert payload["user_id"] == expected_user_id
    assert isinstance(payload["recommendations"], list)
    assert payload["recommendations"], "Expected at least one recommendation."
    for recommendation in payload["recommendations"]:
        assert {"item_id", "score", "source"}.issubset(recommendation)
        if expected_source is not None:
            assert recommendation["source"] == expected_source


def validate_imports_and_routes():
    from api.app import app
    from api.schemas import HealthCheckResponse, RecommendationItem, UserRecommendationResponse

    paths = {route.path for route in app.routes}
    expected_paths = {
        "/",
        "/api/v1/health",
        "/api/v1/recommend/{user_id}",
        "/api/v1/recommend/hybrid",
        "/api/v1/recommend/als",
        "/api/v1/recommend/content",
        "/api/v1/recommend/search",
    }
    assert expected_paths.issubset(paths), f"Missing routes: {expected_paths - paths}"
    assert HealthCheckResponse.__fields__["status"].default == "healthy"
    assert set(RecommendationItem.__fields__) == {"item_id", "score", "source"}
    assert {"user_id", "recommendations"}.issubset(UserRecommendationResponse.__fields__)


def validate_endpoints():
    status, root = request("/")
    assert status == 200
    assert root == {"message": "Hybrid Recommendation API running"}

    # Health invokes the inference dependency and verifies model-registry initialization.
    status, health = request("/api/v1/health")
    assert status == 200
    assert health == {"status": "healthy", "models_loaded": True}

    status, known_user = request("/api/v1/recommend/1150086?top_n=3")
    assert status == 200
    assert_recommendations(known_user, expected_user_id=1150086, expected_source="Hybrid")

    status, cold_start = request("/api/v1/recommend/-999999?top_n=3")
    assert status == 200
    assert_recommendations(cold_start, expected_user_id=-999999, expected_source="Popular")

    requests_to_validate = [
        ("/api/v1/recommend/hybrid", {"user_id": 1150086, "top_n": 3}, "HybridRecommender"),
        ("/api/v1/recommend/als", {"user_id": 1150086, "top_n": 3}, "ALSPredictor"),
        ("/api/v1/recommend/content", {"user_id": 1150086, "top_n": 3}, "ContentPredictor"),
        ("/api/v1/recommend/search", {"query": "product", "top_n": 3}, "ContentTextSearch"),
    ]
    for path, payload, model_name in requests_to_validate:
        status, response = request(path, method="POST", payload=payload)
        assert status == 200
        assert response["model_used"] == model_name
        assert isinstance(response["recommendations"], list)


def main():
    if sys.version_info[:2] != (3, 10):
        raise RuntimeError(
            f"Python 3.10 is required for this validation; found {sys.version.split()[0]}."
        )

    validate_imports_and_routes()
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=PROJECT_ROOT,
    )
    try:
        wait_for_server()
        validate_endpoints()
        print("Python 3.10 API validation passed.")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()


if __name__ == "__main__":
    main()
