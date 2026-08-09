import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .routes import get_inference_engine, recommend_hybrid, router
from .schemas import RecommendationRequest, RecommendationResponse


def _load_deployment_config() -> Dict[str, Any]:
    """Load optional deployment settings without making API startup fragile."""
    config_path = Path(__file__).resolve().parents[1] / "configs" / "deployment_config.yaml"
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            return yaml.safe_load(config_file) or {}
    except (OSError, yaml.YAMLError) as exc:
        logging.getLogger(__name__).warning("Unable to load deployment config: %s", exc)
        return {}


def _allowed_origins(config: Dict[str, Any]) -> List[str]:
    configured_origins = config.get("cors", {}).get("allowed_origins", [])
    environment_origins = os.getenv("ALLOWED_ORIGINS")
    origins = set(configured_origins)
    if environment_origins:
        for origin in environment_origins.split(","):
            origin = origin.strip()
            if origin:
                origins.add(origin)
    return sorted(origins)


deployment_config = _load_deployment_config()
log_level = os.getenv("LOG_LEVEL", deployment_config.get("logging", {}).get("level", "INFO")).upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="Hybrid Recommendation System API",
    description="Production REST API for ALS, Content-Based, and Hybrid Recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(deployment_config),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.post("/predict", response_model=RecommendationResponse)
def predict_root(
    request: RecommendationRequest,
    engine: Any = Depends(get_inference_engine)
) -> RecommendationResponse:
    return recommend_hybrid(request, engine)


@app.get("/")
def root() -> dict:
    """Lightweight service identity endpoint."""
    return {"message": "Hybrid Recommendation API running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
