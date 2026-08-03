from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class Location(BaseModel):
    type: str = "Point"
    coordinates: Tuple[float, float] = Field(..., description="[longitude, latitude]")

class BookingModel(BaseModel):
    id: str
    service_id: str
    category_id: str
    location: Location
    status: str
    
class WorkerModel(BaseModel):
    id: str
    is_active: bool
    is_verified: bool
    is_suspended: bool
    services: List[str]  # List of service IDs
    location: Location
    rating: float
    experience_years: int
    completion_rate: float
    acceptance_rate: float
    cancellation_rate: float
    avg_response_time_mins: float
    is_available: bool

class QuotationModel(BaseModel):
    id: str
    booking_id: str
    worker_id: str
    amount: float
    status: str # 'pending', 'accepted', 'rejected'
    created_at: str # ISO format datetime
