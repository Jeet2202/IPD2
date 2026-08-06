"""
Marketplace Pydantic schemas — worker-facing marketplace responses.

Design & Privacy Guardrails:
    - Workers discover open customer bookings (status == PENDING, unassigned).
    - Customer PII (full name, phone, exact address line 1/2, landmark) is strictly
      REDACTED in marketplace responses.
    - Only sanitized, approximate location details (city, state, postal code,
      latitude, longitude) are returned to workers.
    - distance_km is included as a placeholder for future AI recommendation /
      haversine distance engines.
"""

from datetime import date, datetime
from pydantic import BaseModel, Field

from enum import Enum

from app.booking.models import ServiceSnapshot
from app.utils.enums import BookingStatus, BookingType


class MarketplaceSortOption(str, Enum):
    """Supported sort orders for marketplace job discovery."""

    RECOMMENDED = "recommended"
    NEWEST = "newest"
    OLDEST = "oldest"
    PRICE_HIGH = "price_high"
    PRICE_LOW = "price_low"
    DISTANCE = "distance"


class MarketplaceAddressResponse(BaseModel):
    """
    Sanitized, approximate location information for marketplace listing/details.
    Does NOT contain customer name, phone number, or street address.
    """

    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    postal_code: str = Field(..., description="6-digit PIN code")
    latitude: float | None = Field(
        default=None,
        description="Location latitude (derived from GeoJSON service_location)",
    )
    longitude: float | None = Field(
        default=None,
        description="Location longitude (derived from GeoJSON service_location)",
    )


class MarketplaceBookingItemResponse(BaseModel):
    """
    Marketplace-safe summary DTO for listing bookings on the marketplace tab.
    """

    id: str = Field(..., description="Booking ObjectId string")
    booking_number: str = Field(..., description="Unique booking reference (e.g., KS202600001)")
    booking_type: BookingType = Field(..., description="NORMAL_SERVICE or INSPECTION_REQUEST")
    status: BookingStatus = Field(..., description="Current booking status (PENDING)")
    service_snapshot: ServiceSnapshot = Field(..., description="Snapshotted service information")
    address: MarketplaceAddressResponse = Field(..., description="Sanitized approximate location")
    scheduled_date: date | None = Field(default=None, description="Preferred service date")
    scheduled_time: str | None = Field(default=None, description="Preferred time window")
    estimated_price: float | None = Field(default=None, description="Estimated base price (INR)")
    estimated_duration_minutes: int | None = Field(default=None, description="Estimated duration in minutes")
    distance_km: float | None = Field(
        default=None,
        description="Calculated GeoJSON distance to worker (km)",
    )
    is_recommended: bool = Field(
        default=False,
        description="True if job is recommended for worker based on deterministic scoring",
    )
    has_applied: bool = Field(
        default=False,
        description="True if the authenticated worker has already applied for this booking",
    )
    application_id: str | None = Field(
        default=None,
        description="Job application ObjectId string if worker has applied",
    )
    created_at: datetime = Field(..., description="Booking creation timestamp (UTC)")

    # Customer problem description & media photos (Cloudinary)
    problem_description: str | None = Field(default=None, description="Problem description provided by customer")
    problem_photos: list[str] = Field(default_factory=list, description="Photo URL strings uploaded by customer")
    custom_title: str | None = Field(default=None, description="User-defined title for CUSTOM_SERVICE bookings")
    custom_description: str | None = Field(default=None, description="Detailed requirements for CUSTOM_SERVICE bookings")
    custom_budget: float | None = Field(default=None, description="Customer estimated budget for CUSTOM_SERVICE bookings")
    category_slug: str | None = Field(default=None, description="Category slug")
    customer_notes: str | None = Field(default=None, description="Customer additional notes")
    inspection_charge: float | None = Field(default=None, description="Diagnostic visit fee")
    inspection_status: str | None = Field(default=None, description="Current inspection status")
    payment_status: str | None = Field(default=None, description="Payment status")


class MarketplaceBookingDetailResponse(MarketplaceBookingItemResponse):
    """
    Marketplace-safe detail DTO when tapping a card to open Booking Details.
    Includes additional problem descriptions & photos for inspection requests.
    Customer PII remains strictly redacted.
    """
    pass


class MarketplacePaginatedResponse(BaseModel):
    """
    Standardized paginated list response for marketplace bookings.
    """

    items: list[MarketplaceBookingItemResponse] = Field(..., description="List of marketplace bookings")
    total: int = Field(..., description="Total count matching search filters")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of available pages")
