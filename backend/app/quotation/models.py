"""
Quotation Beanie ODM Document Model — domain model for worker marketplace quotations.
"""

from datetime import date, datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from app.utils.enums import QuotationEventType, QuotationStatus, UserRole


class Quotation(Document):
    """
    Independent Quotation collection model for service marketplace.

    Collection: quotations
    Relationships: Belongs to exactly one Booking, one Worker, one Job Application.
    """

    quotation_number: str = Field(
        ...,
        description="Unique quotation reference number (e.g. QT202600001)",
    )
    booking_id: PydanticObjectId = Field(..., description="Target booking ObjectId")
    worker_id: PydanticObjectId = Field(..., description="Worker user ObjectId")
    application_id: PydanticObjectId = Field(..., description="Associated job application ObjectId")

    quotation_status: QuotationStatus = Field(
        default=QuotationStatus.DRAFT,
        description="Quotation lifecycle state (DRAFT, SUBMITTED, ACCEPTED, REJECTED, EXPIRED, CANCELLED)",
    )

    labour_cost: float = Field(default=0.0, ge=0.0, description="Labour cost (INR)")
    material_cost: float = Field(default=0.0, ge=0.0, description="Material cost (INR)")
    inspection_charge: float = Field(default=0.0, ge=0.0, description="Inspection visit charge (INR)")
    additional_charges: float = Field(default=0.0, ge=0.0, description="Additional/miscellaneous charges (INR)")
    tax_amount: float = Field(default=0.0, ge=0.0, description="Tax amount (INR)")
    discount_amount: float = Field(default=0.0, ge=0.0, description="Discount amount (INR)")
    total_amount: float = Field(default=0.0, ge=0.0, description="Total cost amount (INR)")

    estimated_duration: str = Field(..., description="Estimated duration (e.g. '2 hours', '3 days')")
    validity_date: date = Field(..., description="Quotation expiration / validity date")
    work_start_date: date | None = Field(default=None, description="Optional proposed work start date")
    work_description: str | None = Field(default=None, description="Detailed scope of work description")
    terms_and_conditions: str | None = Field(default=None, description="Worker terms and conditions")
    notes: str | None = Field(default=None, description="Optional breakdown / worker notes")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    submitted_at: datetime | None = Field(
        default=None,
        description="Submission timestamp (UTC)",
    )

    class Settings:
        name = "quotations"
        use_state_management = True
        indexes = [
            IndexModel(
                [("quotation_number", 1)],
                unique=True,
            ),
            [("booking_id", 1), ("worker_id", 1)],
            [("application_id", 1)],
            [("quotation_status", 1)],
            [("booking_id", 1), ("quotation_status", 1)],
        ]

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)


class QuotationHistory(Document):
    """
    Immutable audit history log collection for quotation events.

    Collection: quotation_history
    """

    quotation_id: PydanticObjectId = Field(..., description="Target quotation ObjectId")
    booking_id: PydanticObjectId = Field(..., description="Associated booking ObjectId")
    worker_id: PydanticObjectId = Field(..., description="Worker user ObjectId")
    actor_id: PydanticObjectId = Field(..., description="User ObjectId of actor performing action")
    actor_role: UserRole = Field(..., description="Role of actor (customer, worker, admin)")

    event_type: QuotationEventType = Field(..., description="Type of audit event")
    previous_status: QuotationStatus | None = Field(default=None, description="Status prior to event")
    new_status: QuotationStatus = Field(..., description="Status after event")

    previous_snapshot: dict | None = Field(default=None, description="Snapshot of quotation state before event")
    new_snapshot: dict = Field(..., description="Snapshot of quotation state after event")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event audit timestamp (UTC)",
    )
    notes: str | None = Field(default=None, description="Optional audit notes / event context")

    class Settings:
        name = "quotation_history"
        use_state_management = True
        indexes = [
            [("quotation_id", 1), ("created_at", -1)],
            [("booking_id", 1), ("created_at", -1)],
            [("worker_id", 1), ("created_at", -1)],
            [("event_type", 1)],
        ]
