"""
Marketplace Service — business logic for worker marketplace booking discovery.

Rules:
    - Pure business logic layer: transforms raw Booking models to marketplace DTOs.
    - Strictly redacts customer PII (full name, phone, detailed street address).
    - Enforces pagination constraints and valid parameters.
"""

import math
from datetime import date

from beanie import PydanticObjectId

from app.application.models import JobApplication
from app.booking.models import Booking
from app.core.exceptions import BadRequestException, NotFoundException
from app.marketplace.recommendation.engine import RecommendationEngine
from app.marketplace.repository import MarketplaceRepository
from app.marketplace.rules import MarketplaceRulesEngine
from app.marketplace.schemas import (
    MarketplaceAddressResponse,
    MarketplaceBookingDetailResponse,
    MarketplaceBookingItemResponse,
    MarketplacePaginatedResponse,
    MarketplaceSortOption,
)
from app.utils.enums import BookingType
from app.worker.models import WorkerProfile


class MarketplaceService:
    """Business logic for worker marketplace discovery and recommendations."""

    def __init__(
        self,
        repo: MarketplaceRepository | None = None,
        recommendation_engine: RecommendationEngine | None = None,
    ) -> None:
        self.repo = repo or MarketplaceRepository()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    def _build_sanitized_address(self, booking: Booking) -> MarketplaceAddressResponse:
        """
        Extract sanitized approximate location from booking snapshot and location.
        Strips customer name, phone, address lines, and landmark.
        """
        snapshot = booking.address_snapshot
        lat: float | None = None
        lng: float | None = None

        if booking.service_location and booking.service_location.coordinates:
            lng = booking.service_location.longitude
            lat = booking.service_location.latitude
        elif snapshot.location and snapshot.location.coordinates:
            lng = snapshot.location.longitude
            lat = snapshot.location.latitude

        return MarketplaceAddressResponse(
            city=snapshot.city,
            state=snapshot.state,
            postal_code=snapshot.postal_code,
            latitude=lat,
            longitude=lng,
        )

    def _to_item_response(
        self,
        booking: Booking,
        worker_profile: WorkerProfile | None = None,
        has_applied: bool = False,
    ) -> MarketplaceBookingItemResponse:
        """Map a Booking model to a sanitized summary item DTO with distance & recommendation flags."""
        sanitized_addr = self._build_sanitized_address(booking)
        _, dist_km, is_rec = self.recommendation_engine.score_booking(booking, worker_profile)

        return MarketplaceBookingItemResponse(
            id=str(booking.id),
            booking_number=booking.booking_number,
            booking_type=booking.booking_type,
            status=booking.status,
            service_snapshot=booking.service_snapshot,
            address=sanitized_addr,
            scheduled_date=booking.scheduled_date,
            scheduled_time=booking.scheduled_time,
            estimated_price=booking.estimated_price,
            estimated_duration_minutes=booking.estimated_duration_minutes,
            distance_km=dist_km,
            is_recommended=is_rec,
            has_applied=has_applied,
            created_at=booking.created_at,
        )

    def _to_detail_response(
        self,
        booking: Booking,
        worker_profile: WorkerProfile | None = None,
        has_applied: bool = False,
    ) -> MarketplaceBookingDetailResponse:
        """Map a Booking model to a sanitized detail DTO."""
        item = self._to_item_response(booking, worker_profile, has_applied=has_applied)
        return MarketplaceBookingDetailResponse(
            **item.model_dump(),
            problem_description=booking.problem_description,
            problem_photos=booking.problem_photos,
        )

    async def list_marketplace_bookings(
        self,
        *,
        worker_user_id: str | PydanticObjectId | None = None,
        worker_profile: WorkerProfile | None = None,
        query: str | None = None,
        category_slug: str | None = None,
        booking_type: BookingType | None = None,
        scheduled_date: date | str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        city: str | None = None,
        sort_by: MarketplaceSortOption = MarketplaceSortOption.NEWEST,
        page: int = 1,
        page_size: int = 20,
    ) -> MarketplacePaginatedResponse:
        """
        Retrieve a paginated list of eligible marketplace bookings with search, filters, and recommendation ranking.
        """
        if min_price is not None and min_price < 0:
            raise BadRequestException(
                message="min_price must be greater than or equal to 0",
                error_code="INVALID_PRICE_RANGE",
            )
        if max_price is not None and max_price < 0:
            raise BadRequestException(
                message="max_price must be greater than or equal to 0",
                error_code="INVALID_PRICE_RANGE",
            )
        if min_price is not None and max_price is not None and min_price > max_price:
            raise BadRequestException(
                message="min_price cannot be greater than max_price",
                error_code="INVALID_PRICE_RANGE",
            )

        page = max(1, page)
        page_size = max(1, min(100, page_size))
        skip = (page - 1) * page_size

        bookings, total = await self.repo.list_marketplace_bookings(
            query=query,
            category_slug=category_slug,
            booking_type=booking_type,
            scheduled_date=scheduled_date,
            min_price=min_price,
            max_price=max_price,
            city=city,
            sort_by=sort_by,
            skip=skip,
            limit=page_size,
        )

        applied_booking_ids: set[str] = set()
        user_id_obj = worker_user_id or (worker_profile.user_id if worker_profile else None)
        if user_id_obj:
            uid = PydanticObjectId(str(user_id_obj))
            apps = await JobApplication.find({"worker_id": uid}).to_list()
            applied_booking_ids = {str(app.booking_id) for app in apps}

        items_with_score = []
        for b in bookings:
            score, dist_km, is_rec = self.recommendation_engine.score_booking(b, worker_profile)

            # ── Radius Filter ───────────────────────────────────────────────
            # Only exclude jobs that exceed the worker's configured radius when:
            #   1. A worker_profile exists (radius is configured), AND
            #   2. A valid distance was calculated (worker has a known location)
            if worker_profile is not None and dist_km is not None:
                if dist_km > worker_profile.working_radius_km:
                    continue  # Skip jobs beyond the worker's radius

            has_applied = str(b.id) in applied_booking_ids
            item_dto = MarketplaceBookingItemResponse(
                id=str(b.id),
                booking_number=b.booking_number,
                booking_type=b.booking_type,
                status=b.status,
                service_snapshot=b.service_snapshot,
                address=self._build_sanitized_address(b),
                scheduled_date=b.scheduled_date,
                scheduled_time=b.scheduled_time,
                estimated_price=b.estimated_price,
                estimated_duration_minutes=b.estimated_duration_minutes,
                distance_km=dist_km,
                is_recommended=is_rec,
                has_applied=has_applied,
                created_at=b.created_at,
            )
            items_with_score.append((score, item_dto))

        if sort_by == MarketplaceSortOption.RECOMMENDED:
            items_with_score.sort(key=lambda x: x[0], reverse=True)

        items = [item for _, item in items_with_score]
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return MarketplacePaginatedResponse(
            items=items,
            total=len(items),  # Reflect actual count after radius filter
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_marketplace_booking_detail(
        self,
        booking_id: str,
        worker_user_id: str | PydanticObjectId | None = None,
        worker_profile: WorkerProfile | None = None,
    ) -> MarketplaceBookingDetailResponse:
        """
        Retrieve details of a specific marketplace booking by ID.

        Raises:
            NotFoundException: If booking is not found or no longer available.
        """
        booking = await self.repo.get_marketplace_booking_by_id(booking_id)
        if not booking or not MarketplaceRulesEngine.is_booking_visible(booking):
            raise NotFoundException(
                message=f"Marketplace booking '{booking_id}' not found or no longer available",
                error_code="MARKETPLACE_BOOKING_NOT_FOUND",
            )

        has_applied = False
        user_id_obj = worker_user_id or (worker_profile.user_id if worker_profile else None)
        if user_id_obj and PydanticObjectId.is_valid(booking_id):
            uid = PydanticObjectId(str(user_id_obj))
            bid = PydanticObjectId(booking_id)
            existing = await JobApplication.find_one({"booking_id": bid, "worker_id": uid})
            if existing:
                has_applied = True

        return self._to_detail_response(booking, worker_profile, has_applied=has_applied)
