"""
Request/response schemas for the Review & Rating module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict bounds checking for multidimensional ratings (1.0 to 5.0).
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - ReviewCreateRequest accepts the target `job_id`. The backend service
      layer extracts worker_id, customer_id, service_id, and category_id
      directly from the Job document. This prevents malicious API calls from
      rating arbitrary catalog items or bypassing authorization.
    - WorkerReplyRequest isolates the worker's ability to respond to a review,
      ensuring they cannot modify the customer's actual ratings or text.
"""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ReviewCreateRequest(BaseModel):
    """
    Payload for a customer to submit a new review.

    The service layer will:
        1. Fetch the Job by `job_id`.
        2. Verify the Job status is COMPLETED.
        3. Verify the authenticated user is the `customer_id` on the Job.
        4. Verify no existing review exists for this `job_id`.
        5. Extract worker_id, category_id, and service_id from the Job.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    job_id: str = Field(..., description="Executed Job ObjectId")
    
    # --- Ratings ---
    overall_rating: float = Field(..., ge=1.0, le=5.0, description="Mandatory rating (1-5)")
    quality_rating: float | None = Field(None, ge=1.0, le=5.0, description="Work quality (1-5)")
    communication_rating: float | None = Field(None, ge=1.0, le=5.0, description="Interaction (1-5)")
    punctuality_rating: float | None = Field(None, ge=1.0, le=5.0, description="Timeliness (1-5)")
    professionalism_rating: float | None = Field(None, ge=1.0, le=5.0, description="Conduct (1-5)")
    value_for_money_rating: float | None = Field(None, ge=1.0, le=5.0, description="Cost perception (1-5)")

    # --- Content ---
    review_title: str | None = Field(None, max_length=150, description="Summary headline")
    review_comment: str | None = Field(None, max_length=3000, description="Detailed feedback")
    review_images: list[str] = Field(
        default_factory=list, max_length=5, description="Image URLs"
    )
    is_anonymous: bool = Field(default=False, description="Hide customer details")


class ReviewUpdateRequest(BaseModel):
    """
    Partial update for an existing review.
    
    Typically restricted to the customer (fixing typos) or admin (moderation).
    Workers use `WorkerReplyRequest` instead.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # --- Ratings ---
    overall_rating: float | None = Field(None, ge=1.0, le=5.0, description="Updated rating")
    quality_rating: float | None = Field(None, ge=1.0, le=5.0, description="Updated quality")
    communication_rating: float | None = Field(None, ge=1.0, le=5.0, description="Updated communication")
    punctuality_rating: float | None = Field(None, ge=1.0, le=5.0, description="Updated punctuality")
    professionalism_rating: float | None = Field(None, ge=1.0, le=5.0, description="Updated professionalism")
    value_for_money_rating: float | None = Field(None, ge=1.0, le=5.0, description="Updated value")

    # --- Content ---
    review_title: str | None = Field(None, max_length=150, description="Updated title")
    review_comment: str | None = Field(None, max_length=3000, description="Updated feedback")
    review_images: list[str] | None = Field(None, max_length=5, description="Updated images")
    is_anonymous: bool | None = Field(None, description="Updated visibility")

    # --- Moderation (Admin only) ---
    admin_flagged: bool | None = Field(None, description="Flag for moderation")
    admin_notes: str | None = Field(None, max_length=2000, description="Internal notes")

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ReviewUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


class WorkerReplyRequest(BaseModel):
    """
    Payload for a worker to publicly reply to a review.
    Ensures workers cannot tamper with the customer's rating or text.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    worker_reply: str = Field(
        ..., min_length=2, max_length=2000, description="Public response to customer"
    )


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class ReviewResponse(BaseModel):
    """
    Complete Review representation for API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Review ID")
    review_number: str = Field(..., description="Human-readable ID")
    job_id: str = Field(..., description="Associated Job ID")
    
    customer_id: str = Field(..., description="Customer ID")
    worker_id: str = Field(..., description="Worker ID")
    category_id: str = Field(..., description="Category ID")
    service_id: str = Field(..., description="Service ID")
    
    # --- Ratings ---
    overall_rating: float = Field(..., description="Primary rating")
    quality_rating: float | None = Field(None, description="Quality rating")
    communication_rating: float | None = Field(None, description="Communication rating")
    punctuality_rating: float | None = Field(None, description="Punctuality rating")
    professionalism_rating: float | None = Field(None, description="Professionalism rating")
    value_for_money_rating: float | None = Field(None, description="Value rating")
    
    # --- Content ---
    review_title: str | None = Field(None, description="Review title")
    review_comment: str | None = Field(None, description="Detailed text feedback")
    review_images: list[str] = Field(..., description="Image URLs")
    
    # --- Visibility & Moderation ---
    is_anonymous: bool = Field(..., description="Hide customer details")
    is_verified: bool = Field(..., description="Verified booking")
    admin_flagged: bool = Field(..., description="Moderation flag")
    
    # --- Worker Interaction ---
    worker_reply: str | None = Field(None, description="Worker response text")
    worker_reply_time: datetime | None = Field(None, description="Worker response time")
    
    # --- Timestamps ---
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        return str(value)
