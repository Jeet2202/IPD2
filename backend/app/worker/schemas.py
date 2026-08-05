"""
Pydantic schemas for Worker Profile requests and responses.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.utils.enums import WorkerAvailability


class UpdateWorkerLocationRequest(BaseModel):
    """Payload for PATCH /worker/profile/location — update worker's real-time GPS coordinates."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="GPS latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="GPS longitude")


class UpdateWorkerProfileRequest(BaseModel):
    """Payload for updating worker profile details."""

    full_name: str | None = Field(default=None, min_length=2, max_length=100, description="Full name of worker")
    bio: str | None = Field(default=None, max_length=1000, description="Short professional bio")
    experience_years: float | None = Field(default=None, ge=0.0, le=50.0, description="Years of professional experience")
    skills: list[str] | None = Field(default=None, max_length=20, description="List of skills offered")
    languages: list[str] | None = Field(default=None, max_length=10, description="Languages spoken")
    working_radius_km: float | None = Field(default=None, ge=1.0, le=100.0, description="Service radius in kilometers")
    availability: WorkerAvailability | None = Field(default=None, description="Availability status")
    hourly_rate: float | None = Field(default=None, ge=0.0, le=50000.0, description="Hourly rate in INR")

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            cleaned = [s.strip().lower() for s in v if s.strip()]
            return list(dict.fromkeys(cleaned))  # Deduplicate while preserving order
        return None

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            cleaned = [l.strip().lower() for l in v if l.strip()]
            return list(dict.fromkeys(cleaned))
        return None


class WorkerProfileResponse(BaseModel):
    """Full worker profile DTO combining identity and profile fields."""

    id: str = Field(..., description="Worker Profile ObjectId string")
    user_id: str = Field(..., description="Linked User ObjectId string")
    email: str = Field(..., description="User primary email")
    phone: str = Field(..., description="User primary phone")
    full_name: str = Field(..., description="Worker full name")
    role: str = Field(default="worker", description="User role")

    profile_photo_url: str | None = None
    profile_photo_public_id: str | None = None
    bio: str | None = None
    experience_years: float = 0.0
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    working_radius_km: float = 10.0
    availability: WorkerAvailability = WorkerAvailability.AVAILABLE
    hourly_rate: float | None = None
    rating: float = 0.0
    review_count: int = 0

    profile_completion_percentage: int = Field(..., ge=0, le=100, description="Calculated completion percentage (0-100)")
    profile_completed: bool = Field(default=False, description="True if completion threshold (>= 70%) is reached")

    created_at: datetime
    updated_at: datetime
