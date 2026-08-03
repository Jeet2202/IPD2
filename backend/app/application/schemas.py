"""
JobApplication Pydantic Schemas — request and response DTOs for worker applications.
"""

from datetime import date, datetime
from pydantic import BaseModel, Field

from app.utils.enums import ApplicationStatus, BookingStatus, BookingType


class JobApplicationCreateRequest(BaseModel):
    """
    Request DTO for worker applying to a marketplace booking.
    """

    booking_id: str = Field(..., description="Target booking ObjectId string")
    cover_letter: str | None = Field(
        default=None,
        description="Optional worker message / cover letter",
    )
    proposed_price: float | None = Field(
        default=None,
        ge=0.0,
        description="Optional proposed price (INR) for quotation workflow",
    )


class JobApplicationResponse(BaseModel):
    """
    Worker-facing job application DTO including booking context.
    """

    id: str = Field(..., description="Job application ObjectId string")
    booking_id: str = Field(..., description="Booking ObjectId string")
    worker_id: str = Field(..., description="Worker user ObjectId string")
    application_status: ApplicationStatus = Field(..., description="Application status (PENDING, ACCEPTED, REJECTED, WITHDRAWN)")
    cover_letter: str | None = Field(default=None, description="Optional worker cover letter")
    proposed_price: float | None = Field(default=None, description="Optional proposed price")
    
    # Booking Context Snapshot
    booking_number: str = Field(..., description="Booking reference number (e.g. KS202600001)")
    service_name: str = Field(..., description="Service name")
    category_slug: str = Field(..., description="Service category slug")
    booking_type: BookingType = Field(..., description="NORMAL_SERVICE or INSPECTION_REQUEST")
    booking_status: BookingStatus = Field(..., description="Current booking status")
    scheduled_date: date | None = Field(default=None, description="Preferred service date")
    estimated_price: float | None = Field(default=None, description="Estimated base price")
    
    applied_at: datetime = Field(..., description="Application submission timestamp (UTC)")


class JobApplicationPaginatedResponse(BaseModel):
    """
    Paginated response DTO for listing worker applications.
    """

    items: list[JobApplicationResponse] = Field(..., description="List of worker job applications")
    total: int = Field(..., description="Total count matching filters")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total available pages")
