"""
Phase 12 — Admin Worker Management Unit & Integration Test Suite.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie
from pydantic import ValidationError
from fastapi import HTTPException

from app.address.models import GeoJSONPoint
from app.admin.models import WorkerVerification
from app.admin.router import AdminWorkerProfileUpdateRequest, update_worker_profile_by_admin, get_worker_details
from app.auth.models import User, UserRole
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.category.models import ServiceCategory
from app.marketplace.repository import MarketplaceRepository
from app.utils.enums import BookingStatus, BookingType, InspectionStatus, WorkerAvailability
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

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, ServiceCategory, WorkerVerification])


def create_admin_user() -> User:
    return User(
        id=PydanticObjectId(),
        email="admin@kaamsetu.com",
        phone="+919999999999",
        password_hash="hash",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
    )


def create_worker_user() -> tuple[User, WorkerProfile]:
    uid = PydanticObjectId()
    user = User(
        id=uid,
        email=f"worker_{uid}@example.com",
        phone="+919876543210",
        password_hash="hash",
        full_name="Worker User",
        role=UserRole.WORKER,
        is_active=True,
    )
    profile = WorkerProfile(
        id=PydanticObjectId(),
        user_id=uid,
        skills=["electrical"],
        working_radius_km=10.0,
        profile_completed=True,
        availability=WorkerAvailability.AVAILABLE,
        is_verified=True,
        current_location=DEFAULT_LOC,
    )
    return user, profile


# =============================================================================
# TESTS 1 - 9: ADMIN WORKER MANAGEMENT API & VALIDATION
# =============================================================================

@pytest.mark.asyncio
async def test_1_admin_gets_real_worker_details():
    admin = create_admin_user()
    w_user, w_prof = create_worker_user()

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))
        m.setattr("app.admin.models.WorkerVerification.find_one", AsyncMock(return_value=None))

        res = await get_worker_details(str(w_user.id), admin)
        assert res["id"] == str(w_user.id)
        assert res["full_name"] == w_user.full_name
        assert res["skills"] == ["electrical"]
        assert res["working_radius_km"] == 10.0


@pytest.mark.asyncio
async def test_2_3_admin_updates_and_normalizes_skills():
    admin = create_admin_user()
    w_user, w_prof = create_worker_user()

    payload = AdminWorkerProfileUpdateRequest(
        skills=[" Electrical ", "PLUMBING", "electrical"],
        working_radius_km=15.0,
    )

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))
        m.setattr("app.worker.models.WorkerProfile.save", AsyncMock(return_value=w_prof))
        m.setattr("app.category.models.ServiceCategory.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[]))))

        res = await update_worker_profile_by_admin(str(w_user.id), payload, admin)
        assert res["skills"] == ["electrical", "plumbing"]
        assert res["working_radius_km"] == 15.0
        assert w_prof.skills == ["electrical", "plumbing"]
        assert w_prof.working_radius_km == 15.0


@pytest.mark.asyncio
async def test_4_admin_submits_invalid_skill_slug_rejected():
    admin = create_admin_user()
    w_user, w_prof = create_worker_user()

    payload = AdminWorkerProfileUpdateRequest(skills=["invalid-skill-xyz"])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))
        m.setattr("app.category.models.ServiceCategory.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[]))))

        with pytest.raises(HTTPException) as exc_info:
            await update_worker_profile_by_admin(str(w_user.id), payload, admin)

        assert exc_info.value.status_code == 400
        assert "Invalid worker skill" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_5_admin_submits_empty_skills_clears_skills():
    admin = create_admin_user()
    w_user, w_prof = create_worker_user()

    payload = AdminWorkerProfileUpdateRequest(skills=[])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))
        m.setattr("app.worker.models.WorkerProfile.save", AsyncMock(return_value=w_prof))
        m.setattr("app.category.models.ServiceCategory.find", MagicMock(return_value=MagicMock(to_list=AsyncMock(return_value=[]))))

        res = await update_worker_profile_by_admin(str(w_user.id), payload, admin)
        assert res["skills"] == []
        assert w_prof.skills == []


@pytest.mark.asyncio
async def test_6_7_admin_working_radius_validation():
    admin = create_admin_user()
    w_user, w_prof = create_worker_user()

    # Valid radius
    payload_valid = AdminWorkerProfileUpdateRequest(working_radius_km=25.0)
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=w_user))
        m.setattr("app.worker.models.WorkerProfile.find_one", AsyncMock(return_value=w_prof))
        m.setattr("app.worker.models.WorkerProfile.save", AsyncMock(return_value=w_prof))

        res = await update_worker_profile_by_admin(str(w_user.id), payload_valid, admin)
        assert res["working_radius_km"] == 25.0

    # Invalid radius (<= 0) is caught by Pydantic schema validation
    with pytest.raises(ValidationError):
        AdminWorkerProfileUpdateRequest(working_radius_km=0.0)


@pytest.mark.asyncio
async def test_9_unknown_worker_returns_404():
    admin = create_admin_user()
    payload = AdminWorkerProfileUpdateRequest(skills=["electrical"])

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.auth.models.User.get", AsyncMock(return_value=None))
        m.setattr("app.worker.models.WorkerProfile.get", AsyncMock(return_value=None))

        with pytest.raises(HTTPException) as exc_info:
            await update_worker_profile_by_admin(str(PydanticObjectId()), payload, admin)
        assert exc_info.value.status_code == 404


# =============================================================================
# TESTS 10 & 11: MARKETPLACE MATCHING IMMEDIATE IMPACT
# =============================================================================

@pytest.mark.asyncio
async def test_10_skill_update_impacts_marketplace_eligibility():
    _, w_prof = create_worker_user()
    w_prof.skills = ["plumbing"]

    elec_booking = Booking(
        id=PydanticObjectId(),
        booking_number="BK-ELE",
        customer_id=PydanticObjectId(),
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        inspection_status=InspectionStatus.NOT_REQUIRED,
        service_location=DEFAULT_LOC,
        service_snapshot=ServiceSnapshot(
            service_id="s1", name="Electrical", category_id="c1", category_slug="electrical", required_skills=[], base_market_price=100.0, estimated_duration_minutes=60
        ),
        address_snapshot=AddressSnapshot(
            address_id="a1", label="Home", full_name="Cust", phone="+919876543210", address_line_1="L1", city="Blr", state="KA", postal_code="560001", location=DEFAULT_LOC
        ),
        estimated_price=100.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=elec_booking))

        # Before update: Plumbing worker cannot access electrical booking
        res_before = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking_id=elec_booking.id,
            worker_skills=w_prof.skills,
            worker_location=DEFAULT_LOC,
            working_radius_km=10.0,
        )
        assert res_before is None

        # Admin updates worker skills to electrical
        w_prof.skills = ["electrical"]

        # After update: Worker is eligible
        res_after = await MarketplaceRepository.get_marketplace_booking_by_id(
            booking_id=elec_booking.id,
            worker_skills=w_prof.skills,
            worker_location=DEFAULT_LOC,
            working_radius_km=10.0,
        )
        assert res_after is not None
