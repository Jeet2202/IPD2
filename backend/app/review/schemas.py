"""
Review Pydantic Schemas / DTOs (Phase 4.7.6).
"""

from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    """
    Payload for POST /customer/reviews — Customer submits a review for a CUSTOMER_CONFIRMED booking.
    """

    booking_id: str = Field(..., description="Booking ObjectId string")
    overall_rating: float = Field(..., ge=1.0, le=5.0, description="Overall rating (1.0 to 5.0)")
    punctuality_rating: float = Field(..., ge=1.0, le=5.0, description="Punctuality rating (1.0 to 5.0)")
    quality_rating: float = Field(..., ge=1.0, le=5.0, description="Quality rating (1.0 to 5.0)")
    professionalism_rating: float = Field(..., ge=1.0, le=5.0, description="Professionalism rating (1.0 to 5.0)")
    communication_rating: float = Field(..., ge=1.0, le=5.0, description="Communication rating (1.0 to 5.0)")

    review_title: str | None = Field(default=None, max_length=150, description="Optional title")
    review_comment: str | None = Field(default=None, max_length=2000, description="Optional feedback comment")
    would_recommend: bool = Field(default=True, description="True if customer recommends worker")
    attachments: list[str] = Field(default_factory=list, description="Attachment URLs (prepared for future uploads)")


class ReviewResponse(BaseModel):
    """
    Response DTO representing a submitted review.
    """

    id: str = Field(..., description="Review ObjectId string")
    booking_id: str = Field(..., description="Booking ObjectId string")
    worker_id: str = Field(..., description="Worker ObjectId string")
    customer_id: str = Field(..., description="Customer ObjectId string")

    overall_rating: float
    punctuality_rating: float
    quality_rating: float
    professionalism_rating: float
    communication_rating: float

    review_title: str | None = None
    review_comment: str | None = None
    would_recommend: bool = True
    attachments: list[str] = Field(default_factory=list)

    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    """
    Paginated list of reviews.
    """

    total: int = Field(..., description="Total count of reviews matching filter")
    page: int = Field(default=1, description="Page index (1-indexed)")
    page_size: int = Field(default=20, description="Items per page")
    reviews: list[ReviewResponse] = Field(default_factory=list)


class WorkerRatingSummaryResponse(BaseModel):
    """
    Aggregated rating metrics response for worker profile.
    """

    worker_id: str
    rating_average: float
    total_reviews: int
    rating_distribution: dict[int, int]
    punctuality_avg: float
    quality_avg: float
    professionalism_avg: float
    communication_avg: float
    recommendation_percentage: float
    would_recommend_count: int


class UpdateReviewStatusRequest(BaseModel):
    """
    Payload for updating review moderation status in Admin Panel.
    """

    status: str = Field(..., description="Target status: Published, Flagged, Hidden, Under Review")
    flag_reason: str | None = Field(default=None, description="Reason for flagging or hiding the review")

