from pydantic import BaseModel, Field
from datetime import datetime

class LocationUpdatePayload(BaseModel):
    latitude: float = Field(..., description="Worker's current latitude")
    longitude: float = Field(..., description="Worker's current longitude")
    booking_id: str = Field(..., description="Active booking ID")
    timestamp: datetime = Field(..., description="Timestamp of the GPS reading")

class TrackingStateResponse(BaseModel):
    is_active: bool
    worker_location: dict | None = None
    last_updated_at: datetime | None = None
