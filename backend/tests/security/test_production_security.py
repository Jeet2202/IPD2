"""
Comprehensive Security Test Suite — Phase 10 Production Security Hardening.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from beanie import PydanticObjectId, init_beanie

from app.address.models import GeoJSONPoint
from app.application.models import JobApplication
from app.auth.exceptions import AuthenticationError, InvalidTokenError, TokenExpiredError
from app.auth.models import User, UserRole
from app.auth.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.marketplace.rules import MarketplaceRulesEngine
from app.otp.service import OTPService
from app.payments.service import razorpay_service
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

    await init_beanie(database=mock_db, document_models=[WorkerProfile, User, Booking, JobApplication])


# =============================================================================
# AUTHENTICATION SECURITY TESTS (1-6)
# =============================================================================

def test_1_valid_password_hashing_and_verification():
    raw_pwd = "StrongPassword123!"
    hashed = hash_password(raw_pwd)
    assert hashed != raw_pwd
    assert verify_password(raw_pwd, hashed) is True


def test_2_invalid_password_verification_fails():
    hashed = hash_password("StrongPassword123!")
    assert verify_password("WrongPassword123!", hashed) is False


def test_3_expired_access_token_fails():
    uid = str(PydanticObjectId())
    token = create_access_token(uid, UserRole.CUSTOMER, expires_delta=timedelta(seconds=-10))
    with pytest.raises(TokenExpiredError):
        decode_token(token, expected_type="access")


def test_4_malformed_jwt_fails():
    with pytest.raises(InvalidTokenError):
        decode_token("invalid.jwt.token", expected_type="access")


def test_5_wrong_token_type_fails():
    uid = str(PydanticObjectId())
    refresh = create_refresh_token(uid, UserRole.CUSTOMER)
    with pytest.raises(InvalidTokenError) as exc_info:
        decode_token(refresh, expected_type="access")
    assert exc_info.value.error_code == "TOKEN_TYPE_MISMATCH"


# =============================================================================
# AUTHORIZATION & IDOR SECURITY TESTS (7-13)
# =============================================================================

@pytest.mark.asyncio
async def test_7_8_role_authorization_guards():
    from app.auth.dependencies import get_current_customer, get_current_worker

    cust_user = User(
        id=PydanticObjectId(),
        email="cust@example.com",
        phone="+919876543210",
        password_hash="hash",
        full_name="Cust",
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    work_user = User(
        id=PydanticObjectId(),
        email="work@example.com",
        phone="+919876543211",
        password_hash="hash",
        full_name="Work",
        role=UserRole.WORKER,
        is_active=True,
    )

    # Customer accessing customer guard -> PASS
    assert (await get_current_customer(cust_user)).id == cust_user.id

    # Worker accessing customer guard -> FAIL (CUSTOMER_ROLE_REQUIRED)
    with pytest.raises(Exception) as exc1:
        await get_current_customer(work_user)

    # Customer accessing worker guard -> FAIL (WORKER_ROLE_REQUIRED)
    with pytest.raises(Exception) as exc2:
        await get_current_worker(cust_user)


@pytest.mark.asyncio
async def test_11_customer_idor_booking_isolation():
    from app.application.service import JobApplicationService

    c1_id = PydanticObjectId()
    c2_id = PydanticObjectId()

    cust2 = User(
        id=c2_id,
        email="c2@example.com",
        phone="+919876543212",
        password_hash="hash",
        full_name="Cust 2",
        role=UserRole.CUSTOMER,
        is_active=True,
    )

    booking_owner_c1 = Booking(
        id=PydanticObjectId(),
        booking_number="BK-100",
        customer_id=c1_id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        inspection_status=InspectionStatus.NOT_REQUIRED,
        service_location=DEFAULT_LOC,
        service_snapshot=ServiceSnapshot(
            service_id="s1", name="Service 1", category_id="cat1", category_slug="electrical", required_skills=[], base_market_price=100.0, estimated_duration_minutes=60
        ),
        address_snapshot=AddressSnapshot(
            address_id="a1", label="Home", full_name="Cust 1", phone="+919876543210", address_line_1="L1", city="Blr", state="KA", postal_code="560001", location=DEFAULT_LOC
        ),
        estimated_price=100.0,
        estimated_duration_minutes=60,
        created_at=datetime.now(timezone.utc),
    )

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.booking.models.Booking.get", AsyncMock(return_value=booking_owner_c1))

        svc = JobApplicationService()
        # Customer 2 attempting to list applicants of Customer 1's booking -> REJECTED
        with pytest.raises(ForbiddenException) as exc_info:
            await svc.list_booking_applicants_for_customer(cust2, str(booking_owner_c1.id))

        assert exc_info.value.error_code == "BOOKING_NOT_OWNED"


# =============================================================================
# MARKETPLACE SECURITY TESTS (14-19)
# =============================================================================

def test_14_wrong_skill_worker_application_rejected():
    w_user = User(
        id=PydanticObjectId(),
        email="worker@example.com",
        phone="+919876543210",
        password_hash="hash",
        full_name="Plumber",
        role=UserRole.WORKER,
        is_active=True,
    )
    p_plumber = WorkerProfile(
        id=PydanticObjectId(),
        user_id=w_user.id,
        skills=["plumbing"],
        profile_completed=True,
        availability=WorkerAvailability.AVAILABLE,
        current_location=DEFAULT_LOC,
        working_radius_km=10.0,
    )
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

    with pytest.raises(BadRequestException) as exc_info:
        MarketplaceRulesEngine.validate_worker_skill_eligibility(elec_booking, p_plumber)

    assert exc_info.value.error_code == "SKILL_MISMATCH"


# =============================================================================
# INPUT & NOSQL INJECTION PROTECTION (20-25)
# =============================================================================

def test_20_invalid_objectid_format_rejected():
    assert PydanticObjectId.is_valid("invalid_oid") is False


def test_23_invalid_coordinates_rejected():
    with pytest.raises(ValueError):
        GeoJSONPoint.from_lat_lng(latitude=95.0, longitude=77.5)


# =============================================================================
# FILE UPLOAD SECURITY TESTS (31-34)
# =============================================================================

@pytest.mark.asyncio
async def test_31_unsupported_file_mime_type_rejected():
    from fastapi import UploadFile, HTTPException
    from app.uploads.router import upload_general_media

    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/x-sh"
    mock_file.read = AsyncMock(return_value=b"echo 'malicious'")

    w_user = User(
        id=PydanticObjectId(),
        email="u@example.com",
        phone="+919876543210",
        password_hash="hash",
        full_name="User",
        role=UserRole.CUSTOMER,
        is_active=True,
    )

    with pytest.raises(HTTPException) as exc_info:
        await upload_general_media(mock_file, w_user)

    assert exc_info.value.status_code == 415


# =============================================================================
# PAYMENT SECURITY TESTS (35-38)
# =============================================================================

def test_35_invalid_razorpay_signature_rejected():
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.core.config.settings.RAZORPAY_KEY_SECRET", MagicMock(get_secret_value=lambda: "secret_key"))
        res = razorpay_service.verify_payment_signature(
            razorpay_order_id="order_123",
            razorpay_payment_id="pay_123",
            razorpay_signature="invalid_signature",
        )
        assert res is False
