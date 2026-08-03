"""
Review Beanie ODM Document Model — Domain-specific customer reviews and ratings (Phase 4.7.6).
"""

from datetime import datetime, timezone
from typing import Annotated

import secrets

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field


class Review(Document):
    """
    Independent Review collection storing customer reviews for completed service bookings.

    Collection: reviews
    Indexes:
        - booking_id (Unique: 1 review per booking)
        - worker_id (Compound query indexing)
        - customer_id (Customer ownership indexing)
    """

    review_number: str = Field(
        default_factory=lambda: f"REV-{secrets.token_hex(6).upper()}",
        description="Unique human-readable review reference",
    )
    booking_id: Annotated[PydanticObjectId, Indexed(unique=True)]
    job_id: PydanticObjectId | None = Field(default=None, description="Legacy job_id field")
    worker_id: Annotated[PydanticObjectId, Indexed()]
    customer_id: Annotated[PydanticObjectId, Indexed()]

    overall_rating: float = Field(..., ge=1.0, le=5.0, description="Overall customer rating (1 to 5)")
    punctuality_rating: float = Field(..., ge=1.0, le=5.0, description="Punctuality rating (1 to 5)")
    quality_rating: float = Field(..., ge=1.0, le=5.0, description="Service quality rating (1 to 5)")
    professionalism_rating: float = Field(..., ge=1.0, le=5.0, description="Professionalism rating (1 to 5)")
    communication_rating: float = Field(..., ge=1.0, le=5.0, description="Communication rating (1 to 5)")

    review_title: str | None = Field(default=None, max_length=150, description="Optional title summarizing review")
    review_comment: str | None = Field(default=None, max_length=2000, description="Optional detailed feedback comment")
    would_recommend: bool = Field(default=True, description="True if customer would recommend worker")
    attachments: list[str] = Field(default_factory=list, description="Prepared Cloudinary attachment URLs")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reviews"
        use_state_management = True
        indexes = [
            [("worker_id", 1), ("created_at", -1)],
            [("customer_id", 1), ("created_at", -1)],
        ]

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
