"""
Review Service — Business logic for review creation, validation, and incremental worker profile metric aggregation (Phase 4.7.6).
"""

from datetime import datetime, timezone
import logging
from beanie import PydanticObjectId

from app.auth.models import User
from app.booking.models import Booking
from app.booking.repository import BookingRepository
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.review.models import Review
from app.review.repository import ReviewRepository
from app.review.schemas import (
    CreateReviewRequest,
    ReviewListResponse,
    ReviewResponse,
    WorkerRatingSummaryResponse,
)
from app.utils.enums import BookingStatus
from app.worker.models import WorkerProfile

logger = logging.getLogger("ally.review")


def _to_response(review: Review) -> ReviewResponse:
    """Helper to convert Review model to response DTO."""
    return ReviewResponse(
        id=str(review.id),
        booking_id=str(review.booking_id),
        worker_id=str(review.worker_id),
        customer_id=str(review.customer_id),
        overall_rating=review.overall_rating,
        punctuality_rating=review.punctuality_rating,
        quality_rating=review.quality_rating,
        professionalism_rating=review.professionalism_rating,
        communication_rating=review.communication_rating,
        review_title=review.review_title,
        review_comment=review.review_comment,
        would_recommend=review.would_recommend,
        attachments=review.attachments or [],
        created_at=review.created_at.isoformat() if review.created_at else "",
        updated_at=review.updated_at.isoformat() if review.updated_at else "",
    )


class ReviewService:
    """Service handling business rules, validation, and worker aggregate updates for reviews."""

    @classmethod
    async def create_review(
        cls,
        customer_user: User,
        payload: CreateReviewRequest,
    ) -> ReviewResponse:
        """
        Customer submits a review for a completed (CUSTOMER_CONFIRMED) booking.

        Rules:
            1. Booking must exist.
            2. Customer must be the booking owner.
            3. Booking status MUST be CUSTOMER_CONFIRMED or COMPLETED.
            4. Booking must have an assigned worker.
            5. Only ONE review per booking.
            6. Ratings must be between 1.0 and 5.0.
            7. Incrementally updates WorkerProfile rating aggregates.
        """

        if not PydanticObjectId.is_valid(payload.booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{payload.booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(payload.booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # 1. Ownership check
        if str(booking.customer_id) != str(customer_user.id):
            raise ForbiddenException(
                message="You are not authorized to submit a review for this booking.",
                error_code="BOOKING_ACCESS_DENIED",
            )

        # 2. Lifecycle status check
        if booking.status not in (BookingStatus.CUSTOMER_CONFIRMED, BookingStatus.COMPLETED):
            raise BadRequestException(
                message=f"Reviews can only be submitted for completed bookings (Current status: '{booking.status.value}').",
                error_code="BOOKING_NOT_CONFIRMED",
            )

        # 3. Assigned worker check
        if booking.worker_id is None:
            raise BadRequestException(
                message="Booking has no assigned worker.",
                error_code="WORKER_NOT_ASSIGNED",
            )

        # 4. Duplicate check
        existing = await ReviewRepository.get_by_booking_id(booking.id)
        if existing is not None:
            raise BadRequestException(
                message="A review has already been submitted for this booking.",
                error_code="DUPLICATE_REVIEW",
            )

        # 5. Create & Save Review
        review = Review(
            booking_id=booking.id,
            job_id=booking.id,
            worker_id=booking.worker_id,
            customer_id=customer_user.id,
            overall_rating=round(float(payload.overall_rating), 2),
            punctuality_rating=round(float(payload.punctuality_rating), 2),
            quality_rating=round(float(payload.quality_rating), 2),
            professionalism_rating=round(float(payload.professionalism_rating), 2),
            communication_rating=round(float(payload.communication_rating), 2),
            review_title=payload.review_title.strip() if payload.review_title else None,
            review_comment=payload.review_comment.strip() if payload.review_comment else None,
            would_recommend=payload.would_recommend,
            attachments=payload.attachments or [],
            created_at=datetime.now(timezone.utc),
        )

        review = await ReviewRepository.create(review)

        # 6. Incrementally Update Worker Profile Rating Metrics
        await cls._update_worker_metrics_incrementally(booking.worker_id, review)

        logger.info(
            "Review created: id=%s booking_id=%s worker_id=%s overall=%.1f",
            review.id,
            review.booking_id,
            review.worker_id,
            review.overall_rating,
        )
        return _to_response(review)

    @classmethod
    async def get_review_by_booking(
        cls,
        user: User,
        booking_id: str,
    ) -> ReviewResponse:
        """
        Fetch review details for a specific booking.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        is_owner = str(booking.customer_id) == str(user.id)
        is_worker = booking.worker_id and str(booking.worker_id) == str(user.id)
        is_admin = user.role == "admin"
        if not (is_owner or is_worker or is_admin):
            raise ForbiddenException(
                message="You are not authorized to view the review for this booking.",
                error_code="BOOKING_ACCESS_DENIED",
            )

        review = await ReviewRepository.get_by_booking_id(booking.id)
        if review is None:
            raise NotFoundException(
                message="Review not found for this booking.",
                error_code="REVIEW_NOT_FOUND",
            )

        return _to_response(review)

    @classmethod
    async def get_worker_reviews(
        cls,
        worker_user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> ReviewListResponse:
        """
        Fetch paginated list of reviews for a given worker.
        """
        if not PydanticObjectId.is_valid(worker_user_id):
            raise BadRequestException(
                message=f"Invalid worker ID format '{worker_user_id}'",
                error_code="INVALID_WORKER_ID",
            )

        worker_obj_id = PydanticObjectId(worker_user_id)
        skip = (page - 1) * page_size
        reviews = await ReviewRepository.list_by_worker(worker_obj_id, skip=skip, limit=page_size)
        total = await ReviewRepository.count_by_worker(worker_obj_id)

        dtos = [_to_response(r) for r in reviews]
        return ReviewListResponse(
            total=total,
            page=page,
            page_size=page_size,
            reviews=dtos,
        )

    @classmethod
    async def _update_worker_metrics_incrementally(
        cls,
        worker_id: PydanticObjectId,
        review: Review,
    ) -> None:
        """
        Calculates and saves incremental weighted averages on WorkerProfile.
        O(1) complexity — avoids full review collection scans.
        """
        profile = await WorkerProfile.find_one(WorkerProfile.user_id == worker_id)
        if profile is None:
            return

        old_count = profile.total_reviews or profile.review_count or 0
        new_count = old_count + 1

        # Incremental rolling average formulas
        profile.rating_average = round(((profile.rating_average * old_count) + review.overall_rating) / new_count, 2)
        profile.punctuality_avg = round(((profile.punctuality_avg * old_count) + review.punctuality_rating) / new_count, 2)
        profile.quality_avg = round(((profile.quality_avg * old_count) + review.quality_rating) / new_count, 2)
        profile.professionalism_avg = round(((profile.professionalism_avg * old_count) + review.professionalism_rating) / new_count, 2)
        profile.communication_avg = round(((profile.communication_avg * old_count) + review.communication_rating) / new_count, 2)

        # Sync legacy fields for backwards compatibility
        profile.rating = profile.rating_average
        profile.review_count = new_count
        profile.total_reviews = new_count

        # Rating frequency distribution update
        star = int(round(review.overall_rating))
        star = max(1, min(5, star))
        if profile.rating_distribution is None:
            profile.rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        # Convert string keys to int if necessary
        dist = {int(k): v for k, v in profile.rating_distribution.items()}
        dist[star] = dist.get(star, 0) + 1
        profile.rating_distribution = dist

        # Recommendation percentage tracking
        if review.would_recommend:
            profile.would_recommend_count = (profile.would_recommend_count or 0) + 1
        else:
            profile.would_recommend_count = profile.would_recommend_count or 0

        profile.recommendation_percentage = round((profile.would_recommend_count / new_count) * 100.0, 1)

        await profile.save()
        logger.info(
            "Worker profile metrics updated incrementally: worker_id=%s new_total=%d avg=%.2f",
            worker_id,
            new_count,
            profile.rating_average,
        )
