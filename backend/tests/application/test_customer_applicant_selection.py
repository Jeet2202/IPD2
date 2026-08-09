"""
Unit tests for Phase 9 Customer Applicant Review & Worker Assignment Logic.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import GeoJSONPoint
from app.application.models import JobApplication
from app.application.service import JobApplicationService
from app.auth.models import User, UserRole
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.utils.enums import ApplicationStatus, BookingStatus, BookingType, InspectionStatus, WorkerAvailability
from app.worker.models import WorkerProfile

BANGALORE_CENTER_LAT = 12.9716
BANGALORE_CENTER_LNG = 77.5946
DEFAULT_LOC = GeoJSONPoint.from_lat_lng(latitude=BANGALORE_CENTER_LAT, longitude=BANGALORE_CENTER_LNG)
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
    mock_db.__getitem__ = MagicMock(return_value=mock_coll)

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, JobApplication])


def create_customer(name: str = "Customer 1") -> User:
    uid = PydanticObjectId()
    return User(
        id=uid,
        email=f"cust_{uid}@example.com",
        phone=f"+9198{str(uid)[:8]}",
        password_hash="hash",
        full_name=name,
        role=UserRole.CUSTOMER,
        is_active=True,
    )


def create_worker(name: str = "Worker 1", active: bool = True) -> User:
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


def create_worker_profile(user_id: PydanticObjectId, skills: list[str], loc: GeoJSONPoint | None = DEFAULT_LOC, radius: float = 10.0, completed: bool = True, is_verified: bool = True) -> WorkerProfile:
    return WorkerProfile(
        id=PydanticObjectId(),
        user_id=user_id,
        skills=skills,
        profile_completed=completed,
        availability=WorkerAvailability.AVAILABLE,
        current_location=loc,
        working_radius_km=radius,
        is_verified=is_verified,
    )


def create_booking(customer_id: PydanticObjectId, category_slug: str = "electrical", status: BookingStatus = BookingStatus.PENDING, worker_id: PydanticObjectId | None = None, loc: GeoJSONPoint = DEFAULT_LOC) -> Booking:
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
            name="Electrical Inspection",
            category_id="cat_1",
            category_slug=category_slug,
            required_skills=[],
            base_market_price=500.0,
            estimated_duration_minutes=60,
        ),
        address_snapshot=AddressSnapshot(
            address_id="addr_1",
            label="Home",
            full_name="Customer Name",
            phone="+919876543210",
            address_line_1="Line 1",
            city="Bangalore",
            state="Karnataka",
            postal_code="560001",
            location=loc,
        ),
        estimated_price=500.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )


def create_application(booking_id: PydanticObjectId, worker_id: PydanticObjectId, app_status: ApplicationStatus = ApplicationStatus.PENDING) -> JobApplication:
    return JobApplication(
        id=PydanticObjectId(),
        booking_id=booking_id,
        worker_id=worker_id,
        application_status=app_status,
        cover_letter="I am experienced",
        applied_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_1_customer_views_applicants_own_booking():
    cust = create_customer()
    booking = create_booking(cust.id)
    w1 = create_worker("Worker 1")
    p1 = create_worker_profile(w1.id, ["electrical"])
    app1 = create_application(booking.id, w1.id)

    mock_find_apps = MagicMock()
    mock_find_apps.sort = MagicMock(return_value=mock_find_apps)
    mock_find_apps.to_list = AsyncMock(return_value=[app1])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.find", MagicMock(return_value=mock_find_apps))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w1))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p1))

        svc = JobApplicationService()
        res = await svc.list_booking_applicants_for_customer(cust, str(booking.id))
        assert res.applicant_count == 1
        assert res.applicants[0].worker_id == str(w1.id)


@pytest.mark.asyncio
async def test_2_customer_views_applicants_other_customer_forbidden():
    cust1 = create_customer("Cust 1")
    cust2 = create_customer("Cust 2")
    booking = create_booking(cust1.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))

        svc = JobApplicationService()
        with pytest.raises(ForbiddenException) as exc_info:
            await svc.list_booking_applicants_for_customer(cust2, str(booking.id))

        assert exc_info.value.error_code == "BOOKING_NOT_OWNED"


@pytest.mark.asyncio
async def test_3_and_4_customer_accepts_valid_applicant_others_rejected():
    cust = create_customer()
    booking = create_booking(cust.id)

    w1 = create_worker("Worker 1")
    p1 = create_worker_profile(w1.id, ["electrical"])
    app1 = create_application(booking.id, w1.id)

    w2 = create_worker("Worker 2")
    p2 = create_worker_profile(w2.id, ["electrical"])
    app2 = create_application(booking.id, w2.id)

    mock_coll = MagicMock()
    mock_coll.update_one = AsyncMock(return_value=MagicMock(modified_count=1))

    mock_other_find = MagicMock()
    mock_other_find.to_list = AsyncMock(return_value=[app2])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app1))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w1))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p1))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll))
        m.setattr("app.application.models.JobApplication.save", AsyncMock(return_value=app1))
        m.setattr("app.application.models.JobApplication.find", MagicMock(return_value=mock_other_find))

        svc = JobApplicationService()
        res = await svc.accept_applicant_for_customer(cust, str(booking.id), str(app1.id))

        assert res.worker_id == str(w1.id)
        assert res.application_status == ApplicationStatus.ACCEPTED
        assert app2.application_status == ApplicationStatus.REJECTED


@pytest.mark.asyncio
async def test_5_customer_accepts_applicant_wrong_booking():
    cust = create_customer()
    b1 = create_booking(cust.id)
    b2_id = PydanticObjectId()
    w1 = create_worker()
    app_other = create_application(b2_id, w1.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=b1))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app_other))

        svc = JobApplicationService()
        with pytest.raises(NotFoundException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(b1.id), str(app_other.id))

        assert exc_info.value.error_code == "APPLICATION_NOT_FOUND"


@pytest.mark.asyncio
async def test_6_customer_accepts_already_assigned_booking():
    cust = create_customer()
    assigned_b = create_booking(cust.id, status=BookingStatus.ASSIGNED, worker_id=PydanticObjectId())
    w1 = create_worker()
    app1 = create_application(assigned_b.id, w1.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=assigned_b))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(assigned_b.id), str(app1.id))

        assert exc_info.value.error_code == "BOOKING_NOT_AVAILABLE"


@pytest.mark.asyncio
async def test_7_and_8_customer_accepts_non_pending_application():
    cust = create_customer()
    booking = create_booking(cust.id)
    w1 = create_worker()
    app_rejected = create_application(booking.id, w1.id, app_status=ApplicationStatus.REJECTED)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app_rejected))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(booking.id), str(app_rejected.id))

        assert exc_info.value.error_code == "APPLICATION_NOT_PENDING"


@pytest.mark.asyncio
async def test_9_ineligible_worker_skill_rejected():
    cust = create_customer()
    elec_booking = create_booking(cust.id, category_slug="electrical")
    w_plumber = create_worker("Plumber")
    p_plumber = create_worker_profile(w_plumber.id, ["plumbing"])
    app = create_application(elec_booking.id, w_plumber.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=elec_booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_plumber))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p_plumber))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(elec_booking.id), str(app.id))

        assert exc_info.value.error_code == "SKILL_MISMATCH"


@pytest.mark.asyncio
async def test_10_worker_outside_radius_rejected():
    cust = create_customer()
    far_booking = create_booking(cust.id, loc=LOC_15KM)
    w = create_worker()
    p = create_worker_profile(w.id, ["electrical"], loc=DEFAULT_LOC, radius=10.0)
    app = create_application(far_booking.id, w.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=far_booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(far_booking.id), str(app.id))

        assert exc_info.value.error_code == "OUTSIDE_SERVICE_RADIUS"


@pytest.mark.asyncio
async def test_11_worker_no_location_rejected():
    cust = create_customer()
    booking = create_booking(cust.id)
    w = create_worker()
    p = create_worker_profile(w.id, ["electrical"], loc=None)
    app = create_application(booking.id, w.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(booking.id), str(app.id))

        assert exc_info.value.error_code == "WORKER_LOCATION_REQUIRED"


@pytest.mark.asyncio
async def test_12_worker_profile_incomplete_rejected():
    cust = create_customer()
    booking = create_booking(cust.id)
    w = create_worker()
    p = create_worker_profile(w.id, ["electrical"], completed=False)
    app = create_application(booking.id, w.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p))

        svc = JobApplicationService()
        with pytest.raises((BadRequestException, ForbiddenException)) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(booking.id), str(app.id))

        assert exc_info.value.error_code in ("PROFILE_INCOMPLETE", "WORKER_PROFILE_INCOMPLETE")


@pytest.mark.asyncio
async def test_13_inactive_worker_rejected():
    cust = create_customer()
    booking = create_booking(cust.id)
    w_inactive = create_worker("Inactive", active=False)
    p = create_worker_profile(w_inactive.id, ["electrical"])
    app = create_application(booking.id, w_inactive.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_inactive))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(booking.id), str(app.id))

        assert exc_info.value.error_code == "WORKER_NOT_AVAILABLE"


@pytest.mark.asyncio
async def test_14_concurrent_customer_acceptance_race_atomic_protection():
    cust = create_customer()
    booking = create_booking(cust.id)

    w1 = create_worker("Worker 1")
    p1 = create_worker_profile(w1.id, ["electrical"])
    app1 = create_application(booking.id, w1.id)

    w2 = create_worker("Worker 2")
    p2 = create_worker_profile(w2.id, ["electrical"])

    mock_coll1 = MagicMock()
    mock_coll1.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_coll2 = MagicMock()
    mock_coll2.update_one = AsyncMock(return_value=MagicMock(modified_count=0))

    mock_other_find = MagicMock()
    mock_other_find.to_list = AsyncMock(return_value=[])

    assigned_b = create_booking(cust.id, status=BookingStatus.ASSIGNED, worker_id=w1.id)

    # First acceptance succeeds
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app1))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w1))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p1))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll1))
        m.setattr("app.application.models.JobApplication.save", AsyncMock(return_value=app1))
        m.setattr("app.application.models.JobApplication.find", MagicMock(return_value=mock_other_find))

        svc = JobApplicationService()
        res1 = await svc.accept_applicant_for_customer(cust, str(booking.id), str(app1.id))
        assert res1.worker_id == str(w1.id)

    # Second acceptance loses race atomically because booking was assigned
    app2_pending = create_application(booking.id, w2.id)
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(side_effect=[booking, assigned_b]))
        m.setattr("app.application.models.JobApplication.get", AsyncMock(return_value=app2_pending))
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w2))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=p2))
        m.setattr("app.booking.models.Booking.get_motor_collection", MagicMock(return_value=mock_coll2))

        svc = JobApplicationService()
        with pytest.raises(ConflictException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(booking.id), str(app2_pending.id))

        assert exc_info.value.error_code == "BOOKING_ALREADY_ASSIGNED"


@pytest.mark.asyncio
async def test_15_cancelled_booking_acceptance_rejected():
    cust = create_customer()
    cancelled_b = create_booking(cust.id, status=BookingStatus.CANCELLED)
    w = create_worker()
    app = create_application(cancelled_b.id, w.id)

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=cancelled_b))

        svc = JobApplicationService()
        with pytest.raises(BadRequestException) as exc_info:
            await svc.accept_applicant_for_customer(cust, str(cancelled_b.id), str(app.id))

        assert exc_info.value.error_code == "BOOKING_NOT_AVAILABLE"
