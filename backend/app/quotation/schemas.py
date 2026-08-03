"""
Quotation Pydantic Schemas — DTOs for quotation creation, response serialization, and listing.
"""

from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator

from app.utils.enums import QuotationStatus


class QuotationCreateRequest(BaseModel):
    """
    Request DTO for worker creating a quotation.
    """

    booking_id: str = Field(..., description="Target booking ObjectId string")
    application_id: str = Field(..., description="Target job application ObjectId string")

    labour_cost: float = Field(default=0.0, ge=0.0, description="Labour cost (INR)")
    material_cost: float = Field(default=0.0, ge=0.0, description="Material cost (INR)")
    inspection_charge: float = Field(default=0.0, ge=0.0, description="Inspection visit charge (INR)")
    additional_charges: float = Field(default=0.0, ge=0.0, description="Additional charges (INR)")
    tax_amount: float = Field(default=0.0, ge=0.0, description="Tax amount (INR)")
    discount_amount: float = Field(default=0.0, ge=0.0, description="Discount amount (INR)")

    estimated_duration: str = Field(..., description="Estimated duration (e.g., '2 hours', '3 days')")
    validity_date: date = Field(..., description="Validity date for the quotation")
    work_start_date: date | None = Field(default=None, description="Optional proposed work start date")
    work_description: str | None = Field(default=None, description="Detailed scope of work description")
    terms_and_conditions: str | None = Field(default=None, description="Worker terms and conditions")
    notes: str | None = Field(default=None, description="Optional worker notes")
    is_draft: bool = Field(default=False, description="True to save as DRAFT, False to SUBMIT")

    @model_validator(mode="after")
    def validate_costs(self) -> "QuotationCreateRequest":
        calculated = (
            self.labour_cost
            + self.material_cost
            + self.inspection_charge
            + self.additional_charges
            + self.tax_amount
            - self.discount_amount
        )
        if calculated < 0.0:
            raise ValueError("Discount amount cannot exceed the subtotal costs")
        return self


class QuotationUpdateRequest(BaseModel):
    """
    Request DTO for worker updating an existing draft quotation.
    """

    labour_cost: float | None = Field(default=None, ge=0.0, description="Labour cost (INR)")
    material_cost: float | None = Field(default=None, ge=0.0, description="Material cost (INR)")
    inspection_charge: float | None = Field(default=None, ge=0.0, description="Inspection visit charge (INR)")
    additional_charges: float | None = Field(default=None, ge=0.0, description="Additional charges (INR)")
    tax_amount: float | None = Field(default=None, ge=0.0, description="Tax amount (INR)")
    discount_amount: float | None = Field(default=None, ge=0.0, description="Discount amount (INR)")

    estimated_duration: str | None = Field(default=None, description="Estimated duration")
    validity_date: date | None = Field(default=None, description="Validity date for the quotation")
    work_start_date: date | None = Field(default=None, description="Optional proposed work start date")
    work_description: str | None = Field(default=None, description="Detailed scope of work description")
    terms_and_conditions: str | None = Field(default=None, description="Worker terms and conditions")
    notes: str | None = Field(default=None, description="Optional worker notes")
    submit_now: bool = Field(default=False, description="Set to True to transition status from DRAFT -> SUBMITTED")


class QuotationResponse(BaseModel):
    """
    Full quotation response DTO.
    """

    id: str = Field(..., description="Quotation ObjectId string")
    quotation_number: str = Field(..., description="Unique quotation reference (e.g. QT202600001)")
    booking_id: str = Field(..., description="Booking ObjectId string")
    worker_id: str = Field(..., description="Worker user ObjectId string")
    application_id: str = Field(..., description="Job application ObjectId string")

    quotation_status: QuotationStatus = Field(..., description="Current quotation status")

    labour_cost: float = Field(..., description="Labour cost (INR)")
    material_cost: float = Field(..., description="Material cost (INR)")
    inspection_charge: float = Field(..., description="Inspection visit charge (INR)")
    additional_charges: float = Field(..., description="Additional charges (INR)")
    tax_amount: float = Field(..., description="Tax amount (INR)")
    discount_amount: float = Field(..., description="Discount amount (INR)")
    total_amount: float = Field(..., description="Calculated total amount (INR)")

    estimated_duration: str = Field(..., description="Estimated duration string")
    validity_date: date = Field(..., description="Quotation validity date")
    work_start_date: date | None = Field(default=None, description="Proposed work start date")
    work_description: str | None = Field(default=None, description="Scope of work description")
    terms_and_conditions: str | None = Field(default=None, description="Worker terms and conditions")
    notes: str | None = Field(default=None, description="Worker notes")

    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")
    submitted_at: datetime | None = Field(default=None, description="Submission timestamp (UTC)")


class QuotationPaginatedResponse(BaseModel):
    """
    Paginated list of quotations.
    """

    items: list[QuotationResponse] = Field(..., description="List of quotations")
    total: int = Field(..., description="Total count matching filters")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total available pages")


class WorkerSummaryResponse(BaseModel):
    """
    Worker profile summary included in customer quotation responses.
    """

    id: str = Field(..., description="Worker user ObjectId string")
    full_name: str = Field(..., description="Worker full name")
    profile_photo_url: str | None = Field(default=None, description="Profile picture URL")
    rating: float = Field(default=5.0, description="Worker rating")
    experience_years: float = Field(default=0.0, description="Experience in years")
    skills: list[str] = Field(default_factory=list, description="Worker registered skills")


class CustomerQuotationResponse(QuotationResponse):
    """
    Enhanced quotation DTO for customers including worker details.
    """

    worker: WorkerSummaryResponse = Field(..., description="Worker profile details")


class QuotationAcceptResponse(BaseModel):
    """
    Response returned when a customer accepts a quotation.
    """

    booking_id: str = Field(..., description="Booking ObjectId string")
    quotation_id: str = Field(..., description="Accepted quotation ObjectId string")
    worker_id: str = Field(..., description="Assigned worker ObjectId string")
    booking_status: str = Field(..., description="New booking status (e.g. accepted)")
    quotation_status: str = Field(..., description="New quotation status (accepted)")
    final_price: float = Field(..., description="Final agreed booking price (INR)")
    message: str = Field(default="Quotation accepted and worker assigned successfully.")


class AssignedWorkerResponse(BaseModel):
    """
    Assigned worker detail response for customer booking.
    """

    worker_id: str = Field(..., description="Worker user ObjectId string")
    full_name: str = Field(..., description="Worker full name")
    phone: str | None = Field(default=None, description="Worker contact phone number")
    profile_photo_url: str | None = Field(default=None, description="Profile picture URL")
    rating: float = Field(default=5.0, description="Worker average rating")
    experience_years: float = Field(default=0.0, description="Experience in years")
    skills: list[str] = Field(default_factory=list, description="Worker skills")
    assigned_at: datetime = Field(..., description="Assignment timestamp (UTC)")
    accepted_quotation: CustomerQuotationResponse = Field(..., description="Accepted quotation details")


class QuotationHistoryResponse(BaseModel):
    """
    Historical audit trail item DTO.
    """

    id: str = Field(..., description="Quotation history log ObjectId")
    quotation_id: str = Field(..., description="Quotation ObjectId")
    booking_id: str = Field(..., description="Booking ObjectId")
    worker_id: str = Field(..., description="Worker user ObjectId")
    actor_id: str = Field(..., description="Actor user ObjectId")
    actor_role: str = Field(..., description="Actor role (customer, worker, admin)")
    event_type: str = Field(..., description="Audit event type")
    previous_status: str | None = Field(default=None, description="Status prior to event")
    new_status: str = Field(..., description="Status after event")
    previous_snapshot: dict | None = Field(default=None, description="State snapshot before event")
    new_snapshot: dict = Field(..., description="State snapshot after event")
    created_at: datetime = Field(..., description="Event timestamp (UTC)")
    notes: str | None = Field(default=None, description="Event audit notes")


class QuotationHistoryPaginatedResponse(BaseModel):
    """
    Paginated response container for quotation audit logs.
    """

    items: list[QuotationHistoryResponse]
    total: int
    page: int
    page_size: int
    pages: int
