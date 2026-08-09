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

from app.address.models import GeoJSONPoint
from app.booking.models import Booking
from app.marketplace.recommendation.engine import calculate_haversine_distance
from app.marketplace.schemas import MarketplaceSortOption
from app.utils.enums import BookingStatus, BookingType

logger = logging.getLogger(__name__)


class MarketplaceRepository:
    """Encapsulates Beanie database queries for worker marketplace discovery."""

    @staticmethod
    async def list_marketplace_bookings(
        *,
        worker_skills: list[str] | None = None,
        worker_location: GeoJSONPoint | None = None,
        working_radius_km: float = 10.0,
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
        List open, unassigned marketplace bookings matching worker skills and working radius with search, multi-filtering, and sorting.
        """
        # Security/Business Rule 1: Worker without skills must see 0 marketplace bookings
        if not worker_skills:
            return [], 0

        clean_worker_skills = [s.strip().lower() for s in worker_skills if isinstance(s, str) and s.strip()]
        if not clean_worker_skills:
            return [], 0

        # Security/Business Rule 2: Worker without valid current location must see 0 marketplace bookings
        if not worker_location or not getattr(worker_location, "coordinates", None):
            return [], 0

        if len(worker_location.coordinates) != 2:
            return [], 0

        filters: dict[str, Any] = {
            "status": BookingStatus.PENDING.value,
            "worker_id": None,
        }

        # DB-Level Geospatial Radius Filter ($geoWithin + $centerSphere)
        radius_km = working_radius_km if (working_radius_km is not None and working_radius_km > 0) else 10.0
        radius_radians = radius_km / 6378.1  # Earth radius in kilometers

        filters["service_location"] = {
            "$geoWithin": {
                "$centerSphere": [
                    [worker_location.longitude, worker_location.latitude],  # GeoJSON order: [longitude, latitude]
                    radius_radians,
                ]
            }
        }

        # DB-Level Skill Filter & Category Slug intersection
        if category_slug and category_slug.strip():
            req_cat = category_slug.strip().lower()
            if req_cat in clean_worker_skills:
                filters["service_snapshot.category_slug"] = req_cat
            else:
                # Requested category is not within worker's registered skills
                return [], 0
        else:
            filters["service_snapshot.category_slug"] = {"$in": clean_worker_skills}

        # 1. Text Search across service name, category_slug, and problem description
        if query and query.strip():
            clean_query = re.escape(query.strip())
            regex_pat = {"$regex": clean_query, "$options": "i"}
            filters["$or"] = [
                {"service_snapshot.name": regex_pat},
                {"service_snapshot.category_slug": regex_pat},
                {"problem_description": regex_pat},
            ]

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
    async def get_marketplace_booking_by_id(
        booking_id: str | PydanticObjectId,
        worker_skills: list[str] | None = None,
        worker_location: GeoJSONPoint | None = None,
        working_radius_km: float = 10.0,
    ) -> Booking | None:
        """
        Fetch a single marketplace booking by ObjectId.

        Enforces that the booking must be PENDING, unassigned (worker_id == None),
        matching the worker's skills if worker_skills is provided, and inside worker's radius if worker_location is provided.
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

            # Verify status and assignment eligibility
            if booking.status != BookingStatus.PENDING or booking.worker_id is not None:
                return None

            # Verify skill domain eligibility if worker_skills provided
            if worker_skills is not None:
                clean_skills = [s.strip().lower() for s in worker_skills if isinstance(s, str)]
                b_cat = (booking.service_snapshot.category_slug or "").strip().lower()
                if not clean_skills or b_cat not in clean_skills:
                    return None

            # Verify geospatial eligibility if worker_location provided
            if worker_location is not None:
                if not getattr(worker_location, "coordinates", None):
                    return None
                b_loc = booking.service_location or (booking.address_snapshot.location if booking.address_snapshot else None)
                if not b_loc or not getattr(b_loc, "coordinates", None):
                    return None
                dist_km = calculate_haversine_distance(
                    worker_location.latitude, worker_location.longitude,
                    b_loc.latitude, b_loc.longitude,
                )
                if dist_km > working_radius_km:
                    return None

            return booking
        except Exception as exc:
            logger.debug("Failed to fetch marketplace booking %s: %s", booking_id, exc)
            return None
