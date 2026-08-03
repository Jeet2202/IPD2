"""
Marketplace FastAPI Router — worker booking discovery endpoints.

Endpoints:
    GET /api/v1/worker/marketplace           List eligible open marketplace bookings.
    GET /api/v1/worker/marketplace/{bookingId} Get sanitized booking details.
"""

from datetime import date
from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import WorkerUserDep
from app.marketplace.schemas import (
    MarketplaceBookingDetailResponse,
    MarketplacePaginatedResponse,
    MarketplaceSortOption,
)
from app.marketplace.service import MarketplaceService
from app.utils.enums import BookingType
from app.worker.models import WorkerProfile

router = APIRouter()


def get_marketplace_service() -> MarketplaceService:
    return MarketplaceService()


@router.get(
    "",
    response_model=MarketplacePaginatedResponse,
    summary="List available marketplace bookings",
    description=(
        "Returns a paginated list of open customer bookings (status=PENDING, unassigned) "
        "supporting text search, multi-filtering, and deterministic recommendation ranking. "
        "Customer PII is sanitized. Restricted to authenticated workers."
    ),
)
@router.get(
    "/",
    response_model=MarketplacePaginatedResponse,
    include_in_schema=False,
)
async def list_marketplace_bookings(
    worker: WorkerUserDep,
    query: str | None = Query(default=None, description="Free-text search by service name, category, or problem description"),
    category_slug: str | None = Query(default=None, description="Filter by service category slug"),
    booking_type: BookingType | None = Query(default=None, description="Filter by booking type"),
    scheduled_date: date | None = Query(default=None, description="Filter by preferred date (YYYY-MM-DD)"),
    min_price: float | None = Query(default=None, ge=0.0, description="Minimum estimated price (INR)"),
    max_price: float | None = Query(default=None, ge=0.0, description="Maximum estimated price (INR)"),
    city: str | None = Query(default=None, description="Filter by city name"),
    sort_by: MarketplaceSortOption = Query(default=MarketplaceSortOption.NEWEST, description="Sort order"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    service: MarketplaceService = Depends(get_marketplace_service),
) -> MarketplacePaginatedResponse:
    worker_profile = await WorkerProfile.find_one(WorkerProfile.user_id == worker.id)
    return await service.list_marketplace_bookings(
        worker_user_id=worker.id,
        worker_profile=worker_profile,
        query=query,
        category_slug=category_slug,
        booking_type=booking_type,
        scheduled_date=scheduled_date,
        min_price=min_price,
        max_price=max_price,
        city=city,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{booking_id}",
    response_model=MarketplaceBookingDetailResponse,
    summary="Get marketplace booking details",
    description=(
        "Returns detailed, sanitized information for a specific marketplace booking. "
        "Includes problem description and photos for inspection requests. Customer PII redacted."
    ),
)
async def get_marketplace_booking_detail(
    booking_id: str,
    worker: WorkerUserDep,
    service: MarketplaceService = Depends(get_marketplace_service),
) -> MarketplaceBookingDetailResponse:
    worker_profile = await WorkerProfile.find_one(WorkerProfile.user_id == worker.id)
    return await service.get_marketplace_booking_detail(
        booking_id,
        worker_user_id=worker.id,
        worker_profile=worker_profile,
    )
