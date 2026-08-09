"""
Unit tests for Phase 8 Secure Worker Acceptance & Atomic Assignment Logic.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import GeoJSONPoint
from app.application.models import JobApplication
from app.auth.models import User
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.booking.service import BookingService
from app.core.exceptions import BadRequestException, ConflictException
from app.marketplace.rules import MarketplaceRulesEngine
from app.utils.enums import BookingStatus, BookingType, InspectionStatus, WorkerAvailability
from app.worker.models import WorkerProfile

BANGALORE_CENTER_LAT = 12.9716
BANGALORE_CENTER_LNG = 77.5946
DEFAULT_LOC = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)

# Location approx 15 km away North
LAT_15KM_NORTH = BANGALORE_CENTER_LAT + 0.135
LOC_15KM = GeoJSONPoint.from_lat_lng(latitude=LAT_15KM_NORTH, longitude=BANGALORE_CENTER_LNG)


@pytest.fixture(autouse=True)
async def init_mock_beanie():
    mock_db = MagicMock()
    mock_db.command = AsyncMock(return_value={"version": "6.0.0"})
    mock_db.list_collection_names = AsyncMock(return_value=[])
    mock_coll = MagicMock()
    mock_coll.index_information = AsyncMock(return_value={})
    mock_coll.create_index = AsyncMock(return_value=None)
    mock_coll.create_indexes = AsyncMock(return_value=[])
    mock_coll.count_documents = AsyncMock(return_value=0)
    mock_coll.find_one = AsyncMock(return_value=None)
    mock_coll.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_db.__getitem__ = MagicMock(return_value=mock_coll)

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, JobApplication])


def create_test_user(name: str = "Test Worker") -> User:
    uid = PydanticObjectId()
    return User(
        id=uid,
        email=f"worker_{uid}@example.com",
        phone=f"+91{str(uid)[:10]}",
        password_hash="secret_hash",
        full_name=name,
        is_active=True,
    )


def create_test_profile(user_id: PydanticObjectId, skills: list[str], loc: GeoJSONPoint | None = DEFAULT_LOC, radius: float = 10.0, is_verified: bool = True) -> WorkerProfile:
    return WorkerProfile(
        id=PydanticObjectId(),
        user_id=user_id,
        skills=skills,
        profile_completed=True,
        availability=WorkerAvailability.AVAILABLE,
        current_location=loc,
        working_radius_km=radius,
        is_verified=is_verified,
    )


def create_test_booking(category_slug: str = "electrical", required_skills: list[str] | None = None, loc: GeoJSONPoint = DEFAULT_LOC, status: BookingStatus = BookingStatus.PENDING, worker_id: PydanticObjectId | None = None) -> Booking:
    req_skills = required_skills or []
    return Booking(
        id=PydanticObjectId(),
        booking_number=f"BK-{PydanticObjectId()}",
        customer_id=PydanticObjectId(),
        worker_id=worker_id,
        booking_type=BookingType.INSPECTION_REQUEST,
        status=status,
        inspection_status=InspectionStatus.REQUESTED,
        service_location=loc,
        service_snapshot=ServiceSnapshot(
            service_id="serv_123",
            name="Test Inspection Service",
            category_id="cat_123",
            category_slug=category_slug,
            required_skills=req_skills,
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
            location=loc,
        ),
        estimated_price=500.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_eligible_worker_accepts_succeeds():
    # TEST 1: Eligible worker accepts inspection -> SUCCESS
    user = create_test_user("Worker A")
    profile = create_test_profile(user.id, skills=["electrical"])
    booking = create_test_booking("electrical")

    mock_collection = MagicMock()
    mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_collection.count_documents = AsyncMock(return_value=0)
    mock_collection.find_one = AsyncMock(return_value=None)

    # Assigned booking state returned after atomic update
    assigned_b = create_test_booking("electrical", status=BookingStatus.ASSIGNED, worker_id=user.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(side_effect=[booking, assigned_b]))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_collection))
        m.setattr("app.application.models.JobApplication.find_one", AsyncMock(return_value=None))

        res = await BookingService.accept_inspection(str(booking.id), user)
        assert res.worker_id == str(user.id)
        assert res.status == BookingStatus.ASSIGNED.value


@pytest.mark.asyncio
async def test_skill_mismatch_rejected():
    # TEST 2: Worker skills = ["plumbing"], Booking category = "electrical" -> REJECTED SKILL_MISMATCH
    user = create_test_user("Worker Plumber")
    profile = create_test_profile(user.id, skills=["plumbing"])
    booking = create_test_booking("electrical")

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(booking.id), user)

        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_outside_radius_rejected():
    # TEST 3: Distance 15 km > working radius 10 km -> REJECTED OUTSIDE_SERVICE_RADIUS
    user = create_test_user("Worker Far")
    profile = create_test_profile(user.id, skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)
    far_booking = create_test_booking("electrical", loc=LOC_15KM)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=far_booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(far_booking.id), user)

        assert exc_info.value.error_code == "OUTSIDE_SERVICE_RADIUS"


@pytest.mark.asyncio
async def test_empty_skills_rejected():
    # TEST 4: Worker skills = [] -> REJECTED SKILL_MISMATCH
    user = create_test_user("Worker No Skills")
    profile = create_test_profile(user.id, skills=[])
    booking = create_test_booking("electrical")

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(booking.id), user)

        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_missing_worker_location_rejected():
    # TEST 5: Worker location = None -> REJECTED WORKER_LOCATION_REQUIRED
    user = create_test_user("Worker No Loc")
    profile = create_test_profile(user.id, skills=["electrical"], loc=None)
    booking = create_test_booking("electrical")

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(booking.id), user)

        assert exc_info.value.error_code == "WORKER_LOCATION_REQUIRED"


@pytest.mark.asyncio
async def test_already_assigned_booking_rejected():
    # TEST 6: Booking already assigned to worker1 -> REJECTED BOOKING_NOT_AVAILABLE / BOOKING_ALREADY_ASSIGNED
    user2 = create_test_user("Worker 2")
    profile2 = create_test_profile(user2.id, skills=["electrical"])
    assigned_booking = create_test_booking("electrical", worker_id=PydanticObjectId(), status=BookingStatus.ASSIGNED)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=assigned_booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile2))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(assigned_booking.id), user2)

        assert exc_info.value.error_code in ("BOOKING_NOT_AVAILABLE", "BOOKING_ALREADY_ASSIGNED")


@pytest.mark.asyncio
async def test_wrong_booking_status_rejected():
    # TEST 7: Booking status COMPLETED -> REJECTED BOOKING_NOT_AVAILABLE
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["electrical"])
    completed_booking = create_test_booking("electrical", status=BookingStatus.COMPLETED)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=completed_booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(completed_booking.id), user)

        assert exc_info.value.error_code == "BOOKING_NOT_AVAILABLE"


@pytest.mark.asyncio
async def test_direct_api_bypass_prevented():
    # TEST 8: Direct call to accept_inspection endpoint by unauthorized skill worker -> REJECTED SKILL_MISMATCH
    user_carpenter = create_test_user("Carpenter Worker")
    profile = create_test_profile(user_carpenter.id, skills=["carpentry"])
    elec_booking = create_test_booking("electrical")

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=elec_booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(elec_booking.id), user_carpenter)

        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_concurrent_acceptance_race_atomic_protection():
    # TEST 9: Two workers race to accept the same booking concurrently -> exactly 1 succeeds, 1 fails with BOOKING_ALREADY_ASSIGNED
    w1 = create_test_user("Worker 1")
    p1 = create_test_profile(w1.id, skills=["electrical"])
    w2 = create_test_user("Worker 2")
    p2 = create_test_profile(w2.id, skills=["electrical"])

    booking = create_test_booking("electrical")

    # Simulate atomic MongoDB update_one: Worker 1 update modifies 1 doc, Worker 2 update modifies 0 docs
    mock_coll1 = MagicMock()
    mock_coll1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_coll1.count_documents = AsyncMock(return_value=0)
    mock_coll1.find_one = AsyncMock(return_value=None)

    mock_coll2 = MagicMock()
    mock_coll2.update_one = AsyncMock(return_value=MagicMock(modified_count=0))
    mock_coll2.count_documents = AsyncMock(return_value=0)
    mock_coll2.find_one = AsyncMock(return_value=None)

    assigned_b1 = create_test_booking("electrical", status=BookingStatus.ASSIGNED, worker_id=w1.id)

    # Worker 1 execution
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(side_effect=[booking, assigned_b1]))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w1))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p1))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll1))
        m.setattr("app.application.models.JobApplication.find_one", AsyncMock(return_value=None))

        res1 = await BookingService.accept_inspection(str(booking.id), w1)
        assert res1.worker_id == str(w1.id)

    # Worker 2 execution (fails atomically because update_one returns modified_count=0 and booking is now assigned)
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(side_effect=[booking, assigned_b1]))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p2))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll2))

        with pytest.raises(ConflictException) as exc_info:
            await BookingService.accept_inspection(str(booking.id), w2)

        assert exc_info.value.error_code == "BOOKING_ALREADY_ASSIGNED"


@pytest.mark.asyncio
async def test_case_normalization_in_acceptance():
    # TEST 10: Worker skills = ["Electrical"], Booking category = "electrical" -> SUCCESS
    user = create_test_user("Worker Upper")
    profile = create_test_profile(user.id, skills=["Electrical"])
    booking = create_test_booking("electrical")

    mock_collection = MagicMock()
    mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_collection.count_documents = AsyncMock(return_value=0)
    mock_collection.find_one = AsyncMock(return_value=None)
    assigned_b = create_test_booking("electrical", status=BookingStatus.ASSIGNED, worker_id=user.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(side_effect=[booking, assigned_b]))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_collection))
        m.setattr("app.application.models.JobApplication.find_one", AsyncMock(return_value=None))

        res = await BookingService.accept_inspection(str(booking.id), user)
        assert res.worker_id == str(user.id)
