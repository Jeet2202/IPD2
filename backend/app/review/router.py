"""
Review API Router — Endpoints for ratings & reviews (Phase 4.7.6).
"""

from typing import Any
from fastapi import APIRouter, Query, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep, CustomerDep, WorkerUserDep
from app.review.admin_service import AdminReviewService
from app.review.schemas import (
    CreateReviewRequest,
    ReviewListResponse,
    ReviewResponse,
    UpdateReviewStatusRequest,
    WorkerRatingSummaryResponse,
)
from app.review.service import ReviewService

router = APIRouter(prefix="", tags=["Ratings & Reviews"])


@router.get(
    "/admin/reviews",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get all reviews for admin dashboard",
    description="Fetch paginated list of reviews stored in MongoDB with rating breakdown summary.",
)
async def get_admin_reviews(
    admin: AdminUserDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=200, description="Page size"),
    status: str | None = Query(default=None, description="Status filter"),
    rating: int | None = Query(default=None, description="Rating filter"),
    category: str | None = Query(default=None, description="Category filter"),
    search: str | None = Query(default=None, description="Search term"),
) -> dict[str, Any]:
    """Fetch reviews and ratings summary for Admin Panel from MongoDB."""
    return await AdminReviewService.get_admin_reviews(
        page=page,
        page_size=page_size,
        status=status,
        rating=rating,
        category=category,
        search=search,
    )


@router.patch(
    "/admin/reviews/{review_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update review moderation status",
    description="Update review status (Published, Hidden, Flagged, Under Review) and optional flag reason in MongoDB.",
)
async def update_review_status(
    review_id: str,
    payload: UpdateReviewStatusRequest,
    admin: AdminUserDep,
) -> dict[str, Any]:
    """Update review status in MongoDB."""
    return await AdminReviewService.update_review_status(
        review_id=review_id,
        status=payload.status,
        flag_reason=payload.flag_reason,
    )


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
