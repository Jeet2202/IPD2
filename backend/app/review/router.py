"""
Review API Router — Endpoints for ratings & reviews (Phase 4.7.6).
"""

from fastapi import APIRouter, Query, status

from app.auth.dependencies import ActiveUserDep, CustomerDep, WorkerUserDep
from app.review.schemas import (
    CreateReviewRequest,
    ReviewListResponse,
    ReviewResponse,
    WorkerRatingSummaryResponse,
)
from app.review.service import ReviewService

router = APIRouter(prefix="", tags=["Ratings & Reviews"])


@router.post(
    "/customer/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit customer review for completed booking",
    description="Customer submits category ratings (1-5), title, comment, and recommendation toggle for a CUSTOMER_CONFIRMED booking.",
)
async def create_review(
    payload: CreateReviewRequest,
    current_user: CustomerDep,
) -> ReviewResponse:
    """Customer submits review for completed booking."""
    return await ReviewService.create_review(current_user, payload)


@router.get(
    "/customer/reviews/{booking_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get review submitted for a booking",
    description="Fetch review details for a specific booking ID.",
)
async def get_review_by_booking(
    booking_id: str,
    current_user: ActiveUserDep,
) -> ReviewResponse:
    """Fetch review for a specific booking."""
    return await ReviewService.get_review_by_booking(current_user, booking_id)


@router.get(
    "/worker/reviews",
    response_model=ReviewListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated worker's reviews",
    description="Fetch paginated list of reviews submitted for the authenticated worker.",
)
async def get_my_worker_reviews(
    current_user: WorkerUserDep,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> ReviewListResponse:
    """Authenticated worker fetches their own reviews."""
    return await ReviewService.get_worker_reviews(
        worker_user_id=str(current_user.id),
        page=page,
        page_size=page_size,
    )


@router.get(
    "/worker/reviews/{worker_id}",
    response_model=ReviewListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get public reviews for a worker",
    description="Fetch paginated list of customer reviews for a given worker ID.",
)
async def get_public_worker_reviews(
    worker_id: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> ReviewListResponse:
    """Public lookup of reviews for a worker."""
    return await ReviewService.get_worker_reviews(
        worker_user_id=worker_id,
        page=page,
        page_size=page_size,
    )
