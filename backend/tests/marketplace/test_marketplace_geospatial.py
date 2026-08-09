"""
Unit tests for Phase 6 DB-Level Geospatial / Working-Radius Filtering.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import GeoJSONPoint
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.marketplace.repository import MarketplaceRepository
from app.marketplace.service import MarketplaceService
from app.utils.enums import BookingStatus, BookingType
from app.worker.models import WorkerProfile
from app.auth.models import User

# Bangalore center coordinates
BANGALORE_CENTER_LAT = 12.9716
BANGALORE_CENTER_LNG = 77.5946

# Offset approx 5 km North (approx 0.045 deg latitude)
LAT_5KM_NORTH = 12.9716 + 0.045
# Offset approx 15 km North (approx 0.135 deg latitude)
LAT_15KM_NORTH = 12.9716 + 0.135
# Offset approx 25 km North (approx 0.225 deg latitude)
LAT_25KM_NORTH = 12.9716 + 0.225


@pytest.fixture(autouse=True)
async def init_mock_beanie():
    mock_db = MagicMock()
    mock_db.command = AsyncMock(return_value={"version": "6.0.0"})
    mock_db.list_collection_names = AsyncMock(return_value=[])
    mock_coll = MagicMock()
    mock_coll.index_information = AsyncMock(return_value={})
    mock_coll.create_index = AsyncMock(return_value=None)
    mock_coll.create_indexes = AsyncMock(return_value=[])
    mock_db.__getitem__ = MagicMock(return_value=mock_coll)
    
    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking])


def create_geo_booking(category_slug: str, lat: float, lng: float, title: str = "Geo Job") -> Booking:
    loc = GeoJSONPoint.from_lat_lng(latitude=lat, longitude=lng)
    return Booking(
        id=PydanticObjectId(),
        booking_number=f"BK-{PydanticObjectId()}",
        customer_id=PydanticObjectId(),
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        service_location=loc,
        service_snapshot=ServiceSnapshot(
            service_id="serv_123",
            name=title,
            category_id="cat_123",
            category_slug=category_slug,
            base_market_price=500.0,
            estimated_duration_minutes=60,
        ),
        address_snapshot=AddressSnapshot(
            address_id="addr_123",
            label="Home",
            full_name="Geo Customer",
            phone="+919876543210",
            address_line_1="123 Main St",
            city="Bangalore",
            state="Karnataka",
            postal_code="560001",
            location=loc,
        ),
        estimated_price=500.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_worker_without_location_returns_zero_bookings():
    # TEST 4: Worker with current_location = None receives ZERO marketplace bookings
    service = MarketplaceService()
    profile = WorkerProfile(
        user_id=PydanticObjectId(),
        skills=["electrical"],
        current_location=None,  # Missing location
        working_radius_km=10.0,
    )

    res = await service.list_marketplace_bookings(worker_profile=profile)
    assert res.items == []
    assert res.total == 0


@pytest.mark.asyncio
async def test_geospatial_mongodb_query_construction():
    # TEST 1 & 3 & 7 & 8: Verify $geoWithin and $centerSphere query construction
    worker_loc = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)
    worker_skills = ["electrical"]
    radius_km = 10.0

    mock_query = MagicMock()
    mock_query.count = AsyncMock(return_value=2)
    mock_query.sort = MagicMock(return_value=mock_query)
    mock_query.skip = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.to_list = AsyncMock(return_value=[
        create_geo_booking("electrical", BANGALORE_CENTER_LAT, BANGALORE_CENTER_LNG, "Close Job"),
        create_geo_booking("electrical", LAT_5KM_NORTH, BANGALORE_CENTER_LNG, "5km Job"),
    ])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.find", MagicMock(return_value=mock_query))

        items, total = await MarketplaceRepository.list_marketplace_bookings(
            worker_skills=worker_skills,
            worker_location=worker_loc,
            working_radius_km=radius_km,
        )

        assert len(items) == 2
        assert total == 2

        # Verify MongoDB query parameters passed to Booking.find
        call_args = Booking.find.call_args[0][0]
        assert "service_location" in call_args
        geo_clause = call_args["service_location"]["$geoWithin"]["$centerSphere"]
        
        # Verify coordinates order is [longitude, latitude]
        assert geo_clause[0] == [BANGALORE_CENTER_LNG, BANGALORE_CENTER_LAT]
        
        # Verify radius in radians
        expected_radians = 10.0 / 6378.1
        assert pytest.approx(geo_clause[1], 1e-6) == expected_radians


@pytest.mark.asyncio
async def test_skill_plus_radius_combination():
    # TEST 9: SKILL + RADIUS combination (Electrical/5km visible, others hidden)
    worker_loc = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)
    skills = ["electrical"]
    radius_km = 10.0

    # 1. Detail view check for Electrical at 5 km -> ALLOWED
    elec_5km = create_geo_booking("electrical", LAT_5KM_NORTH, BANGALORE_CENTER_LNG)
    # 2. Detail view check for Electrical at 15 km -> REJECTED (outside radius)
    elec_15km = create_geo_booking("electrical", LAT_15KM_NORTH, BANGALORE_CENTER_LNG)
    # 3. Detail view check for Plumbing at 5 km -> REJECTED (mismatched skill)
    plumb_5km = create_geo_booking("plumbing", LAT_5KM_NORTH, BANGALORE_CENTER_LNG)

    with pytest.MonkeyPatch.context() as m:
        # Electrical 5km is inside radius & matches skill -> return booking
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=elec_5km))
        res1 = await MarketplaceRepository.get_marketplace_booking_by_id(
            elec_5km.id, worker_skills=skills, worker_location=worker_loc, working_radius_km=radius_km
        )
        assert res1 is not None

        # Electrical 15km is outside radius -> return None
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=elec_15km))
        res2 = await MarketplaceRepository.get_marketplace_booking_by_id(
            elec_15km.id, worker_skills=skills, worker_location=worker_loc, working_radius_km=radius_km
        )
        assert res2 is None

        # Plumbing 5km matches radius but violates skill -> return None
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=plumb_5km))
        res3 = await MarketplaceRepository.get_marketplace_booking_by_id(
            plumb_5km.id, worker_skills=skills, worker_location=worker_loc, working_radius_km=radius_km
        )
        assert res3 is None


@pytest.mark.asyncio
async def test_worker_radius_variations():
    # TEST 5 & TEST 6: Worker radius variations (5 km vs 20 km)
    worker_loc = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)
    skills = ["electrical"]

    job_15km = create_geo_booking("electrical", LAT_15KM_NORTH, BANGALORE_CENTER_LNG)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=job_15km))

        # Worker with 5km radius cannot see 15km job
        res_5km = await MarketplaceRepository.get_marketplace_booking_by_id(
            job_15km.id, worker_skills=skills, worker_location=worker_loc, working_radius_km=5.0
        )
        assert res_5km is None

        # Worker with 20km radius CAN see 15km job
        res_20km = await MarketplaceRepository.get_marketplace_booking_by_id(
            job_15km.id, worker_skills=skills, worker_location=worker_loc, working_radius_km=20.0
        )
        assert res_20km is not None
