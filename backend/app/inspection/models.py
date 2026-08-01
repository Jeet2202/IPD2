"""
Inspection Request module models — handling pre-service visits and quotations.

Architecture:
    - Single Beanie Document: InspectionRequest.
    - Embedded model: InspectionAddress.
    - String references to User (customer, worker) and Catalog (category, service).

Inspection Workflow:
    - Unlike standard service requests with fixed prices, some jobs (e.g.,
      custom carpentry, deep renovation) require a physical inspection first.
    - A customer creates an InspectionRequest (paying a fixed inspection_charge).
    - A worker accepts, visits, and submits an assessment with an estimated cost.
    - If the customer approves the quotation, the system transitions this request
      and generates a full 'Job' for execution.
    - This separation isolates quotation negotiations from standard booking flows.

Why this is separate from Service Request:
    - Inspection requests have a vastly different lifecycle than direct bookings.
    - They require two distinct approvals (worker quotes, customer accepts).
    - They involve two financial transactions (inspection fee, then final job cost).
    - Merging this into ServiceRequest would bloat the core booking state machine.

Database design & Scalability:
    - Embedded Address: Snapshotted at booking to preserve historical location accuracy
      independent of future customer profile updates.
    - Optional worker_id: Allows atomic assignments using $set.
    - Future-proofing: worker_notes and reference_images support future AI-based
      damage detection and automated quotation generation.

Index strategy:
    - customer_id: O(1) lookup for a customer's active/past inspections.
    - worker_id + inspection_status: Sparse index for a worker's active pipeline.
    - inspection_status + quotation_status: Admin queue filtering.
    - service_id / category_id: Analytics grouping.
    - preferred_date: Dispatch scheduling.

Collection name: "inspection_requests" (explicit, lowercase, plural).
"""

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class InspectionStatus(str, Enum):
    """
    Lifecycle status of an inspection request.
    
    - REQUESTED: Customer created the request.
    - PENDING: System processing / awaiting broadcast.
    - ACCEPTED: Worker accepted the inspection.
    - VISIT_SCHEDULED: Worker confirmed visit time.
    - VISITED: Worker arrived at the location.
    - REPORT_SUBMITTED: Worker assessed the issue.
    - QUOTATION_SUBMITTED: Worker provided the final estimated cost.
    - CUSTOMER_APPROVED: Customer accepted the quotation.
    - CUSTOMER_REJECTED: Customer declined the quotation.
    - JOB_CREATED: System converted the approved inspection into an active Job.
    - CANCELLED: Request aborted before completion.
    """

    REQUESTED = "requested"
    PENDING = "pending"
    ACCEPTED = "accepted"
    VISIT_SCHEDULED = "visit_scheduled"
    VISITED = "visited"
    REPORT_SUBMITTED = "report_submitted"
    QUOTATION_SUBMITTED = "quotation_submitted"
    CUSTOMER_APPROVED = "customer_approved"
    CUSTOMER_REJECTED = "customer_rejected"
    JOB_CREATED = "job_created"
    CANCELLED = "cancelled"


class QuotationStatus(str, Enum):
    """Status of the financial quotation resulting from the inspection."""

    NOT_GENERATED = "not_generated"
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Embedded Models
# ---------------------------------------------------------------------------

class InspectionAddress(BaseModel):
    """
    Embedded address for an inspection request.
    Snapshotted from the customer's profile to preserve historical accuracy.
    """

    address_line: str = Field(..., max_length=500, description="Full address line")
    landmark: str | None = Field(None, max_length=200, description="Nearby landmark")
    city: str = Field(..., max_length=100, description="City name")
    state: str = Field(..., max_length=100, description="State name")
    pincode: str = Field(..., max_length=10, description="Postal code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


# ---------------------------------------------------------------------------
# Inspection Request Document
# ---------------------------------------------------------------------------

class InspectionRequest(Document):
    """
    Pre-service site visit and assessment request.

    Used when a service requires physical inspection before a final quote
    can be provided (e.g., custom plumbing, heavy appliance repair).

    Attributes:
        inspection_request_number: Human-readable unique ID (e.g., INSP-1234).
        customer_id: Reference to Customer user_id.
        category_id: Reference to ServiceCategory.
        service_id: Reference to Service.
        worker_id: Reference to assigned Worker (optional until accepted).

        address: Embedded snapshot of the inspection address.
        customer_location: [longitude, latitude] of device at booking.
        problem_description: Issue details provided by customer.
        reference_images: Uploaded image URLs for initial context.

        preferred_date: Requested date of inspection.
        preferred_time_slot: Requested time window.

        inspection_charge: The fixed fee charged for the visit itself.
        inspection_status: Current lifecycle state.
        quotation_status: State of the post-visit quotation.

        worker_notes: Assessment details added by worker during/after visit.
        customer_notes: Feedback/comments from the customer regarding the quote.
        worker_estimated_cost: The quoted price provided by the worker.

        customer_approved: True if customer accepted the quotation.
        customer_rejected: True if customer declined the quotation.

        approval_time: Timestamp when customer made their decision.
        completed_time: Timestamp when inspection flow concluded (Job created or rejected).
    """

    # --- Identity & References ---
    inspection_request_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Human-readable unique ID",
        examples=["INSP-1725184000-A1B2"],
    )
    customer_id: str = Field(..., description="Customer User ObjectId")
    category_id: str = Field(..., description="ServiceCategory ObjectId")
    service_id: str = Field(..., description="Service ObjectId")
    worker_id: str | None = Field(
        default=None, description="Assigned Worker User ObjectId"
    )

    # --- Location & Context ---
    address: InspectionAddress = Field(
        ..., description="Embedded snapshot of the inspection address"
    )
    customer_location: list[float] | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="[longitude, latitude] of customer device at booking",
    )
    problem_description: str | None = Field(
        default=None, max_length=2000, description="Problem details from customer"
    )
    reference_images: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Initial images provided by customer (Cloudinary/S3)",
    )

    # --- Timing ---
    preferred_date: date = Field(..., description="Requested inspection date")
    preferred_time_slot: str = Field(
        ..., max_length=50, description="Requested time window (e.g., 10 AM - 12 PM)"
    )

    # --- Financial & State ---
    inspection_charge: float = Field(
        ..., ge=0.0, description="Fixed fee for the inspection visit"
    )
    inspection_status: InspectionStatus = Field(
        default=InspectionStatus.REQUESTED, description="Lifecycle status"
    )
    quotation_status: QuotationStatus = Field(
        default=QuotationStatus.NOT_GENERATED, description="State of the quotation"
    )

    # --- Assessment Details ---
    worker_notes: str | None = Field(
        default=None, max_length=3000, description="Worker's post-inspection report"
    )
    customer_notes: str | None = Field(
        default=None, max_length=1000, description="Customer's reply to the quote"
    )
    worker_estimated_cost: float | None = Field(
        default=None, ge=0.0, description="Final quoted price by worker"
    )

    # --- Approvals ---
    customer_approved: bool = Field(
        default=False, description="True if customer accepted the quote"
    )
    customer_rejected: bool = Field(
        default=False, description="True if customer declined the quote"
    )
    approval_time: datetime | None = Field(
        default=None, description="Timestamp of customer decision"
    )
    completed_time: datetime | None = Field(
        default=None, description="Timestamp of flow conclusion"
    )

    # --- Extensibility & Timestamps ---
    metadata: dict = Field(
        default_factory=dict, description="Flexible key-value store for future features"
    )
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
        name = "inspection_requests"
        use_state_management = True

        indexes = [
            # Customer history
            IndexModel([("customer_id", ASCENDING), ("created_at", DESCENDING)]),
            # Worker assignments (sparse for non-assigned requests)
            IndexModel(
                [("worker_id", ASCENDING), ("inspection_status", ASCENDING)],
                sparse=True,
            ),
            # Service / Category analytics
            IndexModel([("service_id", ASCENDING)]),
            IndexModel([("category_id", ASCENDING)]),
            # Admin queue filtering & reporting
            IndexModel(
                [("inspection_status", ASCENDING), ("quotation_status", ASCENDING)]
            ),
            # Scheduling queries
            IndexModel([("preferred_date", ASCENDING), ("inspection_status", ASCENDING)]),
            # Pagination
            IndexModel([("created_at", DESCENDING)]),
        ]
