from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationRequest(BaseModel):
    booking_id: str = Field(..., description="The ID of the booking to generate recommendations for")
    max_results: Optional[int] = Field(default=10, description="Maximum number of workers to return")

class WorkerRecommendation(BaseModel):
    worker_id: str = Field(..., description="The ID of the recommended worker")
    score: float = Field(..., description="Overall recommendation score (0-100)")
    confidence: str = Field(..., description="Confidence percentage")
    reasons: List[str] = Field(..., description="Reasons why this worker was recommended")
    distance_km: float = Field(..., description="Distance from the booking location in km")
    estimated_arrival_mins: Optional[int] = Field(None, description="Estimated arrival time in minutes")
    ranking: int = Field(..., description="Ranking position (1 is best)")

class RecommendationResponse(BaseModel):
    booking_id: str
    recommendations: List[WorkerRecommendation]
