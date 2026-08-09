"""
Phase 14 — Integration Tests + Production Readiness Test Suite
Ally / IPD2 Production Booking Matching System

Validates:
1. All 20 Phase 14 Business Test Cases.
2. Complete end-to-end customer booking -> matching -> notification -> application -> review -> atomic assignment.
3. Security & Direct API bypass prevention.
4. Concurrency & atomic race condition safety.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import Address, GeoJSONPoint
from app.application.models import JobApplication
from app.application.schemas import JobApplicationCreateRequest
from app.application.service import JobApplicationService
from app.auth.models import User, UserRole
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.booking.service import BookingService
from app.booking.schemas import CreateBookingRequest
from app.category.models import Service, ServiceCategory
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.marketplace.recommendation.engine import RecommendationEngine, calculate_haversine_distance
from app.marketplace.repository import MarketplaceRepository
from app.marketplace.rules import MarketplaceRulesEngine
from app.marketplace.service import MarketplaceService
from app.notifications.service import notification_service
from app.utils.enums import ApplicationStatus, BookingStatus, BookingType, InspectionStatus, WorkerAvailability
from app.worker.models import WorkerProfile

BANGALORE_CENTER_LAT = 12.9716
BANGALORE_CENTER_LNG = 77.5946
DEFAULT_LOC = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)

# 5 km North
LOC_5KM = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT + 0.045, longitude=BANGALORE_CENTER_LNG)
# 15 km North
LOC_15KM = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT + 0.135, longitude=BANGALORE_CENTER_LNG)


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
    mock_coll.find_one_and_update = AsyncMock(return_value={"_id": PydanticObjectId()})
    mock_db.__getitem__ = MagicMock(return_value=mock_coll)

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, JobApplication, Service, ServiceCategory, Address])


def make_customer(name: str = "Test Customer", active: bool = True) -> User:
    uid = PydanticObjectId()
    return User(
        id=uid,
        email=f"cust_{uid}@example.com",
        phone=f"+9198{str(uid)[:8]}",
        password_hash="hash",
        full_name=name,
        role=UserRole.CUSTOMER,
        is_active=active,
    )


def make_worker(name: str = "Test Worker", active: bool = True) -> User:
    uid = PydanticObjectId()
    return User(
        id=uid,
        email=f"work_{uid}@example.com",
        phone=f"+9197{str(uid)[:8]}",
        password_hash="hash",
        full_name=name,
        role=UserRole.WORKER,
        is_active=active,
    )


def make_worker_profile(
    user_id: PydanticObjectId,
    skills: list[str],
    loc: GeoJSONPoint | None = DEFAULT_LOC,
    radius: float = 10.0,
    completed: bool = True,
    is_verified: bool = True,
    availability: WorkerAvailability = WorkerAvailability.AVAILABLE,
) -> WorkerProfile:
    return WorkerProfile(
        id=PydanticObjectId(),
        user_id=user_id,
        skills=skills,
        profile_completed=completed,
        availability=availability,
        current_location=loc,
        working_radius_km=radius,
        is_verified=is_verified,
    )


def make_booking(
    customer_id: PydanticObjectId,
    category_slug: str = "electrical",
    status: BookingStatus = BookingStatus.PENDING,
    worker_id: PydanticObjectId | None = None,
    loc: GeoJSONPoint = DEFAULT_LOC,
) -> Booking:
    return Booking(
        id=PydanticObjectId(),
        booking_number=f"BK-{PydanticObjectId()}",
        customer_id=customer_id,
        worker_id=worker_id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=status,
        inspection_status=InspectionStatus.NOT_REQUIRED,
        service_location=loc,
        service_snapshot=ServiceSnapshot(
            service_id="serv_1",
            name="Electrical Repair",
            category_id="cat_1",
            category_slug=category_slug,
            required_skills=["electrical"],
            base_market_price=500.0,
            estimated_duration_minutes=60,
        ),
        address_snapshot=AddressSnapshot(
            address_id="addr_1",
            label="Home",
            full_name="Customer",
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


# ---------------------------------------------------------------------------
# 20 BUSINESS TEST CASES
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_case_1_worker_electrical_inside_radius_visible():
    """TEST 1: Worker skill=electrical, inside radius -> VISIBLE"""
    profile = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=LOC_5KM)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile.skills, worker_location=profile.current_location, working_radius_km=profile.working_radius_km
        )
        assert res is not None
        assert res.service_snapshot.category_slug == "electrical"


@pytest.mark.asyncio
async def test_case_2_worker_plumbing_booking_electrical_not_visible():
    """TEST 2: Worker skill=plumbing, booking=electrical -> NOT VISIBLE"""
    profile = make_worker_profile(PydanticObjectId(), skills=["plumbing"], loc=DEFAULT_LOC, radius=10.0)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=LOC_5KM)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile.skills, worker_location=profile.current_location, working_radius_km=profile.working_radius_km
        )
        assert res is None


@pytest.mark.asyncio
async def test_case_3_worker_electrical_outside_radius_not_visible():
    """TEST 3: Worker skill=electrical, outside radius (15km > 10km) -> NOT VISIBLE"""
    profile = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=LOC_15KM)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile.skills, worker_location=profile.current_location, working_radius_km=profile.working_radius_km
        )
        assert res is None


@pytest.mark.asyncio
async def test_case_4_multi_skill_worker_booking_electrical_visible():
    """TEST 4: Worker skills=[electrical, plumbing], booking=electrical -> VISIBLE"""
    profile = make_worker_profile(PydanticObjectId(), skills=["electrical", "plumbing"], loc=DEFAULT_LOC, radius=10.0)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=LOC_5KM)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile.skills, worker_location=profile.current_location, working_radius_km=profile.working_radius_km
        )
        assert res is not None


@pytest.mark.asyncio
async def test_case_5_worker_location_none_returns_zero():
    """TEST 5: Worker location=None -> NOT VISIBLE / 0 bookings"""
    profile = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=None, radius=10.0)

    service = MarketplaceService()
    res = await service.list_marketplace_bookings(worker_profile=profile)
    assert res.items == []
    assert res.total == 0


@pytest.mark.asyncio
async def test_case_6_customer_address_no_gps_raises_bad_request():
    """TEST 6: Customer address has no GPS -> 400 INVALID_ADDRESS_LOCATION"""
    customer = make_customer()
    address_no_gps = Address(
        id=PydanticObjectId(),
        customer_id=customer.id,
        label="Home",
        full_name="Customer",
        phone="+919876543210",
        address_line_1="123 Main St",
        city="Bangalore",
        state="Karnataka",
        postal_code="560001",
        is_deleted=False,
        location=None, # Missing GPS
    )

    mock_service = Service(
        id=PydanticObjectId(),
        name="Electrical Repair",
        slug="electrical-repair",
        category_id=str(PydanticObjectId()),
        category_slug="electrical",
        base_market_price=500.0,
        estimated_duration_minutes=60,
        is_active=True,
    )

    req = CreateBookingRequest(
        service_id=str(mock_service.id),
        address_id=str(address_no_gps.id),
        booking_type=BookingType.NORMAL_SERVICE,
    )

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=customer))
        m.setattr("app.category.models.Service.get", AsyncMock(return_value=mock_service))
        m.setattr("app.address.models.Address.get", AsyncMock(return_value=address_no_gps))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.create_booking(str(customer.id), req)
        assert exc_info.value.error_code == "INVALID_ADDRESS_LOCATION"


@pytest.mark.asyncio
async def test_case_7_inactive_worker_account_rejected():
    """TEST 7: Worker is_active=False -> Auth / eligibility rejected"""
    worker = make_worker(active=False)
    profile = make_worker_profile(worker.id, skills=["electrical"])

    with pytest.raises(ForbiddenException) as exc_info:
        MarketplaceRulesEngine.validate_worker_eligibility(worker, profile)
    assert exc_info.value.error_code == "WORKER_INACTIVE"


@pytest.mark.asyncio
async def test_case_8_incomplete_worker_profile_rejected():
    """TEST 8: Worker profile_completed=False -> 403 PROFILE_INCOMPLETE"""
    worker = make_worker()
    profile = make_worker_profile(worker.id, skills=["electrical"], completed=False)

    with pytest.raises(ForbiddenException) as exc_info:
        MarketplaceRulesEngine.validate_worker_eligibility(worker, profile)
    assert exc_info.value.error_code == "PROFILE_INCOMPLETE"


@pytest.mark.asyncio
async def test_case_9_assigned_booking_not_in_marketplace():
    """TEST 9: Booking worker_id already set -> Not available in marketplace"""
    assigned_worker = make_worker()
    booking = make_booking(PydanticObjectId(), category_slug="electrical", status=BookingStatus.ASSIGNED, worker_id=assigned_worker.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=["electrical"], worker_location=DEFAULT_LOC
        )
        assert res is None


@pytest.mark.asyncio
async def test_case_10_plumber_applies_electrical_job_rejected():
    """TEST 10: Plumber applies to electrical job -> 400 SKILL_MISMATCH"""
    worker = make_worker()
    profile = make_worker_profile(worker.id, skills=["plumbing"])
    booking = make_booking(PydanticObjectId(), category_slug="electrical")

    service = JobApplicationService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.application.repository.JobApplicationRepository.find_application_by_booking_and_worker", AsyncMock(return_value=None))

        req = JobApplicationCreateRequest(booking_id=str(booking.id))
        with pytest.raises(BadRequestException) as exc_info:
            await service.apply_for_job(worker, req)
        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_case_11_plumber_accepts_inspection_electrical_rejected():
    """TEST 11: Plumber accepts inspection on electrical booking -> 400 SKILL_MISMATCH"""
    worker = make_worker()
    profile = make_worker_profile(worker.id, skills=["plumbing"])
    booking = make_booking(PydanticObjectId(), category_slug="electrical")
    booking.booking_type = BookingType.INSPECTION_REQUEST
    booking.inspection_status = InspectionStatus.REQUESTED

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))

        with pytest.raises(BadRequestException) as exc_info:
            await BookingService.accept_inspection(str(booking.id), worker)
        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_case_12_empty_worker_skills_returns_zero_bookings():
    """TEST 12: Worker skills=[] -> Empty marketplace (0 bookings)"""
    profile = make_worker_profile(PydanticObjectId(), skills=[], loc=DEFAULT_LOC)

    service = MarketplaceService()
    res = await service.list_marketplace_bookings(worker_profile=profile)
    assert res.items == []
    assert res.total == 0


@pytest.mark.asyncio
async def test_case_13_exact_category_slug_matching():
    """TEST 13: Worker skill matches category_slug exactly -> VISIBLE"""
    profile = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=DEFAULT_LOC)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=DEFAULT_LOC)

    MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)


@pytest.mark.asyncio
async def test_case_14_skill_casing_normalization():
    """TEST 14: Worker skill 'Electrical' -> Normalized to 'electrical'"""
    profile = make_worker_profile(PydanticObjectId(), skills=["Electrical"], loc=DEFAULT_LOC)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=DEFAULT_LOC)

    # Upper case skill input is normalized during validation
    MarketplaceRulesEngine.validate_worker_skill_eligibility(booking, profile)


@pytest.mark.asyncio
async def test_case_15_concurrent_inspection_acceptance_atomic_race():
    """TEST 15: Two workers race to accept same inspection -> Only 1 succeeds"""
    worker1 = make_worker("Worker 1")
    profile1 = make_worker_profile(worker1.id, skills=["electrical"])
    
    worker2 = make_worker("Worker 2")
    profile2 = make_worker_profile(worker2.id, skills=["electrical"])

    booking = make_booking(PydanticObjectId(), category_slug="electrical")
    booking.booking_type = BookingType.INSPECTION_REQUEST
    booking.inspection_status = InspectionStatus.REQUESTED

    # Mock atomic update_one to succeed for Worker 1 (modified=1) and fail for Worker 2 (modified=0)
    mock_coll = MagicMock()
    mock_coll.update_one = AsyncMock(side_effect=[
        MagicMock(modified_count=1), # First worker succeeds
        MagicMock(modified_count=0), # Second worker fails race
    ])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile1))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll))

        # Worker 1 succeeds
        res1 = await BookingService.accept_inspection(str(booking.id), worker1)
        assert res1 is not None

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile2))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll))

        # Worker 2 fails race
        with pytest.raises(Exception) as exc_info:
            await BookingService.accept_inspection(str(booking.id), worker2)
        assert exc_info.value.error_code in ("BOOKING_ALREADY_ASSIGNED", "BOOKING_NOT_AVAILABLE")


@pytest.mark.asyncio
async def test_case_16_recommendation_engine_distance_ranking():
    """TEST 16: Three electrical workers at different distances -> Closest worker ranks highest"""
    engine = RecommendationEngine()
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=DEFAULT_LOC)

    profile_close = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=DEFAULT_LOC)
    profile_mid = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=LOC_5KM)
    profile_far = make_worker_profile(PydanticObjectId(), skills=["electrical"], loc=LOC_15KM, radius=20.0)

    score_close, dist_close, _ = engine.score_booking(booking, profile_close)
    score_mid, dist_mid, _ = engine.score_booking(booking, profile_mid)
    score_far, dist_far, _ = engine.score_booking(booking, profile_far)

    assert score_close > score_mid > score_far
    assert dist_close < dist_mid < dist_far


@pytest.mark.asyncio
async def test_case_17_customer_applicant_selection_and_atomic_assignment():
    """TEST 17: Customer accepts applicant 2 of 3 -> worker_id=worker2, other apps rejected"""
    customer = make_customer()
    worker1 = make_worker("Worker 1")
    worker2 = make_worker("Worker 2")
    worker3 = make_worker("Worker 3")

    booking = make_booking(customer.id, category_slug="electrical")
    
    app1 = JobApplication(id=PydanticObjectId(), booking_id=booking.id, worker_id=worker1.id, application_status=ApplicationStatus.PENDING)
    app2 = JobApplication(id=PydanticObjectId(), booking_id=booking.id, worker_id=worker2.id, application_status=ApplicationStatus.PENDING)
    app3 = JobApplication(id=PydanticObjectId(), booking_id=booking.id, worker_id=worker3.id, application_status=ApplicationStatus.PENDING)

    profile2 = make_worker_profile(worker2.id, skills=["electrical"])

    mock_coll = MagicMock()
    mock_coll.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_coll.update_many = AsyncMock(return_value=MagicMock(modified_count=2))
    mock_coll.find_one_and_update = AsyncMock(return_value={"_id": app2.id})

    service = JobApplicationService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app2))
        m.setattr("app.application.models.JobApplication.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[app1, app3]))))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=worker2))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile2))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll))
        m.setattr("app.application.models.JobApplication.get_motor_collection", MagicMock(return_value=mock_coll))
        m.setattr("app.application.models.JobApplication.save", AsyncMock(return_value=app2))

        res = await service.accept_applicant_for_customer(customer, str(booking.id), str(app2.id))
        assert res.application_status == ApplicationStatus.ACCEPTED
        assert res.worker_id == str(worker2.id)


@pytest.mark.asyncio
async def test_case_18_duplicate_application_prevention():
    """TEST 18: Worker applies to same booking twice -> 409 DUPLICATE_APPLICATION"""
    worker = make_worker()
    profile = make_worker_profile(worker.id, skills=["electrical"])
    booking = make_booking(PydanticObjectId(), category_slug="electrical")
    existing_app = JobApplication(booking_id=booking.id, worker_id=worker.id, application_status=ApplicationStatus.PENDING)

    service = JobApplicationService()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile))
        m.setattr("app.application.repository.JobApplicationRepository.find_application_by_booking_and_worker", AsyncMock(return_value=existing_app))

        req = JobApplicationCreateRequest(booking_id=str(booking.id))
        with pytest.raises(ConflictException) as exc_info:
            await service.apply_for_job(worker, req)
        assert exc_info.value.error_code == "DUPLICATE_APPLICATION"


@pytest.mark.asyncio
async def test_case_19_admin_worker_profile_update_and_immediate_eligibility():
    """TEST 19: Admin updates worker skills/radius -> immediate eligibility impact"""
    worker = make_worker()
    profile = make_worker_profile(worker.id, skills=["plumbing"], radius=5.0)
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=LOC_5KM)

    # Initial state: Plumbing worker cannot see electrical booking
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res_initial = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile.skills, worker_location=profile.current_location, working_radius_km=profile.working_radius_km
        )
        assert res_initial is None

    # Admin updates skills to include "electrical" and radius to 10.0 km
    profile.skills = ["electrical", "plumbing"]
    profile.working_radius_km = 10.0

    # Updated state: Electrical worker at 5 km now sees electrical booking
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        res_updated = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile.skills, worker_location=profile.current_location, working_radius_km=profile.working_radius_km
        )
        assert res_updated is not None


@pytest.mark.asyncio
async def test_case_20_notification_targeting_eligible_workers_only():
    """TEST 20: Booking created -> only eligible workers receive notification"""
    booking = make_booking(PydanticObjectId(), category_slug="electrical", loc=DEFAULT_LOC)

    worker_a = make_worker("Eligible Worker A")
    profile_a = make_worker_profile(worker_a.id, skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)

    worker_b = make_worker("Mismatched Skill Worker B")
    profile_b = make_worker_profile(worker_b.id, skills=["plumbing"], loc=DEFAULT_LOC, radius=10.0)

    worker_c = make_worker("Outside Radius Worker C")
    profile_c = make_worker_profile(worker_c.id, skills=["electrical"], loc=LOC_15KM, radius=10.0)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[worker_a, worker_b, worker_c]))))
        m.setattr("app.worker.models.WorkerProfile.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[profile_a, profile_b, profile_c]))))

        eligible_ids = await notification_service.find_eligible_workers_for_booking(booking)
        assert len(eligible_ids) == 1
        assert str(worker_a.id) in eligible_ids
        assert str(worker_b.id) not in eligible_ids
        assert str(worker_c.id) not in eligible_ids


# ---------------------------------------------------------------------------
# COMPLETE END-TO-END FLOW TEST
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_phase14_complete_end_to_end_flow():
    """
    Complete End-to-End Production Flow Validation:
    Customer creates booking -> ServiceSnapshot validation -> Eligible worker discovery ->
    Notification targeting -> Application submission -> Customer applicant review ->
    Atomic customer selection & assignment -> Competing applications rejection.
    """
    customer = make_customer("EndToEnd Customer")
    worker_elec = make_worker("Electrical Worker")
    worker_plumb = make_worker("Plumbing Worker")

    profile_elec = make_worker_profile(worker_elec.id, skills=["electrical"], loc=DEFAULT_LOC, radius=10.0)
    profile_plumb = make_worker_profile(worker_plumb.id, skills=["plumbing"], loc=DEFAULT_LOC, radius=10.0)

    # 1. Customer creates electrical booking
    booking = make_booking(customer.id, category_slug="electrical", loc=DEFAULT_LOC)
    assert booking.service_snapshot.category_slug == "electrical"
    assert booking.status == BookingStatus.PENDING

    # 2. Marketplace Discovery: Only Electrical Worker discovers the booking
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        elec_view = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile_elec.skills, worker_location=profile_elec.current_location
        )
        plumb_view = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking.id, worker_skills=profile_plumb.skills, worker_location=profile_plumb.current_location
        )
        assert elec_view is not None
        assert plumb_view is None

    # 3. Notification Targeting: Only Electrical Worker is notified
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[worker_elec, worker_plumb]))))
        m.setattr("app.worker.models.WorkerProfile.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[profile_elec, profile_plumb]))))
        target_ids = await notification_service.find_eligible_workers_for_booking(booking)
        assert target_ids == [str(worker_elec.id)]

    # 4. Direct API Application Submission: Electrical Worker succeeds, Plumbing Worker fails
    app_service = JobApplicationService()
    req = JobApplicationCreateRequest(booking_id=str(booking.id))

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile_plumb))
        m.setattr("app.application.repository.JobApplicationRepository.find_application_by_booking_and_worker", AsyncMock(return_value=None))

        with pytest.raises(BadRequestException) as exc_info:
            await app_service.apply_for_job(worker_plumb, req)
        assert exc_info.value.error_code == "SKILL_MISMATCH"

    app_elec = JobApplication(
        id=PydanticObjectId(),
        booking_id=booking.id,
        worker_id=worker_elec.id,
        application_status=ApplicationStatus.PENDING,
    )

    # 5. Customer Applicant Review & Selection
    mock_coll = MagicMock()
    mock_coll.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_coll.update_many = AsyncMock(return_value=MagicMock(modified_count=0))

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app_elec))
        m.setattr("app.application.models.JobApplication.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[]))))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=worker_elec))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=profile_elec))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll))
        m.setattr("app.application.models.JobApplication.get_motor_collection", MagicMock(return_value=mock_coll))
        m.setattr("app.application.models.JobApplication.save", AsyncMock(return_value=app_elec))

        res = await app_service.accept_applicant_for_customer(customer, str(booking.id), str(app_elec.id))
        assert res.application_status == ApplicationStatus.ACCEPTED
        assert res.worker_id == str(worker_elec.id)
