from pydantic import BaseModel, Field
from typing import List, Optional

class PricingEstimateRequest(BaseModel):
    booking_id: str = Field(..., description="The ID of the booking to estimate price for")
    estimated_duration_hours: float = Field(default=1.0, description="Estimated duration of the service in hours")
    urgency_level: str = Field(default="normal", description="Urgency: 'normal', 'high', 'critical'")
    preferred_date: Optional[str] = Field(None, description="Preferred date in YYYY-MM-DD format")
    preferred_time: Optional[str] = Field(None, description="Preferred time in HH:MM format")
    city: str = Field(..., description="City where the service is requested")
    locality: Optional[str] = Field(None, description="Locality within the city")
    booking_notes: Optional[str] = Field(None, description="Any additional notes provided by the user")
    complexity_level: str = Field(default="standard", description="Complexity: 'low', 'standard', 'high'")

class HistoricalSummary(BaseModel):
    min_price: float
    max_price: float
    avg_price: float
    median_price: float
    std_dev: float
    data_points: int

class PricingEstimateResponse(BaseModel):
    booking_id: str
    estimated_price: float
    min_price: float
    max_price: float
    confidence_percentage: int
    risk_level: str # 'low', 'medium', 'high'
    reasons: List[str]
    demand_level: str # 'Low', 'Normal', 'High', 'Peak'
    historical_summary: HistoricalSummary

class HistoricalAnalyticsResponse(BaseModel):
    service_id: str
    city: str
    historical_summary: HistoricalSummary
    recent_price_trends: List[float] # List of recent prices to show a trend
    outliers_detected: int
