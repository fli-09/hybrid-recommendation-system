from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    item_id: int = Field(..., description="Recommended product item ID")
    product_name: Optional[str] = Field(default=None, description="Product display name")
    category: Optional[str] = Field(default=None, description="Product category")
    brand: Optional[str] = Field(default=None, description="Product brand")
    price: Optional[float] = Field(default=None, description="Product price")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    description: Optional[str] = Field(default=None, description="Product description")
    score: float = Field(..., description="Recommendation score")
    source: str = Field(..., description="Recommendation source model (e.g. Hybrid, Popular)")


class UserRecommendationResponse(BaseModel):
    user_id: int = Field(..., description="User ID requested")
    recommendations: List[RecommendationItem] = Field(..., description="Top-N recommendations list")


class RecommendationRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user for whom to generate recommendations")
    top_n: int = Field(default=10, ge=1, le=100, description="Number of recommendations to return")
    weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional custom weights for hybrid scoring (e.g. {'als': 0.6, 'content': 0.4})"
    )


class TextSearchRequest(BaseModel):
    query: str = Field(..., description="Text query describing item of interest")
    top_n: int = Field(default=10, ge=1, le=100, description="Number of recommendations to return")


class ItemScore(BaseModel):
    item_id: int = Field(..., description="Recommended item ID")
    product_name: Optional[str] = Field(default=None, description="Product display name")
    category: Optional[str] = Field(default=None, description="Product category")
    brand: Optional[str] = Field(default=None, description="Product brand")
    price: Optional[float] = Field(default=None, description="Product price")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    description: Optional[str] = Field(default=None, description="Product description")
    score: float = Field(..., description="Recommendation score")
    source: str = Field(..., description="Recommendation source model (e.g. Hybrid, Popular)")


class RecommendationResponse(BaseModel):
    user_id: Optional[int] = Field(default=None, description="User ID requested")
    model_used: str = Field(..., description="Name of recommendation model used")
    recommendations: List[ItemScore] = Field(..., description="List of recommended items with scores")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context metadata")


class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy")
    models_loaded: bool = Field(...)
