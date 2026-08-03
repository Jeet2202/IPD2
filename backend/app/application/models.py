"""
JobApplication Beanie ODM document model — domain model for worker marketplace applications.
"""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from app.utils.enums import ApplicationStatus


class JobApplication(Document):
    """
    Worker job application for open marketplace bookings.

    Collection: job_applications
    Compound Index: (booking_id, worker_id) unique to prevent duplicate applications.
    """

    booking_id: PydanticObjectId = Field(..., description="Target booking ID")
    worker_id: PydanticObjectId = Field(..., description="Applicant worker user ID")
    application_status: ApplicationStatus = Field(
        default=ApplicationStatus.PENDING,
        description="Current application status (PENDING, ACCEPTED, REJECTED, WITHDRAWN)",
    )
    cover_letter: str | None = Field(
        default=None,
        description="Optional worker cover letter / message to customer",
    )
    proposed_price: float | None = Field(
        default=None,
        description="Optional proposed price (INR) for quotation workflow",
    )

    applied_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "job_applications"
        use_state_management = True
        indexes = [
            IndexModel(
                [("booking_id", 1), ("worker_id", 1)],
                unique=True,
                name="idx_booking_worker_unique",
            ),
            [("worker_id", 1), ("created_at", -1)],
            [("booking_id", 1), ("application_status", 1)],
        ]

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
