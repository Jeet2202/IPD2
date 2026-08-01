"""
Review & Rating module models — handling customer feedback and worker reputation.

Architecture:
    - Single Beanie Document: Review.
    - Zero embedded models; everything is flattened for high-performance aggregations.
    - String references to User (customer, worker), Catalog (category, service), and Job.

Relationship strategy:
    - 1:1 mapping with Job. A Job can only have one Review. The service layer
      must enforce this uniqueness constraint before creation.
    - String references (ObjectId strings) decouple the Review from User/Catalog
      models, preventing Beanie Link lazy loading overhead.
    - Denormalized category_id and service_id allow rapid querying of "average
      rating for Plumbing Services" without joining the Job collection.

Rating architecture:
    - Multidimensional rating system (1-5 scale).
    - `overall_rating` is mandatory.
    - Sub-ratings (quality, communication, punctuality, professionalism, value)
      are optional to reduce friction for the customer, but provide deep
      analytics when filled out.

Analytics considerations:
    - Flattened numeric fields enable ultra-fast MongoDB $avg and $group operations.
    - Aggregation pipelines can instantly compute a worker's reputation score
      over the last 30 days using `worker_id` + `created_at`.
    - `is_verified` distinguishes between genuine booking reviews and potential
      imported/legacy reviews.

Index strategy:
    - job_id: Unique index to strictly enforce 1 review per job at the database level.
    - worker_id + created_at: Core index for worker reputation dashboards and ranking.
    - customer_id: O(1) lookup for a customer's review history.
    - category_id / service_id: O(1) lookup for catalog analytics.
    - overall_rating: Filtering (e.g., "show only 5-star reviews").

Collection name: "reviews" (explicit, lowercase, plural).
"""

from datetime import datetime, timezone

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Review Document
# ---------------------------------------------------------------------------

class Review(Document):
    """
    Customer review and rating for a completed Job.

    Attributes:
        review_number: Human-readable unique ID (e.g., REV-2023-XXXX).
        job_id: Reference to the executed Job.
        customer_id: Reference to Customer who wrote the review.
        worker_id: Reference to Worker who executed the job.
        category_id: Reference to ServiceCategory (denormalized from Job).
        service_id: Reference to Service (denormalized from Job).

        overall_rating: Primary score (1.0 to 5.0).
        quality_rating: Specific rating for work quality.
        communication_rating: Specific rating for worker interaction.
        punctuality_rating: Specific rating for timeliness.
        professionalism_rating: Specific rating for conduct.
        value_for_money_rating: Specific rating for cost perception.

        review_title: Short summary headline.
        review_comment: Detailed customer feedback.
        review_images: Proof or visual context uploaded by customer.

        is_anonymous: If True, hide customer details in public views.
        is_verified: True if attached to a completed platform Job.

        worker_reply: Public response from the worker.
        worker_reply_time: Timestamp of the worker's response.

        admin_flagged: True if flagged for moderation (spam/abuse).
        admin_notes: Internal context from moderation team.

        metadata: Flexible store for AI sentiment, spam scores, etc.
    """

    # --- Identity & References ---
    review_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Human-readable unique ID",
        examples=["REV-1725184000-A1B2"],
    )
    job_id: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Reference to executed Job (1 Review per Job)",
    )
    customer_id: str = Field(..., description="Customer User ObjectId")
    worker_id: str = Field(..., description="Worker User ObjectId")
    category_id: str = Field(..., description="ServiceCategory ObjectId")
    service_id: str = Field(..., description="Service ObjectId")

    # --- Multidimensional Ratings (1.0 to 5.0) ---
    overall_rating: float = Field(
        ..., ge=1.0, le=5.0, description="Mandatory primary rating"
    )
    quality_rating: float | None = Field(
        default=None, ge=1.0, le=5.0, description="Work quality"
    )
    communication_rating: float | None = Field(
        default=None, ge=1.0, le=5.0, description="Worker interaction"
    )
    punctuality_rating: float | None = Field(
        default=None, ge=1.0, le=5.0, description="Timeliness"
    )
    professionalism_rating: float | None = Field(
        default=None, ge=1.0, le=5.0, description="Conduct"
    )
    value_for_money_rating: float | None = Field(
        default=None, ge=1.0, le=5.0, description="Cost perception"
    )

    # --- Text & Media ---
    review_title: str | None = Field(
        default=None, max_length=150, description="Short summary headline"
    )
    review_comment: str | None = Field(
        default=None, max_length=3000, description="Detailed text feedback"
    )
    review_images: list[str] = Field(
        default_factory=list, max_length=5, description="Uploaded images"
    )

    # --- Visibility & Moderation ---
    is_anonymous: bool = Field(
        default=False, description="Hide customer details publicly"
    )
    is_verified: bool = Field(
        default=True, description="True if tied to a completed KaamSetu Job"
    )
    admin_flagged: bool = Field(
        default=False, description="Flagged for moderation"
    )
    admin_notes: str | None = Field(
        default=None, max_length=2000, description="Internal moderation notes"
    )

    # --- Worker Interaction ---
    worker_reply: str | None = Field(
        default=None, max_length=2000, description="Public response from worker"
    )
    worker_reply_time: datetime | None = Field(
        default=None, description="Timestamp of worker response"
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict, description="Flexible store for AI sentiment, trust scores"
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
        name = "reviews"
        use_state_management = True

        indexes = [
            # Note: job_id unique index is defined directly on the field.
            
            # Reputation & Worker Analytics
            IndexModel([("worker_id", ASCENDING), ("created_at", DESCENDING)]),
            
            # Customer History
            IndexModel([("customer_id", ASCENDING), ("created_at", DESCENDING)]),
            
            # Service & Category Analytics
            IndexModel([("category_id", ASCENDING), ("overall_rating", DESCENDING)]),
            IndexModel([("service_id", ASCENDING), ("overall_rating", DESCENDING)]),
            
            # General Filtering & Pagination
            IndexModel([("overall_rating", DESCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
