"""
Request/response schemas for the Inspection Request module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict validation for dates, coordinates, and pricing.
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - InspectionAddressSchema ensures valid pincodes and coordinate bounds.
    - InspectionRequestCreateRequest sets the initial expectations (address,
      date, problem description). The service layer injects the inspection_charge
      based on current pricing configurations to prevent spoofing.
    - Status transitions and approvals are managed via the Update schema,
      where the service layer validates state machine rules (e.g., worker cannot
      submit quotation if not VISITED).
"""

from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.inspection.models import InspectionStatus, QuotationStatus


# ---------------------------------------------------------------------------
# Embedded Component Schemas
# ---------------------------------------------------------------------------

class InspectionAddressSchema(BaseModel):
    """
    Address schema for an inspection.
    Passed by the client and snapshotted into the InspectionRequest.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    address_line: str = Field(..., min_length=5, max_length=500, description="Full address line")
    landmark: str | None = Field(None, max_length=200, description="Nearby landmark")
    city: str = Field(..., min_length=2, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=100, description="State name")
    pincode: str = Field(..., pattern=r"^[1-9]\d{5}$", description="6-digit Indian postal code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude (WGS84)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude (WGS84)")


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class InspectionRequestCreateRequest(BaseModel):
    """
    Payload to book a new physical inspection.

    The service layer will:
        1. Validate category_id and service_id existence.
        2. Verify that this service actually requires an inspection.
        3. Extract customer_id from the authenticated user token.
        4. Generate a unique inspection_request_number.
        5. Fetch the `inspection_charge` from PricingConfiguration and lock it in.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: str = Field(..., description="ServiceCategory ObjectId")
    service_id: str = Field(..., description="Service ObjectId")
    
    address: InspectionAddressSchema = Field(..., description="Location for inspection")
    customer_location: list[float] | None = Field(
        None, min_length=2, max_length=2, description="[longitude, latitude]"
    )
    
    preferred_date: date = Field(..., description="Requested inspection date")
    preferred_time_slot: str = Field(
        ..., min_length=5, max_length=50, description="e.g. 10:00 AM - 12:00 PM"
    )
    
    problem_description: str | None = Field(
        None, max_length=2000, description="Customer-provided context"
    )
    reference_images: list[str] = Field(
        default_factory=list, max_length=10, description="Image URLs"
    )
    
    # NOTE: `inspection_charge` is NOT provided here by the client. It is determined
    # by the backend service layer based on the pricing module to prevent fraud.

    @field_validator("preferred_date")
    @classmethod
    def validate_future_date(cls, value: date) -> date:
        """Ensure preferred date is not in the past."""
        if value < date.today():
            raise ValueError("Preferred date cannot be in the past")
        return value


class InspectionRequestUpdateRequest(BaseModel):
    """
    Partial update for an existing inspection request.

    Used by:
      - Worker (to submit notes and estimated_cost).
      - Customer (to reschedule, approve/reject quotation).
      - Admin (override).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # Customer updates
    preferred_date: date | None = Field(None, description="Rescheduled date")
    preferred_time_slot: str | None = Field(None, max_length=50, description="Rescheduled time")
    problem_description: str | None = Field(None, max_length=2000, description="Updated details")
    reference_images: list[str] | None = Field(None, max_length=10, description="Updated images")
    
    customer_notes: str | None = Field(None, max_length=1000, description="Feedback on quote")
    customer_approved: bool | None = Field(None, description="Accept the quotation")
    customer_rejected: bool | None = Field(None, description="Decline the quotation")
    
    # Worker updates
    worker_notes: str | None = Field(None, max_length=3000, description="Worker's assessment")
    worker_estimated_cost: float | None = Field(
        None, ge=0.0, description="Quoted cost after inspection"
    )

    # State transitions
    inspection_status: InspectionStatus | None = Field(None, description="Lifecycle status")
    quotation_status: QuotationStatus | None = Field(None, description="Quotation state")
    
    # Admin updates
    worker_id: str | None = Field(None, description="Reassign worker")

    @model_validator(mode="after")
    def validate_approval_conflict(self) -> "InspectionRequestUpdateRequest":
        """Ensure a quotation isn't simultaneously approved and rejected."""
        if self.customer_approved and self.customer_rejected:
            raise ValueError("Cannot simultaneously approve and reject a quotation")
        return self
        
    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "InspectionRequestUpdateRequest":
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

class InspectionRequestResponse(BaseModel):
    """
    Complete inspection request representation for API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Inspection Request ID")
    inspection_request_number: str = Field(..., description="Human-readable ID")
    customer_id: str = Field(..., description="Customer ID")
    category_id: str = Field(..., description="Category ID")
    service_id: str = Field(..., description="Service ID")
    worker_id: str | None = Field(None, description="Worker ID")
    
    address: InspectionAddressSchema = Field(..., description="Inspection location")
    customer_location: list[float] | None = Field(None, description="[longitude, latitude]")
    
    problem_description: str | None = Field(None, description="Customer context")
    reference_images: list[str] = Field(..., description="Initial image URLs")
    
    preferred_date: date = Field(..., description="Requested date")
    preferred_time_slot: str = Field(..., description="Requested time slot")
    
    inspection_charge: float = Field(..., description="Fee charged for visit")
    inspection_status: InspectionStatus = Field(..., description="Lifecycle status")
    quotation_status: QuotationStatus = Field(..., description="Quotation state")
    
    worker_notes: str | None = Field(None, description="Worker assessment")
    customer_notes: str | None = Field(None, description="Customer reply")
    worker_estimated_cost: float | None = Field(None, description="Quoted price")
    
    customer_approved: bool = Field(..., description="Quote accepted")
    customer_rejected: bool = Field(..., description="Quote declined")
    
    approval_time: datetime | None = Field(None, description="Decision timestamp")
    completed_time: datetime | None = Field(None, description="Completion timestamp")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        return str(value)
