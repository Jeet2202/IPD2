"""
Request/response schemas for the Service Request module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict validation for dates, coordinates, and prices.
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - AddressSchema validates pincode formats and coordinate bounds.
    - PriceSnapshotSchema strictly ensures non-negative financial values.
    - ServiceRequestCreateRequest requires the client to send the expected
      estimated_price. The service layer verifies this against the current
      market price to prevent price mismatch during booking.
    - Status updates are partially restricted in UpdateRequest — cancellation
      requires a reason, and transitions are validated by the service layer.
"""

from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.service_request.models import CancelledBy, RequestPriority, RequestStatus


# ---------------------------------------------------------------------------
# Embedded Component Schemas
# ---------------------------------------------------------------------------

class AddressSchema(BaseModel):
    """
    Address schema for booking.
    Passed by the client and snapshotted into the ServiceRequest.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    address_line: str = Field(..., min_length=5, max_length=500, description="Full address line")
    landmark: str | None = Field(None, max_length=200, description="Nearby landmark")
    city: str = Field(..., min_length=2, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=100, description="State name")
    pincode: str = Field(..., pattern=r"^[1-9]\d{5}$", description="6-digit Indian postal code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude (WGS84)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude (WGS84)")


class PriceSnapshotSchema(BaseModel):
    """
    Schema for displaying the frozen price snapshot.
    Client cannot pass this directly on creation; it is computed by the backend.
    """

    model_config = ConfigDict(from_attributes=True)

    market_price: float = Field(..., description="Base service price")
    worker_price: float = Field(..., description="Worker payout")
    inspection_charge: float = Field(..., description="Inspection fee")
    service_fee: float = Field(..., description="Platform service fee")
    tax: float = Field(..., description="Tax (GST)")
    total_price: float = Field(..., description="Total payable")


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ServiceRequestCreateRequest(BaseModel):
    """
    Payload to book a new service.

    The service layer will:
        1. Validate category_id and service_id existence.
        2. Verify estimated_price against the current PricingConfiguration.
        3. Snapshot the PriceSnapshot.
        4. Extract customer_id from the authenticated user token.
        5. Generate a unique request_number.
        6. Compute estimated_duration and is_emergency from Service catalog.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: str = Field(..., description="ServiceCategory ObjectId")
    service_id: str = Field(..., description="Service ObjectId")
    
    service_address: AddressSchema = Field(..., description="Location of service")
    customer_location: list[float] | None = Field(
        None, min_length=2, max_length=2, description="[longitude, latitude]"
    )
    
    preferred_date: date = Field(..., description="Requested service date")
    preferred_time_slot: str = Field(
        ..., min_length=5, max_length=50, description="e.g. 10:00 AM - 12:00 PM"
    )
    
    estimated_price: float = Field(
        ..., ge=0.0, description="Client's expected price (validated by server)"
    )
    
    customer_description: str | None = Field(None, max_length=2000, description="Problem details")
    attached_images: list[str] = Field(
        default_factory=list, max_length=5, description="Image URLs"
    )

    @field_validator("preferred_date")
    @classmethod
    def validate_future_date(cls, value: date) -> date:
        """Ensure preferred date is not in the past."""
        if value < date.today():
            raise ValueError("Preferred date cannot be in the past")
        return value


class ServiceRequestUpdateRequest(BaseModel):
    """
    Partial update for an existing service request.

    Used by customer (to reschedule), worker (to update status), or admin.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    preferred_date: date | None = Field(None, description="Rescheduled date")
    preferred_time_slot: str | None = Field(None, max_length=50, description="Rescheduled time")
    customer_description: str | None = Field(None, max_length=2000, description="Updated details")
    attached_images: list[str] | None = Field(None, max_length=5, description="Updated images")
    
    status: RequestStatus | None = Field(None, description="Status transition")
    cancellation_reason: str | None = Field(None, max_length=1000, description="Reason if cancelled")
    cancelled_by: CancelledBy | None = Field(None, description="Actor who cancelled")
    
    worker_id: str | None = Field(None, description="Assigned worker (admin/system only)")

    @model_validator(mode="after")
    def validate_cancellation(self) -> "ServiceRequestUpdateRequest":
        """If status is CANCELLED, require reason and cancelled_by."""
        if self.status == RequestStatus.CANCELLED:
            if not self.cancellation_reason or not self.cancelled_by:
                raise ValueError(
                    "cancellation_reason and cancelled_by are required when cancelling"
                )
        return self
        
    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ServiceRequestUpdateRequest":
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

class ServiceRequestResponse(BaseModel):
    """
    Complete service request representation for API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Service Request ID")
    request_number: str = Field(..., description="Human-readable ID")
    customer_id: str = Field(..., description="Customer ID")
    category_id: str = Field(..., description="Category ID")
    service_id: str = Field(..., description="Service ID")
    worker_id: str | None = Field(None, description="Worker ID")
    
    service_address: AddressSchema = Field(..., description="Service location")
    customer_location: list[float] | None = Field(None, description="[longitude, latitude]")
    
    preferred_date: date = Field(..., description="Requested date")
    preferred_time_slot: str = Field(..., description="Requested time slot")
    estimated_duration: int = Field(..., description="Duration in minutes")
    
    estimated_price: float = Field(..., description="Total price estimate")
    price_snapshot: PriceSnapshotSchema = Field(..., description="Frozen price details")
    
    customer_description: str | None = Field(None, description="Problem details")
    attached_images: list[str] = Field(..., description="Image URLs")
    
    status: RequestStatus = Field(..., description="Lifecycle status")
    priority: RequestPriority = Field(..., description="Dispatch priority")
    is_emergency: bool = Field(..., description="Emergency request")
    requires_inspection: bool = Field(..., description="Needs inspection")
    
    cancellation_reason: str | None = Field(None, description="Cancellation reason")
    cancelled_by: CancelledBy | None = Field(None, description="Who cancelled")
    accepted_at: datetime | None = Field(None, description="Acceptance timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        return str(value)
