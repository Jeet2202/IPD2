"""
Job module models — the central execution entity in KaamSetu.

Architecture:
    - Single Beanie Document: Job.
    - Embedded models: JobAddress, JobPricingSnapshot.
    - String references to all other domain entities (User, Service, Requests).

Why Job is the central entity:
    - While ServiceRequest and InspectionRequest handle the initial booking and
      negotiation phases, the `Job` is the actual execution of work.
    - A Job represents an accepted, scheduled, and actionable unit of work.
    - It consolidates both `NORMAL_SERVICE` (direct bookings) and
      `INSPECTION_BASED` (post-quotation approvals) into a single, unified pipeline.
    - Payments, invoicing, worker payouts, and dispute resolutions all anchor
      to the Job, not the preliminary requests.

Relationship strategy:
    - Uses string references (ObjectId strings) instead of Beanie Links.
    - Links to Customer, Worker, Category, and Service for denormalized analytics.
    - Optionally links back to its origin (service_request_id OR inspection_request_id)
      for auditability and lifecycle tracing.

Embedded pricing design:
    - JobPricingSnapshot freezes the final agreed-upon financial breakdown.
    - This is crucial for invoicing and worker payouts. If the global pricing
      configuration changes *during* job execution, the Job retains the exact
      amounts agreed upon at scheduling.

Embedded address design:
    - JobAddress freezes the exact service location at the time of execution.
    - If a customer deletes their profile or changes their primary address later,
      the Job history remains immutable and historically accurate.

Index strategy:
    - customer_id / worker_id: O(1) lookup for user job histories.
    - job_status + scheduled_date: Core dispatch and operational query.
    - payment_status: Financial reconciliation and automated dunning.
    - category_id / service_id: Service-level analytics and performance tracking.
    - created_at: General pagination and audit trailing.

Collection name: "jobs" (explicit, lowercase, plural).
"""

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class JobType(str, Enum):
    """Origin of the job."""
    NORMAL_SERVICE = "normal_service"
    INSPECTION_BASED = "inspection_based"


class JobStatus(str, Enum):
    """
    Execution lifecycle of the job.

    - CREATED: Job record initialized.
    - ASSIGNED: Worker confirmed for execution.
    - WORKER_ON_THE_WAY: Worker is traveling to site.
    - ARRIVED: Worker is at the customer location.
    - IN_PROGRESS: Work has actively begun.
    - PAUSED: Work temporarily halted (e.g., waiting for parts).
    - COMPLETED: Work finished successfully.
    - CANCELLED: Terminated before completion.
    - FAILED: Terminated due to inability to complete (e.g., technical failure).
    """
    CREATED = "created"
    ASSIGNED = "assigned"
    WORKER_ON_THE_WAY = "worker_on_the_way"
    ARRIVED = "arrived"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Financial status of the job."""
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    """Customer payment method."""
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"
    CASH = "cash"
    WALLET = "wallet"


# ---------------------------------------------------------------------------
# Embedded Models
# ---------------------------------------------------------------------------

class JobAddress(BaseModel):
    """
    Embedded address for job execution.
    Snapshotted from the originating request.
    """
    address_line: str = Field(..., max_length=500, description="Full address line")
    landmark: str | None = Field(None, max_length=200, description="Nearby landmark")
    city: str = Field(..., max_length=100, description="City name")
    state: str = Field(..., max_length=100, description="State name")
    pincode: str = Field(..., max_length=10, description="Postal code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude")


class JobPricingSnapshot(BaseModel):
    """
    Frozen financial breakdown for the executed job.
    Used for invoicing and payouts.
    """
    base_price: float = Field(..., ge=0.0, description="Core service cost")
    inspection_charge: float = Field(default=0.0, ge=0.0, description="Pre-visit fee")
    worker_charge: float = Field(..., ge=0.0, description="Worker payout portion")
    platform_fee: float = Field(default=0.0, ge=0.0, description="KaamSetu commission")
    tax: float = Field(default=0.0, ge=0.0, description="Calculated tax (GST)")
    discount: float = Field(default=0.0, ge=0.0, description="Applied discount")
    final_amount: float = Field(..., ge=0.0, description="Total payable by customer")


# ---------------------------------------------------------------------------
# Job Document
# ---------------------------------------------------------------------------

class Job(Document):
    """
    Central execution entity representing an active/completed service.

    Attributes:
        job_number: Human-readable unique ID (e.g., JOB-2023-XXXX).
        customer_id: Reference to Customer.
        worker_id: Reference to assigned Worker.
        category_id: Reference to ServiceCategory.
        service_id: Reference to Service.
        service_request_id: Originating request (if NORMAL_SERVICE).
        inspection_request_id: Originating request (if INSPECTION_BASED).

        service_address: Embedded location snapshot.
        job_type: Origin type.
        job_status: Current execution state.

        scheduled_date: Planned date of execution.
        scheduled_time: Planned time window.
        started_at: Actual start timestamp.
        completed_at: Actual completion timestamp.
        cancelled_at: Cancellation timestamp.

        estimated_duration: Expected minutes to complete.
        actual_duration: Real execution time in minutes.

        pricing_snapshot: Frozen financials for invoicing.

        worker_notes: Closing remarks from worker.
        customer_notes: Feedback/review context from customer.
        completion_images: Proof of work images.
        customer_signature: URL to signed approval (if required).
        worker_signature: URL to worker sign-off.

        cancellation_reason: Context if cancelled.
        cancelled_by: Actor who cancelled.

        payment_status: Invoice payment state.
        payment_method: Customer's chosen method.
        invoice_number: Generated invoice ID.
    """

    # --- Identity & References ---
    job_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Human-readable unique ID",
        examples=["JOB-1725184000-A1B2"],
    )
    customer_id: str = Field(..., description="Customer User ObjectId")
    worker_id: str = Field(..., description="Worker User ObjectId")
    category_id: str = Field(..., description="ServiceCategory ObjectId")
    service_id: str = Field(..., description="Service ObjectId")
    
    service_request_id: str | None = Field(
        default=None, description="Originating Service Request (if applicable)"
    )
    inspection_request_id: str | None = Field(
        default=None, description="Originating Inspection Request (if applicable)"
    )

    # --- Location & Type ---
    service_address: JobAddress = Field(..., description="Execution location")
    job_type: JobType = Field(..., description="Origin of the job")
    job_status: JobStatus = Field(
        default=JobStatus.CREATED, description="Execution lifecycle"
    )

    # --- Timing ---
    scheduled_date: date = Field(..., description="Planned execution date")
    scheduled_time: str = Field(..., max_length=50, description="Planned time window")
    
    started_at: datetime | None = Field(default=None, description="Actual start time")
    completed_at: datetime | None = Field(default=None, description="Actual end time")
    cancelled_at: datetime | None = Field(default=None, description="Cancellation time")
    
    estimated_duration: int = Field(..., ge=1, description="Expected duration (mins)")
    actual_duration: int | None = Field(
        default=None, ge=1, description="Real duration (mins)"
    )

    # --- Financials ---
    pricing_snapshot: JobPricingSnapshot = Field(
        ..., description="Frozen pricing for invoicing"
    )

    # --- Execution Details ---
    worker_notes: str | None = Field(
        default=None, max_length=2000, description="Worker remarks"
    )
    customer_notes: str | None = Field(
        default=None, max_length=2000, description="Customer feedback"
    )
    completion_images: list[str] = Field(
        default_factory=list, max_length=10, description="Proof of work images"
    )
    customer_signature: str | None = Field(
        default=None, max_length=512, description="Customer sign-off URL"
    )
    worker_signature: str | None = Field(
        default=None, max_length=512, description="Worker sign-off URL"
    )

    # --- Exceptions ---
    cancellation_reason: str | None = Field(
        default=None, max_length=1000, description="Cancellation context"
    )
    cancelled_by: str | None = Field(
        default=None, description="Actor who cancelled"
    )

    # --- Billing ---
    payment_status: PaymentStatus = Field(
        default=PaymentStatus.PENDING, description="Invoice payment state"
    )
    payment_method: PaymentMethod | None = Field(
        default=None, description="Chosen payment method"
    )
    invoice_number: Indexed(str, unique=True, sparse=True) | None = Field(  # type: ignore[valid-type]
        default=None, description="Generated invoice ID"
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict, description="Flexible store for AI and analytics"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "jobs"
        use_state_management = True

        indexes = [
            # Actor queries
            IndexModel([("customer_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("worker_id", ASCENDING), ("job_status", ASCENDING)]),
            
            # Operational & Dispatch
            IndexModel([("job_status", ASCENDING), ("scheduled_date", ASCENDING)]),
            IndexModel([("job_type", ASCENDING)]),
            
            # Financial & Billing
            IndexModel([("payment_status", ASCENDING)]),
            
            # Analytics
            IndexModel([("category_id", ASCENDING)]),
            IndexModel([("service_id", ASCENDING)]),
            
            # Pagination
            IndexModel([("created_at", DESCENDING)]),
        ]
