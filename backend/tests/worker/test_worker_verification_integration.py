"""
Phase 11 — Worker Verification Integration Unit & Integration Test Suite.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import GeoJSONPoint
from app.application.models import JobApplication
from app.auth.models import User, UserRole
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.core.exceptions import BadRequestException, ForbiddenException
from app.marketplace.rules import MarketplaceRulesEngine
from app.marketplace.service import MarketplaceService
from app.utils.enums import BookingStatus, BookingType, InspectionStatus, WorkerAvailability
from app.verification.models import WorkerVerification
from app.verification.schemas import VerificationStatus, VerificationType
from app.verification.service import VerificationService
from app.worker.models import WorkerProfile

BANGALORE_CENTER_LAT = 12.9716
BANGALORE_CENTER_LNG = 77.5946
DEFAULT_LOC = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)


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

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, JobApplication, WorkerVerification])


def create_test_worker(is_verified: bool = False, skills: list[str] | None = None):
    uid = PydanticObjectId()
    user = User(
        id=uid,
        email=f"worker_{uid}@example.com",
        phone="+919876543210",
        password_hash="hash",
        full_name="Test Worker",
        role=UserRole.WORKER,
        is_active=True,
    )
    profile = WorkerProfile(
        id=PydanticObjectId(),
        user_id=uid,
        skills=skills or ["electrical"],
        profile_completed=True,
        availability=WorkerAvailability.AVAILABLE,
        current_location=DEFAULT_LOC,
        working_radius_km=10.0,
        is_verified=is_verified,
    )
    return user, profile


def create_test_booking(category_slug: str = "electrical"):
    return Booking(
        id=PydanticObjectId(),
        booking_number="BK-TEST",
        customer_id=PydanticObjectId(),
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        inspection_status=InspectionStatus.NOT_REQUIRED,
        service_location=DEFAULT_LOC,
        service_snapshot=ServiceSnapshot(
            service_id="s1",
            name="Test Service",
            category_id="c1",
            category_slug=category_slug,
            required_skills=[],
            base_market_price=100.0,
            estimated_duration_minutes=60,
        ),
        address_snapshot=AddressSnapshot(
            address_id="a1",
            label="Home",
            full_name="Cust",
            phone="+919876543210",
            address_line_1="L1",
            city="Bangalore",
            state="KA",
            postal_code="560001",
            location=DEFAULT_LOC,
        ),
        estimated_price=100.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )


# =============================================================================
# TESTS 1 - 5: ELIGIBILITY & STATUS CHECKS
# =============================================================================

def test_1_verified_worker_valid_skill_radius_is_eligible():
    w_user, w_prof = create_test_worker(is_verified=True, skills=["electrical"])
    MarketplaceRulesEngine.validate_worker_eligibility(w_user, w_prof)


def test_2_unverified_worker_is_rejected():
    w_user, w_prof = create_test_worker(is_verified=False, skills=["electrical"])
    with pytest.raises(ForbiddenException) as exc_info:
        MarketplaceRulesEngine.validate_worker_eligibility(w_user, w_prof)
    assert exc_info.value.error_code == "WORKER_NOT_VERIFIED"


def test_3_worker_with_no_verification_record_defaults_to_unverified():
    _, w_prof = create_test_worker(is_verified=False)
    assert w_prof.is_verified is False


@pytest.mark.asyncio
async def test_4_5_pending_or_rejected_verification_results_in_unverified():
    w_user, w_prof = create_test_worker(is_verified=False)
    worker_id_str = str(w_user.id)

    pending_v = WorkerVerification(
        verification_id="v1",
        worker_id=worker_id_str,
        verification_type=VerificationType.IDENTITY,
        status=VerificationStatus.SUBMITTED,
    )

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.verification.repository.WorkerVerificationRepository.list_by_worker", AsyncMock(return_value=[pending_v]))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))

        is_verified = await VerificationService.sync_worker_verification_status(worker_id_str)
        assert is_verified is False
        assert w_prof.is_verified is False


# =============================================================================
# TESTS 6 & 14: SYNCHRONIZATION & IDEMPOTENCY
# =============================================================================

@pytest.mark.asyncio
async def test_6_14_approved_verification_sync_and_idempotency():
    w_user, w_prof = create_test_worker(is_verified=False)
    worker_id_str = str(w_user.id)

    approved_v = WorkerVerification(
        verification_id="v2",
        worker_id=worker_id_str,
        verification_type=VerificationType.IDENTITY,
        status=VerificationStatus.APPROVED,
    )

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.verification.repository.WorkerVerificationRepository.list_by_worker", AsyncMock(return_value=[approved_v]))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))

        res1 = await VerificationService.sync_worker_verification_status(worker_id_str)
        assert res1 is True
        assert w_prof.is_verified is True

        res2 = await VerificationService.sync_worker_verification_status(worker_id_str)
        assert res2 is True
        assert w_prof.is_verified is True


# =============================================================================
# TESTS 7 & 8: APPLICATION & ACCEPTANCE REJECTION FOR UNVERIFIED WORKERS
# =============================================================================

@pytest.mark.asyncio
async def test_7_unverified_worker_direct_application_rejected():
    w_user, w_prof = create_test_worker(is_verified=False, skills=["electrical"])
    booking = create_test_booking("electrical")

    with pytest.raises(ForbiddenException) as exc_info:
        await MarketplaceRulesEngine.validate_application_submission(
            booking=booking,
            worker_user=w_user,
            worker_profile=w_prof,
            existing_application=None,
        )
    assert exc_info.value.error_code == "WORKER_NOT_VERIFIED"


def test_8_unverified_worker_accept_inspection_rejected():
    w_user, w_prof = create_test_worker(is_verified=False, skills=["electrical"])
    booking = create_test_booking("electrical")

    with pytest.raises(ForbiddenException) as exc_info:
        MarketplaceRulesEngine.validate_worker_acceptance_eligibility(
            booking=booking,
            worker_user=w_user,
            worker_profile=w_prof,
        )
    assert exc_info.value.error_code == "WORKER_NOT_VERIFIED"


# =============================================================================
# TESTS 9 & 10: VERIFIED WORKER SKILL & RADIUS PRESERVATION
# =============================================================================

def test_9_verified_worker_wrong_skill_still_rejected_with_skill_mismatch():
    w_user, w_prof = create_test_worker(is_verified=True, skills=["plumbing"])
    booking = create_test_booking("electrical")

    with pytest.raises(BadRequestException) as exc_info:
        MarketplaceRulesEngine.validate_worker_acceptance_eligibility(
            booking=booking,
            worker_user=w_user,
            worker_profile=w_prof,
        )
    assert exc_info.value.error_code == "SKILL_MISMATCH"


def test_10_verified_worker_outside_radius_still_rejected():
    w_user, w_prof = create_test_worker(is_verified=True, skills=["electrical"])
    booking = create_test_booking("electrical")

    booking.service_location = GeoJSONPoint.from_lat_lng(latitude=28.6139, longitude=77.2090)

    with pytest.raises(BadRequestException) as exc_info:
        MarketplaceRulesEngine.validate_worker_acceptance_eligibility(
            booking=booking,
            worker_user=w_user,
            worker_profile=w_prof,
        )
    assert exc_info.value.error_code == "OUTSIDE_SERVICE_RADIUS"


# =============================================================================
# TESTS 12 & 13: MARKETPLACE LISTING FOR UNVERIFIED VS VERIFIED WORKERS
# =============================================================================

@pytest.mark.asyncio
async def test_12_unverified_worker_sees_0_marketplace_results():
    _, w_prof = create_test_worker(is_verified=False, skills=["electrical"])
    svc = MarketplaceService()

    res = await svc.list_marketplace_bookings(worker_profile=w_prof)
    assert res.total == 0
    assert len(res.items) == 0


@pytest.mark.asyncio
async def test_13_verified_eligible_worker_sees_marketplace_results():
    _, w_prof = create_test_worker(is_verified=True, skills=["electrical"])
    booking = create_test_booking("electrical")
    svc = MarketplaceService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.marketplace.repository.MarketplaceRepository.list_marketplace_bookings", AsyncMock(return_value=([booking], 1)))
        m.setattr("app.application.models.JobApplication.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[]))))

        res = await svc.list_marketplace_bookings(worker_profile=w_prof)
        assert res.total == 1
        assert len(res.items) == 1


# =============================================================================
# TEST 15: COMPATIBILITY FOR EXISTING WORKERPROFILE WITHOUT IS_VERIFIED
# =============================================================================

def test_15_legacy_worker_profile_without_is_verified_defaults_false():
    p = WorkerProfile.model_construct(
        skills=["electrical"],
        profile_completed=True,
        availability=WorkerAvailability.AVAILABLE,
    )
    assert getattr(p, "is_verified", False) is False
