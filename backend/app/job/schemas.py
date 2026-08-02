"""
Request/response schemas for the Job module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict validation for coordinates, financial amounts, and durations.
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - JobCreateRequest strictly requires the backend to map over the 
      service/inspection request details securely. The client does not dictate
      the final pricing; the backend constructs it from the origin request.
    - JobUpdateRequest manages complex execution lifecycles, ensuring that
      cancellations always include a reason and actor.
"""

from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.job.models import JobStatus, JobType, PaymentMethod, PaymentStatus


# ---------------------------------------------------------------------------
# Embedded Component Schemas
# ---------------------------------------------------------------------------

class JobAddressSchema(BaseModel):
    """
    Address schema for job execution.
    Snapshotted from the originating request.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    address_line: str = Field(..., min_length=5, max_length=500, description="Full address line")
    landmark: str | None = Field(None, max_length=200, description="Nearby landmark")
    city: str = Field(..., min_length=2, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=100, description="State name")
    pincode: str = Field(..., pattern=r"^[1-9]\d{5}$", description="6-digit Indian postal code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude (WGS84)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude (WGS84)")


class PricingSnapshotSchema(BaseModel):
    """
    Frozen financial breakdown for the job.
    Ensures amounts are strictly non-negative.
    """

    model_config = ConfigDict(from_attributes=True)

    base_price: float = Field(..., ge=0.0, description="Core service cost")
    inspection_charge: float = Field(..., ge=0.0, description="Pre-visit fee")
    worker_charge: float = Field(..., ge=0.0, description="Worker payout")
    platform_fee: float = Field(..., ge=0.0, description="Platform commission")
    tax: float = Field(..., ge=0.0, description="Tax (GST)")
    discount: float = Field(..., ge=0.0, description="Applied discount")
    final_amount: float = Field(..., ge=0.0, description="Total payable")


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class JobCreateRequest(BaseModel):
    """
    Payload to initialize a new Job from an accepted request.

    The service layer will:
        1. Validate the origin (ServiceRequest OR InspectionRequest).
        2. Ensure the origin is approved/assigned and not already converted.
        3. Extract customer, worker, category, and service IDs.
        4. Copy the address and pricing snapshots securely.
        5. Generate a unique job_number.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # Identifiers
    customer_id: str = Field(..., description="Customer ObjectId")
    worker_id: str = Field(..., description="Worker ObjectId")
    category_id: str = Field(..., description="Category ObjectId")
    service_id: str = Field(..., description="Service ObjectId")
    
    # Origin routing
    job_type: JobType = Field(..., description="NORMAL_SERVICE or INSPECTION_BASED")
    service_request_id: str | None = Field(None, description="Originating request")
    inspection_request_id: str | None = Field(None, description="Originating request")
    
    # Context
    service_address: JobAddressSchema = Field(..., description="Execution location")
    pricing_snapshot: PricingSnapshotSchema = Field(..., description="Frozen financials")
    
    scheduled_date: date = Field(..., description="Planned date")
    scheduled_time: str = Field(..., max_length=50, description="Planned time")
    estimated_duration: int = Field(..., ge=1, description="Expected duration (mins)")

    @model_validator(mode="after")
    def validate_origin(self) -> "JobCreateRequest":
        """Ensure exactly one origin is provided based on job_type."""
        if self.job_type == JobType.NORMAL_SERVICE and not self.service_request_id:
            raise ValueError("NORMAL_SERVICE requires a service_request_id")
        if self.job_type == JobType.INSPECTION_BASED and not self.inspection_request_id:
            raise ValueError("INSPECTION_BASED requires an inspection_request_id")
        return self


class JobUpdateRequest(BaseModel):
    """
    Partial update for an active job lifecycle.

    Used heavily by workers (status transitions) and the billing system
    (payment status updates).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # Execution State
    job_status: JobStatus | None = Field(None, description="Lifecycle state")
    actual_duration: int | None = Field(None, ge=1, description="Actual duration (mins)")
    
    # Context & Proof
    worker_notes: str | None = Field(None, max_length=2000, description="Worker closing remarks")
    customer_notes: str | None = Field(None, max_length=2000, description="Customer feedback")
    completion_images: list[str] | None = Field(None, max_length=10, description="Proof images")
    
    # Exceptions
    cancellation_reason: str | None = Field(None, max_length=1000, description="Cancellation context")
    cancelled_by: str | None = Field(None, description="Actor who cancelled")
    
    # Billing
    payment_status: PaymentStatus | None = Field(None, description="Invoice status")
    payment_method: PaymentMethod | None = Field(None, description="Chosen method")
    invoice_number: str | None = Field(None, min_length=3, max_length=100, description="Invoice ID")

    @model_validator(mode="after")
    def validate_cancellation(self) -> "JobUpdateRequest":
        """Enforce cancellation rules."""
        if self.job_status in [JobStatus.CANCELLED, JobStatus.FAILED]:
            if not self.cancellation_reason or not self.cancelled_by:
                raise ValueError("cancellation_reason and cancelled_by are required for terminal failure states")
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "JobUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class JobResponse(BaseModel):
    """
    Complete Job representation for API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Job ID")
    job_number: str = Field(..., description="Human-readable ID")
    
    customer_id: str = Field(..., description="Customer ID")
    worker_id: str = Field(..., description="Worker ID")
    category_id: str = Field(..., description="Category ID")
    service_id: str = Field(..., description="Service ID")
    service_request_id: str | None = Field(None, description="Origin request ID")
    inspection_request_id: str | None = Field(None, description="Origin inspection ID")
    
    service_address: JobAddressSchema = Field(..., description="Execution location")
    job_type: JobType = Field(..., description="Origin type")
    job_status: JobStatus = Field(..., description="Execution status")
    
    scheduled_date: date = Field(..., description="Planned date")
    scheduled_time: str = Field(..., description="Planned time")
    started_at: datetime | None = Field(None, description="Actual start time")
    completed_at: datetime | None = Field(None, description="Actual end time")
    cancelled_at: datetime | None = Field(None, description="Cancellation time")
    
    estimated_duration: int = Field(..., description="Expected duration (mins)")
    actual_duration: int | None = Field(None, description="Real duration (mins)")
    
    pricing_snapshot: PricingSnapshotSchema = Field(..., description="Frozen financials")
    
    worker_notes: str | None = Field(None, description="Worker remarks")
    customer_notes: str | None = Field(None, description="Customer feedback")
    completion_images: list[str] = Field(..., description="Proof images")
    customer_signature: str | None = Field(None, description="Customer sign-off URL")
    worker_signature: str | None = Field(None, description="Worker sign-off URL")
    
    cancellation_reason: str | None = Field(None, description="Cancellation context")
    cancelled_by: str | None = Field(None, description="Who cancelled")
    
    payment_status: PaymentStatus = Field(..., description="Invoice payment state")
    payment_method: PaymentMethod | None = Field(None, description="Payment method")
    invoice_number: str | None = Field(None, description="Invoice ID")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        return str(value)
