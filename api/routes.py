import sys
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List

# Ensure project root is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.inference.recommend import InferenceEngine
from .schemas import (
    RecommendationItem,
    UserRecommendationResponse,
    RecommendationRequest,
    TextSearchRequest,
    RecommendationResponse,
    HealthCheckResponse,
    ItemScore
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Global inference engine instance
_engine: InferenceEngine = None


def get_inference_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        _engine = InferenceEngine()
    return _engine


@router.get("/health", response_model=HealthCheckResponse)
def health_check(engine: InferenceEngine = Depends(get_inference_engine)):
    return HealthCheckResponse(
        status="ok",
        models_loaded=True
    )


@router.get("/recommend/{user_id}", response_model=UserRecommendationResponse)
def get_recommendations_for_user(
    user_id: int,
    top_n: int = Query(default=10, ge=1, le=100, description="Number of recommendations to return"),
    engine: InferenceEngine = Depends(get_inference_engine)
):
    """
    GET /recommend/{user_id}?top_n=10
    Fetches top-N recommendations for a target user ID.
    Returns Hybrid recommendations for known users and Popular items fallback for unknown users.
    """
    try:
        results = engine.recommend(user_id=user_id, top_n=top_n)
        recommendation_items = [
            RecommendationItem(
                item_id=int(rec["item_id"]),
                score=float(rec["score"]),
                source=str(rec["source"])
            )
            for rec in results
        ]
        return UserRecommendationResponse(
            user_id=user_id,
            recommendations=recommendation_items
        )
    except Exception as e:
        logger.error(f"Error serving recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/hybrid", response_model=RecommendationResponse)
def recommend_hybrid(
    request: RecommendationRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
):
    try:
        results = engine.recommend_hybrid(
            user_id=request.user_id,
            top_n=request.top_n,
            weights=request.weights
        )
        scores = [ItemScore(item_id=int(item_id), score=float(score)) for item_id, score in results]
        return RecommendationResponse(
            user_id=request.user_id,
            model_used="HybridRecommender",
            recommendations=scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/als", response_model=RecommendationResponse)
def recommend_als(
    request: RecommendationRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
):
    try:
        results = engine.recommend_als(
            user_id=request.user_id,
            top_n=request.top_n
        )
        scores = [ItemScore(item_id=int(item_id), score=float(score)) for item_id, score in results]
        return RecommendationResponse(
            user_id=request.user_id,
            model_used="ALSPredictor",
            recommendations=scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/content", response_model=RecommendationResponse)
def recommend_content(
    request: RecommendationRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
):
    try:
        results = engine.recommend_content_user(
            user_id=request.user_id,
            top_n=request.top_n
        )
        scores = [ItemScore(item_id=int(item_id), score=float(score)) for item_id, score in results]
        return RecommendationResponse(
            user_id=request.user_id,
            model_used="ContentPredictor",
            recommendations=scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/search", response_model=RecommendationResponse)
def recommend_search(
    request: TextSearchRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
):
    try:
        results = engine.recommend_text_search(
            query=request.query,
            top_n=request.top_n
        )
        scores = [ItemScore(item_id=int(item_id), score=float(score)) for item_id, score in results]
        return RecommendationResponse(
            model_used="ContentTextSearch",
            recommendations=scores,
            metadata={"query": request.query}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
