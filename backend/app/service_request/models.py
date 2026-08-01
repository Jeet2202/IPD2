"""
Service Request module models — customer requests for home services.

Architecture:
    - Single Beanie Document: ServiceRequest.
    - Embedded models: ServiceAddress, PriceSnapshot.
    - References via strings (customer_id, category_id, service_id, worker_id).

Why Price Snapshot is embedded:
    - Pricing changes over time. When a request is created, the current
      market price, taxes, and fees must be frozen (snapshotted) so that
      the customer pays the agreed amount, even if the global PricingConfiguration
      or ServicePriceGuide changes tomorrow.
    - An embedded snapshot guarantees immutable financial history.

Why Address is embedded:
    - Customers can update their saved addresses (in CustomerProfile).
    - If a customer changes their address next month, it should NOT alter
      the historical record of where past services were delivered.
    - Embedding the full address at the time of booking ensures exact historical
      accuracy and avoids complex $lookup joins for location analytics.

Relationship strategy:
    - String references are used for customer_id, category_id, service_id,
      and worker_id (if assigned).
    - Avoids Beanie Link lazy loading and prevents circular imports across modules.
    - The service layer handles validation and hydration for API responses.

Database design & Scalability:
    - Denormalized category_id and service_id allow filtering requests
      without joining the catalog collections.
    - Optional worker_id allows atomic updates during the assignment phase
      using $set without restructuring the document.
    - Metadata field allows storing AI matching scores and tracking events
      without schema migrations.

Index strategy:
    - customer_id: O(1) lookup for customer's booking history.
    - worker_id: O(1) lookup for worker's assigned jobs (sparse index).
    - service_id / category_id: Analytics and dashboard filtering.
    - status + created_at: Common admin dashboard view (e.g., "show pending").
    - preferred_date: Range queries for scheduling and reminders.
    - is_emergency: Boolean index for priority dispatch queue.

Collection name: "service_requests" (explicit, lowercase, plural).
"""

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RequestStatus(str, Enum):
    """
    Lifecycle status of a service request.

    - REQUESTED: Created by customer, awaiting initial processing.
    - PENDING: Processing, waiting for worker assignment.
    - ACCEPTED: Accepted by the platform/worker.
    - ASSIGNED: Worker explicitly assigned, ready for service.
    - IN_PROGRESS: Worker has started the job on-site.
    - COMPLETED: Job successfully completed and paid.
    - CANCELLED: Cancelled before completion.
    - EXPIRED: Time slot passed without assignment.
    """

    REQUESTED = "requested"
    PENDING = "pending"
    ACCEPTED = "accepted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RequestPriority(str, Enum):
    """Priority level for dispatch and worker matching."""

    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CancelledBy(str, Enum):
    """Actor who cancelled the request."""

    CUSTOMER = "customer"
    WORKER = "worker"
    ADMIN = "admin"
    SYSTEM = "system"


# ---------------------------------------------------------------------------
# Embedded Models
# ---------------------------------------------------------------------------

class ServiceAddress(BaseModel):
    """
    Embedded address for a service request.

    Snapshotted from the customer's saved address at booking time to ensure
    historical accuracy even if the customer later deletes or updates their profile.
    """

    address_line: str = Field(..., max_length=500, description="Full address line")
    landmark: str | None = Field(None, max_length=200, description="Nearby landmark")
    city: str = Field(..., max_length=100, description="City name")
    state: str = Field(..., max_length=100, description="State name")
    pincode: str = Field(..., max_length=10, description="Postal code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


class PriceSnapshot(BaseModel):
    """
    Frozen pricing details at the time of booking.

    Protects the booking from future price changes in the catalog.
    """

    market_price: float = Field(..., ge=0.0, description="Base service price")
    worker_price: float = Field(default=0.0, ge=0.0, description="Agreed worker payout")
    inspection_charge: float = Field(default=0.0, ge=0.0, description="Inspection fee")
    service_fee: float = Field(default=0.0, ge=0.0, description="Platform service fee")
    tax: float = Field(default=0.0, ge=0.0, description="Calculated tax (GST)")
    total_price: float = Field(..., ge=0.0, description="Total amount payable")


# ---------------------------------------------------------------------------
# Service Request Document
# ---------------------------------------------------------------------------

class ServiceRequest(Document):
    """
    Customer's request for a service.

    This document represents the intent and initial booking. Once assigned
    and executed, it tracks the lifecycle through to completion. It does NOT
    contain deep execution logic (like worker clock-in/out logs), which belongs
    in a separate Job module, but it tracks the core state.

    Attributes:
        request_number: Human-readable unique ID (e.g., REQ-12345).
        customer_id: Reference to Customer profile user_id.
        category_id: Reference to ServiceCategory.
        service_id: Reference to Service.
        worker_id: Reference to assigned Worker profile (optional).

        service_address: Embedded snapshotted address.
        customer_location: Real-time [longitude, latitude] array (GeoJSON point)
                           if available from customer's device.
        preferred_date: Requested date of service.
        preferred_time_slot: Requested time window (e.g., "10:00 AM - 12:00 PM").
        estimated_duration: Expected minutes to complete.

        estimated_price: Preliminary total estimate.
        price_snapshot: Frozen financial breakdown.

        customer_description: Issue details provided by customer.
        attached_images: List of uploaded image URLs.

        status: Current lifecycle state.
        priority: Dispatch priority.
        is_emergency: True for immediate dispatch requests.
        requires_inspection: True if inspection is needed before final price.

        cancellation_reason: Reason text if cancelled.
        cancelled_by: Actor who cancelled.
        accepted_at: Timestamp when accepted.
        completed_at: Timestamp when completed.
    """

    # --- Identity & References ---
    request_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Human-readable unique ID",
        examples=["REQ-1725184000-A1B2"],
    )
    customer_id: str = Field(..., description="Customer User ObjectId")
    category_id: str = Field(..., description="ServiceCategory ObjectId")
    service_id: str = Field(..., description="Service ObjectId")
    worker_id: str | None = Field(
        default=None, description="Assigned Worker User ObjectId"
    )

    # --- Location & Timing ---
    service_address: ServiceAddress = Field(
        ..., description="Embedded snapshot of the service address"
    )
    customer_location: list[float] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="[longitude, latitude] of customer device at booking",
    )
    preferred_date: date = Field(..., description="Requested service date")
    preferred_time_slot: str = Field(
        ..., max_length=50, description="Requested time window (e.g., 10 AM - 12 PM)"
    )
    estimated_duration: int = Field(..., ge=1, description="Expected duration in mins")

    # --- Financials ---
    estimated_price: float = Field(..., ge=0.0, description="Initial estimate total")
    price_snapshot: PriceSnapshot = Field(..., description="Frozen price breakdown")

    # --- Details ---
    customer_description: str | None = Field(
        default=None, max_length=2000, description="Problem description"
    )
    attached_images: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="List of image URLs (Cloudinary/S3)",
    )

    # --- State ---
    status: RequestStatus = Field(
        default=RequestStatus.REQUESTED, description="Lifecycle status"
    )
    priority: RequestPriority = Field(
        default=RequestPriority.NORMAL, description="Dispatch priority"
    )
    is_emergency: bool = Field(
        default=False, description="True for priority emergency dispatch"
    )
    requires_inspection: bool = Field(
        default=False, description="True if inspection is required first"
    )

    # --- Cancellation & Lifecycle ---
    cancellation_reason: str | None = Field(
        default=None, max_length=1000, description="Reason if cancelled"
    )
    cancelled_by: CancelledBy | None = Field(
        default=None, description="Actor who cancelled"
    )
    accepted_at: datetime | None = Field(default=None, description="Acceptance time")
    completed_at: datetime | None = Field(default=None, description="Completion time")

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict, description="Flexible key-value store for features"
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp (UTC)",
    )

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "service_requests"
        use_state_management = True

        indexes = [
            # Customer history
            IndexModel([("customer_id", ASCENDING), ("created_at", DESCENDING)]),
            # Worker assignments (sparse for non-assigned requests)
            IndexModel([("worker_id", ASCENDING), ("status", ASCENDING)], sparse=True),
            # Service analytics
            IndexModel([("service_id", ASCENDING)]),
            IndexModel([("category_id", ASCENDING)]),
            # Admin queue filtering
            IndexModel([("status", ASCENDING), ("created_at", DESCENDING)]),
            # Scheduling queries
            IndexModel([("preferred_date", ASCENDING), ("status", ASCENDING)]),
            # Emergency dispatch queue
            IndexModel([("is_emergency", DESCENDING), ("status", ASCENDING)]),
        ]
