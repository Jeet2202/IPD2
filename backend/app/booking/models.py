"""
Booking Beanie document model — bookings collection.

Design:
    - Booking is the central transaction record in Ally.
    - Each booking links: Customer → Service → Address (snapshot) → Worker (future).
    - Address is snapshotted at booking creation: changes to the address after
      booking do not affect the active job (same pattern as e-commerce orders).
    - GeoJSON Point is copied from Address.location into service_location so
      future $geoNear aggregation can find nearby workers without joining addresses.
    - booking_number is a unique, human-readable identifier (KS202600001).
    - worker_id, inspection_id, quotation_id, payment_id are nullable stubs
      — all None at creation, populated by future phases without schema change.

Collection: bookings

Index strategy:
    - customer_id + status + created_at: Customer's booking history filtered
      by status, sorted newest-first. The most common query.
    - booking_number (unique): Fast lookup by human-readable booking number.
    - status + created_at: Admin/worker dashboards listing pending bookings.
    - service_location (2dsphere): Geo queries for worker matching and distance
      calculation (Phase 4.5).
    - service_id + status: Analytics — how many pending bookings per service.

Future integration points:
    - Phase 4.4.x (Worker Assignment): Set worker_id, status → ACCEPTED.
    - Phase 4.5   (Inspection):        Set inspection_id, link InspectionRequest.
    - Phase 4.6   (Quotation):         Set quotation_id, final_price.
    - Phase 4.7   (Payment):           Set payment_id, payment_status.
    - Phase 4.8   (Notifications):     Trigger on status transitions.
"""

from datetime import date, datetime, time, timezone

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, IndexModel
from typing import Annotated

from app.address.models import GeoJSONPoint
from app.utils.enums import BookingStatus, BookingType, InspectionStatus


# ---------------------------------------------------------------------------
# Embedded Address Snapshot
# ---------------------------------------------------------------------------

class AddressSnapshot(BaseModel):
    """
    Point-in-time snapshot of the customer's address at booking creation.

    Embedded directly in the Booking document so that:
    - Editing or deleting the address after booking does not affect the job.
    - Workers always see the address that was valid when the customer booked.
    - No join required to display address in booking detail.

    location mirrors Address.location (GeoJSON Point) for $geoNear support.
    """

    address_id: str = Field(
        ...,
        description="Original Address document ObjectId (reference, not join)",
    )
    label: str = Field(
        ...,
        description="Address label (Home / Office / Other)",
        examples=["Home"],
    )
    full_name: str = Field(
        ...,
        description="Contact person full name",
        examples=["Rajesh Kumar"],
    )
    phone: str = Field(
        ...,
        description="Contact phone number",
        examples=["+919876543210"],
    )
    address_line_1: str = Field(..., description="Primary address line")
    address_line_2: str | None = Field(default=None, description="Secondary address line")
    landmark: str | None = Field(default=None, description="Nearby landmark")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    country: str = Field(default="India", description="Country")
    postal_code: str = Field(..., description="6-digit PIN code")
    location: GeoJSONPoint | None = Field(
        default=None,
        description=(
            "GeoJSON Point copied from Address.location. "
            "Enables $geoNear aggregation for worker matching. "
            "None if the address had no GPS coordinates."
        ),
    )


# ---------------------------------------------------------------------------
# Embedded Service Snapshot
# ---------------------------------------------------------------------------

class ServiceSnapshot(BaseModel):
    """
    Point-in-time snapshot of the service at booking creation.

    Prevents service catalog changes (price updates, deactivation) from
    retroactively modifying historical bookings.
    """

    service_id: str = Field(..., description="Original Service document ObjectId")
    name: str = Field(..., description="Service display name at booking time")
    category_id: str = Field(..., description="ServiceCategory ObjectId")
    category_slug: str = Field(..., description="Denormalized category slug")
    base_market_price: float = Field(..., description="Base price at booking time (INR)")
    estimated_duration_minutes: int = Field(..., description="Expected duration at booking time (minutes)")
    is_inspection_required: bool = Field(
        default=False,
        description="Whether an inspection was required for this service at booking time",
    )


# ---------------------------------------------------------------------------
# Embedded Timeline Event Snapshot (Phase 4.7.2)
# ---------------------------------------------------------------------------

class BookingTimelineEvent(BaseModel):
    """
    Audit trail event entry for booking status progression and domain tracking (Phase 4.7.4).
    """

    event_id: str = Field(
        default_factory=lambda: str(PydanticObjectId()),
        description="Unique event ID string",
    )
    event_type: str = Field(
        default="STATUS_CHANGE",
        description="Event discriminator type (STATUS_CHANGE, BOOKING_CREATED, WORKER_ASSIGNED, GPS_UPDATE, ETA_UPDATE, PAYMENT, DISPUTE)",
    )
    status: BookingStatus = Field(..., description="Booking status at event time")
    previous_status: BookingStatus | None = Field(
        default=None,
        description="Booking status prior to transition",
    )
    new_status: BookingStatus | None = Field(
        default=None,
        description="Booking status resulting from transition",
    )
    title: str = Field(..., description="Short human-readable event title")
    description: str | None = Field(default=None, description="Optional event notes/description")
    actor_id: PydanticObjectId = Field(..., description="User ObjectId of actor who triggered event")
    actor_role: str = Field(..., description="Role of actor (customer, worker, admin, system)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of event occurrence",
    )
    metadata: dict = Field(default_factory=dict, description="Arbitrary event metadata (GPS, ETA, notifications, payment info)")


# ---------------------------------------------------------------------------
# Booking Document
# ---------------------------------------------------------------------------

class Booking(Document):
    """
    Core booking transaction document.

    Lifecycle (Phase 4.4.1 implements PENDING + CANCELLED only):
        PENDING → ACCEPTED → IN_PROGRESS → COMPLETED
              ↘ CANCELLED (by customer, anytime before ACCEPTED)

    All future extension points (worker_id, inspection_id, etc.) are
    declared as Optional[...] = None to avoid schema migrations.
    """

    # ── Identity ─────────────────────────────────────────────────────────────

    booking_number: Annotated[str, Indexed(unique=True)] = Field(
        ...,
        description=(
            "Human-readable booking reference (e.g., KS202600001). "
            "Unique, sequential per year, generated by BookingRepository."
        ),
        examples=["KS202600001"],
    )

    # ── Ownership ─────────────────────────────────────────────────────────────

    customer_id: Annotated[PydanticObjectId, Indexed()] = Field(
        ...,
        description="User ObjectId of the customer who made this booking",
    )

    # ── Type & Status ─────────────────────────────────────────────────────────

    booking_type: BookingType = Field(
        default=BookingType.NORMAL_SERVICE,
        description=(
            "NORMAL_SERVICE: standard service booking. "
            "INSPECTION_REQUEST: site-visit assessment before full quote."
        ),
    )
    status: BookingStatus = Field(
        default=BookingStatus.PENDING,
        description="Current lifecycle state of the booking.",
    )

    # ── Snapshots (immutable at creation) ────────────────────────────────────

    service_snapshot: ServiceSnapshot = Field(
        ...,
        description="Point-in-time copy of the service at booking creation.",
    )
    address_snapshot: AddressSnapshot = Field(
        ...,
        description="Point-in-time copy of the customer's address at booking creation.",
    )

    # ── GeoJSON location (denormalized from address_snapshot.location) ───────

    service_location: GeoJSONPoint | None = Field(
        default=None,
        description=(
            "GeoJSON Point for the service location. "
            "Copied from address_snapshot.location. "
            "Indexed with 2dsphere for $geoNear worker matching queries."
        ),
    )

    # ── Scheduling ────────────────────────────────────────────────────────────

    scheduled_date: date | None = Field(
        default=None,
        description=(
            "Customer's preferred service date (ISO 8601 date). "
            "None for ASAP / on-demand bookings."
        ),
        examples=["2026-08-15"],
    )
    scheduled_time: str | None = Field(
        default=None,
        max_length=20,
        description=(
            "Customer's preferred service time window (e.g., '10:00-12:00', 'morning'). "
            "None for ASAP / on-demand bookings."
        ),
        examples=["10:00-12:00"],
    )

    # ── Pricing (at booking creation) ─────────────────────────────────────────

    estimated_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500_000.0,
        description=(
            "Estimated price for the service (INR). "
            "Copied from service.base_market_price at booking time. "
            "May differ from final_price after inspection/negotiation."
        ),
        examples=[499.0],
    )
    estimated_duration_minutes: int | None = Field(
        default=None,
        gt=0,
        le=2880,
        description="Estimated job duration (minutes) from service snapshot.",
        examples=[60],
    )

    # ── Inspection Details ───────────────────────────────────────────────────

    problem_description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detailed problem description provided during inspection request.",
        examples=["Living room switchboard is sparking whenever the AC is turned on."],
    )
    problem_photos: list[str] = Field(
        default_factory=list,
        description="List of photo URL strings (Cloudinary) uploaded for inspection.",
    )

    # ── Custom Service & Inspection Workflow Fields ─────────────────────────

    custom_title: str | None = Field(
        default=None,
        max_length=200,
        description="User-defined title for CUSTOM_SERVICE bookings.",
    )
    custom_description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed requirements for CUSTOM_SERVICE bookings.",
    )
    custom_budget: float | None = Field(
        default=None,
        ge=0.0,
        description="Customer estimated budget for CUSTOM_SERVICE bookings.",
    )
    category_slug: str | None = Field(
        default=None,
        description="Service category slug for custom or inspection bookings.",
    )
    inspection_status: InspectionStatus | None = Field(
        default=None,
        description="Lifecycle status for INSPECTION_REQUEST bookings.",
    )
    inspection_scheduled_at: datetime | None = Field(
        default=None,
        description="Scheduled date/time for site inspection visit.",
    )
    inspection_charge: float | None = Field(
        default=None,
        ge=0.0,
        description="Diagnostic fee for inspection visit (INR).",
    )
    payment_status: str | None = Field(
        default="PENDING",
        description="Payment status: PENDING, PAID, REFUNDED, FAILED.",
    )

    # ── Customer notes ────────────────────────────────────────────────────────

    customer_notes: str | None = Field(
        default=None,
        max_length=1000,
        description=(
            "Free-text instructions or notes from the customer. "
            "Examples: 'Call before arriving', 'Gate code: 1234'."
        ),
        examples=["Please call 10 minutes before arrival."],
    )

    # ── Future Phase Stubs ────────────────────────────────────────────────────
    # Declared here to avoid schema migrations in later phases.

    worker_id: PydanticObjectId | None = Field(
        default=None,
        description="[Phase 4.4.x] WorkerProfile ObjectId — set when worker accepts.",
    )
    assigned_at: datetime | None = Field(
        default=None,
        description="[Phase 4.4.x] Timestamp when worker was assigned.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="[Phase 4.4.x] Timestamp when worker marked job as started.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="[Phase 4.4.x] Timestamp when job was completed.",
    )
    cancelled_at: datetime | None = Field(
        default=None,
        description="[Phase 4.4.1] Timestamp when booking was cancelled.",
    )
    cancellation_reason: str | None = Field(
        default=None,
        max_length=500,
        description="[Phase 4.4.1] Reason for cancellation (customer-provided).",
    )
    final_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500_000.0,
        description="[Phase 4.6] Actual price after quotation/negotiation (INR).",
    )
    inspection_id: PydanticObjectId | None = Field(
        default=None,
        description="[Phase 4.5] InspectionRequest ObjectId — set for INSPECTION_REQUEST type.",
    )
    quotation_id: PydanticObjectId | None = Field(
        default=None,
        description="[Phase 4.6] Quotation ObjectId — set after inspection/approval.",
    )
    payment_id: PydanticObjectId | None = Field(
        default=None,
        description="[Phase 4.7] Payment ObjectId — set when payment is initiated.",
    )

    # ── Job Execution & Completion (Phase 4.7.2) ──────────────────────────────

    en_route_at: datetime | None = Field(
        default=None,
        description="Timestamp when worker marked en route to location.",
    )
    arrived_at: datetime | None = Field(
        default=None,
        description="Timestamp when worker arrived at location.",
    )
    completion_notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Worker notes recorded upon job completion.",
    )
    work_summary: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional work summary submitted by worker.",
    )
    before_photos: list[str] = Field(
        default_factory=list,
        description="Cloudinary photo URLs taken before work execution.",
    )
    after_photos: list[str] = Field(
        default_factory=list,
        description="Cloudinary photo URLs taken after work completion.",
    )
    timeline: list["BookingTimelineEvent"] = Field(
        default_factory=list,
        description="Full audit trail of lifecycle timeline events.",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Booking creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp (UTC, auto-updated)",
    )

    # ── Settings ─────────────────────────────────────────────────────────────

    class Settings:
        name = "bookings"
        use_state_management = True

        indexes = [
            IndexModel(
                [("customer_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
                name="idx_customer_status_created",
            ),
            IndexModel(
                [("status", ASCENDING), ("created_at", DESCENDING)],
                name="idx_status_created",
            ),
            IndexModel([("service_location", "2dsphere")], name="service_location_2dsphere"),
            IndexModel([("service_snapshot.service_id", ASCENDING), ("status", ASCENDING)], name="service_status_idx"),
        ]

# ---------------------------------------------------------------------------
# Chat Message Document Model
# ---------------------------------------------------------------------------

class ChatMessage(Document):
    """
    Persistent chat message document model for live booking communication.

    Collection: chat_messages
    """

    booking_id: Annotated[PydanticObjectId, Indexed()]
    sender_id: Annotated[PydanticObjectId, Indexed()]
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_read: bool = False

    media_url: str | None = None
    media_type: str | None = None
    media_name: str | None = None
    media_size: int | None = None

    class Settings:
        name = "chat_messages"
        indexes = [
            IndexModel(
                [("booking_id", ASCENDING), ("timestamp", ASCENDING)],
                name="chat_booking_timestamp_idx",
            ),
        ]

    # ── Lifecycle helpers ─────────────────────────────────────────────────────

    async def save(self, *args, **kwargs):
        """Auto-update updated_at on every save."""
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)

    def __repr__(self) -> str:
        return (
            f"<Booking {self.booking_number!r} "
            f"status={self.status.value!r} "
            f"customer_id={self.customer_id}>"
        )
