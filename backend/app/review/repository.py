"""
Review Repository — Database access layer for reviews (Phase 4.7.6).
"""

from beanie import PydanticObjectId
from app.review.models import Review


class ReviewRepository:
    """Repository handling CRUD operations for Review documents."""

    @classmethod
    async def create(cls, review: Review) -> Review:
        """Persist new Review document."""
        return await review.insert()

    @classmethod
    async def get_by_id(cls, review_id: str | PydanticObjectId) -> Review | None:
        """Fetch review by ID."""
        if isinstance(review_id, str):
            if not PydanticObjectId.is_valid(review_id):
                return None
            review_id = PydanticObjectId(review_id)
        return await Review.get(review_id)

    @classmethod
    async def get_by_booking_id(cls, booking_id: str | PydanticObjectId) -> Review | None:
        """Fetch single review by booking_id."""
        if isinstance(booking_id, str):
            if not PydanticObjectId.is_valid(booking_id):
                return None
            booking_id = PydanticObjectId(booking_id)
        return await Review.find_one(Review.booking_id == booking_id)

    @classmethod
    async def list_by_worker(
        cls,
        worker_id: str | PydanticObjectId,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Review]:
        """Fetch paginated reviews for worker, sorted by created_at descending."""
        if isinstance(worker_id, str):
            if not PydanticObjectId.is_valid(worker_id):
                return []
            worker_id = PydanticObjectId(worker_id)
        return (
            await Review.find(Review.worker_id == worker_id)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @classmethod
    async def count_by_worker(cls, worker_id: str | PydanticObjectId) -> int:
        """Count total reviews for worker."""
        if isinstance(worker_id, str):
            if not PydanticObjectId.is_valid(worker_id):
                return 0
            worker_id = PydanticObjectId(worker_id)
        return await Review.find(Review.worker_id == worker_id).count()
