"""
Unit tests for Phase 7 Server-Side Skill Validation During Worker Application.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import GeoJSONPoint
from app.application.models import JobApplication
from app.application.schemas import JobApplicationCreateRequest
from app.application.service import JobApplicationService
from app.auth.models import User
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.core.exceptions import BadRequestException, ConflictException
from app.marketplace.rules import MarketplaceRulesEngine
from app.utils.enums import ApplicationStatus, BookingStatus, BookingType, WorkerAvailability
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
    mock_db.__getitem__ = MagicMock(return_value=mock_coll)

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, JobApplication])


def create_test_user() -> User:
    uid = PydanticObjectId()
    return User(
        id=uid,
        email=f"worker_{uid}@example.com",
        phone=f"+91{str(uid)[:10]}",
        password_hash="secret_hash",
        full_name="Test Worker",
        is_active=True,
    )


def create_test_profile(user_id: PydanticObjectId, skills: list[str], loc: GeoJSONPoint = DEFAULT_LOC, radius: float = 10.0, is_verified: bool = True) -> WorkerProfile:
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


def create_test_booking(category_slug: str, required_skills: list[str] | None = None, loc: GeoJSONPoint = DEFAULT_LOC, status: BookingStatus = BookingStatus.PENDING) -> Booking:
    req_skills = required_skills or []
    return Booking(
        id=PydanticObjectId(),
        booking_number=f"BK-{PydanticObjectId()}",
        customer_id=PydanticObjectId(),
        booking_type=BookingType.NORMAL_SERVICE,
        status=status,
        service_location=loc,
        service_snapshot=ServiceSnapshot(
            service_id="serv_123",
            name="Test Service",
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
async def test_matching_category_skill_succeeds():
    # TEST 1: Worker skills = ["electrical"], Booking category = "electrical" -> SUCCEEDS
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["electrical"])
    booking = create_test_booking("electrical")

    # Call rules engine directly
    MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)


@pytest.mark.asyncio
async def test_unrelated_skill_rejected_with_skill_mismatch():
    # TEST 2: Worker skills = ["plumbing"], Booking category = "electrical" -> 400 SKILL_MISMATCH
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["plumbing"])
    booking = create_test_booking("electrical")

    with pytest.raises(BadRequestException) as exc_info:
        MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)

    assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_multi_skill_worker_succeeds():
    # TEST 3: Worker skills = ["plumbing", "electrical", "carpentry"], Booking category = "electrical" -> SUCCEEDS
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["plumbing", "electrical", "carpentry"])
    booking = create_test_booking("electrical")

    MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)


@pytest.mark.asyncio
async def test_worker_with_no_skills_rejected():
    # TEST 4: Worker skills = [] -> 400 SKILL_MISMATCH
    user = create_test_user()
    profile = create_test_profile(user.id, skills=[])
    booking = create_test_booking("electrical")

    with pytest.raises(BadRequestException) as exc_info:
        MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)

    assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_casing_normalization_succeeds():
    # TEST 5: Worker skills = ["Electrical"], Booking category = "electrical" -> SUCCEEDS
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["Electrical"])
    booking = create_test_booking("electrical")

    MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)


@pytest.mark.asyncio
async def test_direct_api_bypass_prevention():
    # TEST 6: Direct API call to apply_for_job with mismatched skill -> 400 SKILL_MISMATCH
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["painting"])
    booking = create_test_booking("electrical")

    service = JobApplicationService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.application.repository.JobApplicationRepository.find_application_by_booking_and_worker", AsyncMock(return_value=None))

        req = JobApplicationCreateRequest(booking_id=str(booking.id))
        with pytest.raises(BadRequestException) as exc_info:
            await service.apply_for_job(user, req)

        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_duplicate_application_protection_preserved():
    # TEST 7: Eligible worker submits duplicate application -> 409 DUPLICATE_APPLICATION
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["electrical"])
    booking = create_test_booking("electrical")
    existing_app = JobApplication(booking_id=booking.id, worker_id=user.id, application_status=ApplicationStatus.PENDING)

    service = JobApplicationService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.application.repository.JobApplicationRepository.find_application_by_booking_and_worker", AsyncMock(return_value=existing_app))

        req = JobApplicationCreateRequest(booking_id=str(booking.id))
        with pytest.raises(ConflictException) as exc_info:
            await service.apply_for_job(user, req)

        assert exc_info.value.error_code == "DUPLICATE_APPLICATION"


@pytest.mark.asyncio
async def test_unavailable_booking_preserves_error():
    # TEST 8: Closed/Unavailable booking -> 400 BOOKING_NOT_AVAILABLE
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["electrical"])
    closed_booking = create_test_booking("electrical", status=BookingStatus.ACCEPTED)

    service = JobApplicationService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=closed_booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.application.repository.JobApplicationRepository.find_application_by_booking_and_worker", AsyncMock(return_value=None))

        req = JobApplicationCreateRequest(booking_id=str(closed_booking.id))
        with pytest.raises(BadRequestException) as exc_info:
            await service.apply_for_job(user, req)

        assert exc_info.value.error_code == "BOOKING_NOT_AVAILABLE"


@pytest.mark.asyncio
async def test_skill_match_and_radius_match():
    # TEST 9: Skill match + radius match (5 km away, radius 10 km) -> SUCCEEDS
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)
    booking = create_test_booking("electrical", loc=DEFAULT_LOC)

    MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)


@pytest.mark.asyncio
async def test_skill_match_and_radius_mismatch():
    # TEST 10: Skill match + radius mismatch (15 km away, radius 10 km) -> 400 OUTSIDE_SERVICE_RADIUS
    user = create_test_user()
    profile = create_test_profile(user.id, skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)
    far_booking = create_test_booking("electrical", loc=LOC_15KM)

    with pytest.raises(BadRequestException) as exc_info:
        await MarketplaceRulesEngine.validate_application_submission(
            booking=far_booking,
            worker_user=user,
            worker_profile=profile,
            existing_application=None,
        )

    assert exc_info.value.error_code == "OUTSIDE_SERVICE_RADIUS"
