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

    The client provides references (IDs) for service and address.
    The service layer validates existence, ownership, and active status,
    then creates immutable snapshots before persisting.
    """

    service_id: str = Field(
        ...,
        min_length=24,
        max_length=24,
        description="ObjectId of the service to book",
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
        description=(
            "NORMAL_SERVICE: standard service booking. "
            "INSPECTION_REQUEST: site-visit before committing."
        ),
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

    @field_validator("service_id", "address_id")
    @classmethod
    def validate_object_id(cls, v: str) -> str:
        """Ensure value looks like a valid MongoDB ObjectId (24 hex chars)."""
        v = v.strip()
        if not all(c in "0123456789abcdefABCDEF" for c in v):
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
    def validate_inspection_request(self) -> "CreateBookingRequest":
        """Enforce that problem_description is provided when booking_type is INSPECTION_REQUEST."""
        if self.booking_type == BookingType.INSPECTION_REQUEST:
            if not self.problem_description or not self.problem_description.strip():
                raise ValueError("Problem description is required for inspection requests.")
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

    booking_type: str = Field(..., description="NORMAL_SERVICE or INSPECTION_REQUEST")
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

    # Future stubs — always None in Phase 4.4.1
    worker_id: str | None = Field(default=None, description="[Phase 4.4.x] Assigned worker ObjectId")
    assigned_at: str | None = Field(default=None, description="[Phase 4.4.x] Worker assignment timestamp")
    started_at: str | None = Field(default=None, description="[Phase 4.4.x] Job started timestamp")
    completed_at: str | None = Field(default=None, description="[Phase 4.4.x] Job completed timestamp")
    cancelled_at: str | None = Field(default=None, description="[Phase 4.4.1] Cancellation timestamp")
    cancellation_reason: str | None = Field(default=None, description="[Phase 4.4.1] Cancellation reason")
    final_price: float | None = Field(default=None, description="[Phase 4.6] Final confirmed price (INR)")
    inspection_id: str | None = Field(default=None, description="[Phase 4.5] Inspection ObjectId")
    quotation_id: str | None = Field(default=None, description="[Phase 4.6] Quotation ObjectId")
    payment_id: str | None = Field(default=None, description="[Phase 4.7] Payment ObjectId")

    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last-update timestamp")

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    """Response for listing customer bookings."""

    total: int = Field(..., description="Total number of bookings matching the filter")
    bookings: list[BookingResponse] = Field(..., description="List of booking DTOs")
