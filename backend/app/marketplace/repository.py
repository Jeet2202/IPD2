"""
Marketplace Repository — pure database access layer for worker booking discovery.

Rules:
    - ONLY database queries here — no business logic.
    - Operates on the existing 'bookings' collection without duplication.
    - Exposes strictly eligible bookings: status == PENDING and worker_id == None.
"""

import logging
import re
from datetime import date
from typing import Any

from beanie import PydanticObjectId

from app.booking.models import Booking
from app.marketplace.schemas import MarketplaceSortOption
from app.utils.enums import BookingStatus, BookingType

logger = logging.getLogger(__name__)


class MarketplaceRepository:
    """Encapsulates Beanie database queries for worker marketplace discovery."""

    @staticmethod
    async def list_marketplace_bookings(
        *,
        query: str | None = None,
        category_slug: str | None = None,
        booking_type: BookingType | None = None,
        scheduled_date: date | str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        city: str | None = None,
        sort_by: MarketplaceSortOption = MarketplaceSortOption.NEWEST,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Booking], int]:
        """
        List open, unassigned marketplace bookings with search, multi-filtering, and sorting.
        """
        filters: dict[str, Any] = {
            "status": BookingStatus.PENDING.value,
            "worker_id": None,
        }

        # 1. Text Search across service name, category_slug, and problem description
        if query and query.strip():
            clean_query = re.escape(query.strip())
            regex_pat = {"$regex": clean_query, "$options": "i"}
            filters["$or"] = [
                {"service_snapshot.name": regex_pat},
                {"service_snapshot.category_slug": regex_pat},
                {"problem_description": regex_pat},
            ]

        # 2. Filters
        if category_slug and category_slug.strip():
            filters["service_snapshot.category_slug"] = category_slug.strip()

        if booking_type:
            filters["booking_type"] = booking_type.value

        if scheduled_date:
            if isinstance(scheduled_date, str):
                try:
                    from datetime import datetime as dt
                    scheduled_date = dt.strptime(scheduled_date, "%Y-%m-%d").date()
                except ValueError:
                    pass
            filters["scheduled_date"] = scheduled_date

        if city and city.strip():
            filters["address_snapshot.city"] = {
                "$regex": f"^{re.escape(city.strip())}$",
                "$options": "i",
            }

        # Price Range Filter
        if min_price is not None or max_price is not None:
            price_filter: dict[str, Any] = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            filters["estimated_price"] = price_filter

        # 3. Sorting
        sort_expression: str = "-created_at"
        if sort_by == MarketplaceSortOption.OLDEST:
            sort_expression = "created_at"
        elif sort_by == MarketplaceSortOption.PRICE_HIGH:
            sort_expression = "-estimated_price"
        elif sort_by == MarketplaceSortOption.PRICE_LOW:
            sort_expression = "estimated_price"
        elif sort_by == MarketplaceSortOption.DISTANCE:
            # Fallback to newest until distance calculation engine is plugged in
            sort_expression = "-created_at"

        mongo_query = Booking.find(filters)

        total = await mongo_query.count()
        items = (
            await mongo_query
            .sort(sort_expression)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

        return items, total

    @staticmethod
    async def get_marketplace_booking_by_id(booking_id: str | PydanticObjectId) -> Booking | None:
        """
        Fetch a single marketplace booking by ObjectId.

        Enforces that the booking must be PENDING and unassigned (worker_id == None).
        Returns None if not found or not eligible for marketplace viewing.
        """
        try:
            oid = (
                PydanticObjectId(str(booking_id))
                if isinstance(booking_id, str)
                else booking_id
            )
            booking = await Booking.get(oid)
            if not booking:
                return None

            # Verify marketplace eligibility
            if booking.status != BookingStatus.PENDING or booking.worker_id is not None:
                return None

            return booking
        except Exception as exc:
            logger.debug("Failed to fetch marketplace booking %s: %s", booking_id, exc)
            return None
