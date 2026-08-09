"""
Worker profile Beanie document model — domain-specific data for service workers.
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field

from app.address.models import GeoJSONPoint
from app.utils.enums import WorkerAvailability


class WorkerProfile(Document):
    """
    Worker profile document linked 1:1 with User.

    Collection: worker_profiles
    """

    user_id: Annotated[PydanticObjectId, Indexed(unique=True)]

    profile_photo_url: str | None = Field(default=None, description="URL for worker profile picture")
    profile_photo_public_id: str | None = Field(default=None, description="Cloudinary public ID for worker profile picture")
    bio: str | None = Field(default=None, description="Short professional bio")
    experience_years: float = Field(default=0.0, ge=0.0, le=50.0, description="Total years of work experience")
    skills: list[str] = Field(default_factory=list, description="List of registered worker skills")
    languages: list[str] = Field(default_factory=list, description="Languages spoken by worker")
    working_radius_km: float = Field(default=10.0, ge=1.0, le=100.0, description="Service radius in kilometers")
    current_location: GeoJSONPoint | None = Field(
        default=None,
        description="Worker real-time GeoJSON Point location. Enables geospatial proximity queries.",
    )
    current_location_updated_at: datetime | None = Field(
        default=None,
        description="Timestamp when current GPS location was last updated (UTC)",
    )
    availability: WorkerAvailability = Field(default=WorkerAvailability.AVAILABLE, description="Real-time availability status")
    hourly_rate: float | None = Field(default=None, ge=0.0, le=50000.0, description="Base rate in INR")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average customer rating")
    review_count: int = Field(default=0, ge=0, description="Total number of reviews")
    rating_average: float = Field(default=0.0, ge=0.0, le=5.0, description="Overall average rating")
    total_reviews: int = Field(default=0, ge=0, description="Total number of reviews submitted")
    rating_distribution: dict[int, int] = Field(
        default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        description="Frequency count of ratings 1 to 5",
    )
    punctuality_avg: float = Field(default=0.0, ge=0.0, le=5.0, description="Average punctuality rating")
    quality_avg: float = Field(default=0.0, ge=0.0, le=5.0, description="Average quality rating")
    professionalism_avg: float = Field(default=0.0, ge=0.0, le=5.0, description="Average professionalism rating")
    communication_avg: float = Field(default=0.0, ge=0.0, le=5.0, description="Average communication rating")
    recommendation_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of customers who would recommend")
    would_recommend_count: int = Field(default=0, ge=0, description="Total count of positive recommendations")
    profile_completed: bool = Field(default=False, description="True if profile completion threshold is reached")
    is_verified: bool = Field(default=False, description="True if worker identity or profile verification has been approved")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "worker_profiles"
        use_state_management = True
        indexes = [
            [("current_location", "2dsphere")],
        ]

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
