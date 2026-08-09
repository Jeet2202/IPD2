"""
Unit tests for Phase 5 & 6 DB-Level Skill Filter & Geospatial in Marketplace queries.
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

DEFAULT_WORKER_LOC = GeoJSONPoint.from_lat_lng(12.9716, 77.5946)


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


def create_dummy_booking(category_slug: str, title: str = "Test Job") -> Booking:
    return Booking(
        id=PydanticObjectId(),
        booking_number=f"BK-{PydanticObjectId()}",
        customer_id=PydanticObjectId(),
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        service_location=DEFAULT_WORKER_LOC,
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
            full_name="Test Customer",
            phone="+919876543210",
            address_line_1="123 Main St",
            city="Bangalore",
            state="Karnataka",
            postal_code="560001",
            location=DEFAULT_WORKER_LOC,
        ),
        estimated_price=500.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_empty_skills_returns_zero_bookings():
    # TEST 6 & TEST 12: Worker with empty skills receives 0 marketplace bookings
    service = MarketplaceService()
    profile = WorkerProfile(user_id=PydanticObjectId(), skills=[], current_location=DEFAULT_WORKER_LOC)

    res = await service.list_marketplace_bookings(worker_profile=profile)
    assert res.items == []
    assert res.total == 0
    assert res.total_pages == 0


@pytest.mark.asyncio
async def test_no_worker_profile_returns_zero_bookings():
    # Security test: None worker_profile receives 0 marketplace bookings
    service = MarketplaceService()

    res = await service.list_marketplace_bookings(worker_profile=None)
    assert res.items == []
    assert res.total == 0


@pytest.mark.asyncio
async def test_skill_filter_intersection_with_requested_category():
    # TEST 9 & TEST 10: Category filter request vs worker skills intersection
    skills = ["electrical"]

    # TEST 9: Worker requests category "plumbing" which they do NOT have -> 0 results
    items, total = await MarketplaceRepository.list_marketplace_bookings(
        worker_skills=skills,
        worker_location=DEFAULT_WORKER_LOC,
        category_slug="plumbing",
    )
    assert items == []
    assert total == 0

    # TEST 10: Worker requests category "electrical" which they DO have -> passes to query
    mock_query = MagicMock()
    mock_query.count = AsyncMock(return_value=1)
    mock_query.sort = MagicMock(return_value=mock_query)
    mock_query.skip = MagicMock(return_value=mock_query)
    dummy_b = create_dummy_booking("electrical")
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.to_list = AsyncMock(return_value=[dummy_b])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.find", MagicMock(return_value=mock_query))

        items, total = await MarketplaceRepository.list_marketplace_bookings(
            worker_skills=skills,
            worker_location=DEFAULT_WORKER_LOC,
            category_slug="electrical",
        )
        assert len(items) == 1
        assert total == 1
        # Verify DB query filter passed to Booking.find
        call_args = Booking.find.call_args[0][0]
        assert call_args["service_snapshot.category_slug"] == "electrical"
        assert call_args["status"] == "pending"
        assert call_args["worker_id"] is None


@pytest.mark.asyncio
async def test_multi_skill_db_query_construction():
    # TEST 1 & 2 & 3 & 4 & 5 & 7 & 11: Multi-skill $in query construction
    skills = ["electrical", "plumbing"]

    mock_query = MagicMock()
    mock_query.count = AsyncMock(return_value=3)
    mock_query.sort = MagicMock(return_value=mock_query)
    mock_query.skip = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.to_list = AsyncMock(return_value=[
        create_dummy_booking("electrical"),
        create_dummy_booking("plumbing"),
        create_dummy_booking("electrical"),
    ])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.find", MagicMock(return_value=mock_query))

        items, total = await MarketplaceRepository.list_marketplace_bookings(
            worker_skills=skills,
            worker_location=DEFAULT_WORKER_LOC,
        )
        assert len(items) == 3
        assert total == 3

        call_args = Booking.find.call_args[0][0]
        assert call_args["service_snapshot.category_slug"] == {"$in": ["electrical", "plumbing"]}
        assert call_args["status"] == "pending"
        assert call_args["worker_id"] is None


@pytest.mark.asyncio
async def test_pagination_and_total_count():
    # TEST 8: Pagination limit and total count accuracy
    skills = ["electrical"]

    mock_query = MagicMock()
    mock_query.count = AsyncMock(return_value=10) # Total 10 matching DB records
    mock_query.sort = MagicMock(return_value=mock_query)
    mock_query.skip = MagicMock(return_value=mock_query)
    mock_query.limit = MagicMock(return_value=mock_query)
    mock_query.to_list = AsyncMock(return_value=[create_dummy_booking("electrical") for _ in range(5)])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.find", MagicMock(return_value=mock_query))

        items, total = await MarketplaceRepository.list_marketplace_bookings(
            worker_skills=skills,
            worker_location=DEFAULT_WORKER_LOC,
            skip=0,
            limit=5,
        )
        assert len(items) == 5
        assert total == 10 # Total matches the filtered query total count


@pytest.mark.asyncio
async def test_detail_view_skill_check():
    # Detail endpoint enforces skill eligibility and location eligibility
    skills = ["electrical"]
    elec_booking = create_dummy_booking("electrical")
    plumb_booking = create_dummy_booking("plumbing")

    with pytest.MonkeyPatch.context() as m:
        # Returning electrical booking inside radius -> allowed
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=elec_booking))
        res_elec = await MarketplaceRepository.get_marketplace_booking_by_id(
            elec_booking.id, worker_skills=skills, worker_location=DEFAULT_WORKER_LOC
        )
        assert res_elec is not None

        # Returning plumbing booking -> rejected (returns None)
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=plumb_booking))
        res_plumb = await MarketplaceRepository.get_marketplace_booking_by_id(
            plumb_booking.id, worker_skills=skills, worker_location=DEFAULT_WORKER_LOC
        )
        assert res_plumb is None
