"""
Booking schemas — request validation and response serialization.

Schemas:
    CreateBookingRequest  — POST /bookings payload
    BookingResponse       — Full booking DTO returned by all endpoints
    BookingListResponse   — Paginated list wrapper

Design:
    - The API accepts service_id and address_id (references).
    - The service and address are validated in the service layer.
    - Snapshots are created server-side — never sent by the client.
    - lat/lng in the response is extracted from service_location for
      Flutter compatibility (same pattern as Address module).
"""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.utils.enums import BookingStatus, BookingType


# ---------------------------------------------------------------------------
# Embedded Response DTOs
# ---------------------------------------------------------------------------

class AddressSnapshotResponse(BaseModel):
    """Address snapshot embedded in BookingResponse."""

    address_id: str
    label: str
    full_name: str
    phone: str
    address_line_1: str
    address_line_2: str | None = None
    landmark: str | None = None
    city: str
    state: str
    country: str
    postal_code: str
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class ServiceSnapshotResponse(BaseModel):
    """Service snapshot embedded in BookingResponse."""

    service_id: str
    name: str
    category_id: str
    category_slug: str
    base_market_price: float
    estimated_duration_minutes: int
    is_inspection_required: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class CreateBookingRequest(BaseModel):
    """
    Payload for POST /bookings — create a new service booking.

    Supports:
        - NORMAL_SERVICE: requires service_id.
        - CUSTOM_SERVICE: requires custom_title and category_slug.
        - INSPECTION_REQUEST: requires problem_description and category_slug (or service_id).
    """

    service_id: str | None = Field(
        default=None,
        description="ObjectId of the service to book (Required for NORMAL_SERVICE)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    address_id: str = Field(
        ...,
        min_length=24,
        max_length=24,
        description="ObjectId of the customer's saved address for this booking",
        examples=["60d5ec49f1a2c8b1f8e4e1b2"],
    )
    booking_type: BookingType = Field(
        default=BookingType.NORMAL_SERVICE,
        description="NORMAL_SERVICE, INSPECTION_REQUEST, or CUSTOM_SERVICE",
    )
    scheduled_date: date | None = Field(
        default=None,
        description="Preferred service date (YYYY-MM-DD). Omit for ASAP.",
        examples=["2026-08-15"],
    )
    scheduled_time: str | None = Field(
        default=None,
        max_length=20,
        description="Preferred time window (e.g., '10:00-12:00'). Omit for ASAP.",
        examples=["10:00-12:00"],
    )
    customer_notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional instructions or notes for the worker.",
        examples=["Please call 10 minutes before arrival."],
    )
    problem_description: str | None = Field(
        default=None,
        max_length=1000,
        description="Required when booking_type is INSPECTION_REQUEST.",
        examples=["AC unit is making loud buzzing noise and leaking water."],
    )
    problem_photos: list[str] = Field(
        default_factory=list,
        description="Optional photo URL strings (Cloudinary)",
    )

    # Custom Service & Inspection Category Fields
    custom_title: str | None = Field(
        default=None,
        max_length=200,
        description="Required for CUSTOM_SERVICE bookings.",
    )
    custom_description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed requirements for CUSTOM_SERVICE bookings.",
    )
    custom_budget: float | None = Field(
        default=None,
        ge=0.0,
        description="Estimated budget for CUSTOM_SERVICE bookings (INR).",
    )
    category_slug: str | None = Field(
        default=None,
        description="Service category slug for CUSTOM_SERVICE or standalone INSPECTION_REQUEST.",
    )

    @field_validator("address_id")
    @classmethod
    def validate_address_id(cls, v: str) -> str:
        """Ensure value looks like a valid MongoDB ObjectId (24 hex chars)."""
        v = v.strip()
        if len(v) != 24 or not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("Must be a valid 24-character hexadecimal ObjectId.")
        return v

    @field_validator("service_id")
    @classmethod
    def validate_service_id(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) != 24 or not all(c in "0123456789abcdefABCDEF" for c in v):
                raise ValueError("Must be a valid 24-character hexadecimal ObjectId.")
        return v

    @field_validator("customer_notes")
    @classmethod
    def strip_notes(cls, v: str | None) -> str | None:
        return v.strip() if v and v.strip() else None

    @field_validator("scheduled_date")
    @classmethod
    def validate_scheduled_date(cls, v: date | None) -> date | None:
        """Scheduled date cannot be in the past."""
        if v is not None and v < date.today():
            raise ValueError("Scheduled date cannot be in the past.")
        return v

    @field_validator("scheduled_time")
    @classmethod
    def validate_scheduled_time(cls, v: str | None) -> str | None:
        """Sanitize scheduled_time string if provided."""
        if v is not None:
            v = v.strip()
            return v if v else None
        return None

    @model_validator(mode="after")
    def validate_booking_type_fields(self) -> "CreateBookingRequest":
        if self.booking_type == BookingType.NORMAL_SERVICE:
            if not self.service_id:
                raise ValueError("service_id is required for normal service bookings.")
        elif self.booking_type == BookingType.CUSTOM_SERVICE:
            if not self.custom_title or not self.custom_title.strip():
                raise ValueError("custom_title is required for custom service bookings.")
            if not self.category_slug or not self.category_slug.strip():
                raise ValueError("category_slug is required for custom service bookings.")
        elif self.booking_type == BookingType.INSPECTION_REQUEST:
            if not self.problem_description or not self.problem_description.strip():
                raise ValueError("Problem description is required for inspection requests.")
            if not self.service_id and not self.category_slug:
                raise ValueError("Either category_slug or service_id is required for inspection requests.")
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class BookingResponse(BaseModel):
    """
    Full booking DTO returned by all booking endpoints.

    service_location is serialized as flat latitude/longitude fields
    for Flutter compatibility (same pattern as Address module).
    """

    id: str = Field(..., description="Booking ObjectId string")
    booking_number: str = Field(..., description="Human-readable booking reference (KSYYYYnnnnn)")
    customer_id: str = Field(..., description="Customer User ObjectId")

    booking_type: str = Field(..., description="NORMAL_SERVICE, INSPECTION_REQUEST, or CUSTOM_SERVICE")
    status: str = Field(..., description="Current booking status")

    service_snapshot: ServiceSnapshotResponse
    address_snapshot: AddressSnapshotResponse

    # Flat location from service_location GeoJSON (null if no GPS on address)
    latitude: float | None = Field(
        default=None,
        description="Service location latitude (from address GeoJSON snapshot)",
    )
    longitude: float | None = Field(
        default=None,
        description="Service location longitude (from address GeoJSON snapshot)",
    )

    scheduled_date: str | None = Field(default=None, description="Preferred date (YYYY-MM-DD)")
    scheduled_time: str | None = Field(default=None, description="Preferred time window")

    estimated_price: float | None = Field(default=None, description="Estimated price (INR)")
    estimated_duration_minutes: int | None = Field(default=None, description="Estimated duration (minutes)")

    customer_notes: str | None = None
    problem_description: str | None = None
    problem_photos: list[str] = Field(default_factory=list)

    custom_title: str | None = None
    custom_description: str | None = None
    custom_budget: float | None = None
    category_slug: str | None = None
    inspection_status: str | None = None
    inspection_scheduled_at: str | None = None

    # Execution & Completion (Phase 4.7.2)
    worker_id: str | None = Field(default=None, description="Assigned worker ObjectId")
    worker_name: str | None = Field(default=None, description="Assigned worker full name")
    worker_phone: str | None = Field(default=None, description="Assigned worker phone number")
    assigned_at: str | None = Field(default=None, description="Worker assignment timestamp")
    en_route_at: str | None = Field(default=None, description="Worker en route timestamp")
    arrived_at: str | None = Field(default=None, description="Worker arrival timestamp")
    started_at: str | None = Field(default=None, description="Job started timestamp")
    completed_at: str | None = Field(default=None, description="Job completed timestamp")
    cancelled_at: str | None = Field(default=None, description="Cancellation timestamp")
    cancellation_reason: str | None = Field(default=None, description="Cancellation reason")
    final_price: float | None = Field(default=None, description="Final confirmed price (INR)")
    inspection_id: str | None = Field(default=None, description="Inspection ObjectId")
    quotation_id: str | None = Field(default=None, description="Quotation ObjectId")
    payment_id: str | None = Field(default=None, description="Payment ObjectId")

    completion_notes: str | None = Field(default=None, description="Worker completion notes")
    work_summary: str | None = Field(default=None, description="Worker summary of work performed")
    before_photos: list[str] = Field(default_factory=list, description="Before work photo URLs")
    after_photos: list[str] = Field(default_factory=list, description="After work photo URLs")
    timeline: list["BookingTimelineEventResponse"] = Field(default_factory=list, description="Audit timeline events")

    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last-update timestamp")

    # ── Marketplace fields ──────────────────────────────────────────────────
    applicant_count: int = Field(
        default=0,
        description="Number of workers who have applied for this marketplace booking",
    )

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """Response DTO for an individual chat message."""

    id: str = Field(..., description="Message ObjectId string")
    booking_id: str = Field(..., description="Booking ObjectId string")
    sender_id: str = Field(..., description="Sender User ObjectId string")
    message: str = Field(..., description="Message body text")
    timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    is_read: bool = Field(default=False, description="Read receipt status")

    media_url: str | None = Field(default=None, description="Optional attached media URL")
    media_type: str | None = Field(default=None, description="Media type: image or document")
    media_name: str | None = Field(default=None, description="Original filename")
    media_size: int | None = Field(default=None, description="File size in bytes")


class ChatMessageListResponse(BaseModel):
    """Response DTO for listing chat messages for a booking."""

    messages: list[ChatMessageResponse] = Field(default_factory=list)



class BookingTimelineEventResponse(BaseModel):
    """Timeline event response schema (Phase 4.7.4)."""

    event_id: str
    event_type: str = "STATUS_CHANGE"
    status: str
    previous_status: str | None = None
    new_status: str | None = None
    title: str
    description: str | None = None
    actor_id: str
    actor_role: str
    timestamp: str
    metadata: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class BookingTimelineResponse(BaseModel):
    """Paginated timeline response for GET /bookings/{id}/timeline."""

    booking_id: str = Field(..., description="Booking ObjectId string")
    booking_number: str = Field(..., description="Human-readable booking reference number")
    current_status: str = Field(..., description="Current booking status string")
    total_events: int = Field(..., description="Total count of timeline events recorded")
    page: int = Field(default=1, description="Current page number (1-indexed)")
    page_size: int = Field(default=50, description="Items per page")
    events: list[BookingTimelineEventResponse] = Field(
        default_factory=list,
        description="Chronologically ordered list of timeline event objects",
    )


class CompleteJobRequest(BaseModel):
    """
    Payload for PUT /worker/bookings/{id}/complete — mark job as WORK_COMPLETED.
    """

    completion_notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional worker notes recorded upon completion.",
    )
    work_summary: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional summary of work completed.",
    )
    before_photos: list[str] = Field(
        default_factory=list,
        description="List of Cloudinary image URLs taken before work execution.",
    )
    after_photos: list[str] = Field(
        default_factory=list,
        description="List of Cloudinary image URLs taken after work completion.",
    )


class BookingListResponse(BaseModel):
    """Response for listing customer bookings."""

    total: int = Field(..., description="Total number of bookings matching the filter")
    bookings: list[BookingResponse] = Field(..., description="List of booking DTOs")


# ---------------------------------------------------------------------------
# Status Lifecycle Schemas (Phase 4.7.1)
# ---------------------------------------------------------------------------

class UpdateBookingStatusRequest(BaseModel):
    """
    Payload for PUT /worker/bookings/{id}/status — worker updates booking execution status.
    """

    status: BookingStatus = Field(
        ...,
        description="Target lifecycle status (e.g. worker_en_route, arrived, in_progress, work_completed).",
    )
    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Optional worker note for status transition.",
    )


class BookingStatusResponse(BaseModel):
    """
    Response DTO for GET /bookings/{id}/status — detailed status inspection.
    """

    booking_id: str = Field(..., description="Booking ObjectId string")
    booking_number: str = Field(..., description="Human-readable booking reference number")
    current_status: str = Field(..., description="Current booking lifecycle status string")
    next_allowed_statuses: list[str] = Field(..., description="List of valid next status strings")
    assigned_worker_id: str | None = Field(default=None, description="Assigned worker ObjectId string if assigned")
    timestamps: dict[str, str | None] = Field(
        default_factory=dict,
        description="Lifecycle milestone timestamps (assigned_at, started_at, completed_at, cancelled_at, etc.)",
    )


# ---------------------------------------------------------------------------
# Customer Confirmation Schemas (Phase 4.7.3)
# ---------------------------------------------------------------------------

class ConfirmCompletionRequest(BaseModel):
    """
    Payload for PUT /customer/bookings/{id}/confirm — customer confirms job completion.
    """

    notes: str | None = Field(
        default=None,
        max_length=500,
        description="Optional customer note or feedback upon confirmation.",
    )


class CustomerCompletionReviewResponse(BaseModel):
    """
    Response for GET /customer/bookings/{id}/completion — customer reviews completed work.
    """

    booking_id: str = Field(..., description="Booking ObjectId string")
    booking_number: str = Field(..., description="Human-readable booking reference number")
    service_name: str = Field(..., description="Service display name")
    status: str = Field(..., description="Current booking status")
    worker_id: str | None = Field(default=None, description="Assigned worker ObjectId string")
    estimated_duration_minutes: int | None = Field(default=None, description="Estimated duration (minutes)")
    started_at: str | None = Field(default=None, description="ISO timestamp when work started")
    completed_at: str | None = Field(default=None, description="ISO timestamp when work was completed")
    actual_duration_minutes: int | None = Field(default=None, description="Actual duration calculated in minutes")
    completion_notes: str | None = Field(default=None, description="Worker completion notes")
    work_summary: str | None = Field(default=None, description="Summary of work completed")
    before_photos: list[str] = Field(default_factory=list, description="Before photos Cloudinary URLs")
    after_photos: list[str] = Field(default_factory=list, description="After photos Cloudinary URLs")
    timeline: list[BookingTimelineEventResponse] = Field(default_factory=list, description="Audit timeline events")

    model_config = {"from_attributes": True}


