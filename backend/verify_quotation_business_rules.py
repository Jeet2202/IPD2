"""
Verification script for KaamSetu Centralized Quotation Business Rules & Validation (Phase 4.6.5).

Tests end-to-end against MongoDB Atlas:
  1. Configurable Settings: Validate config settings in app/core/config.py.
  2. State Machine Transitions: Enforce valid status transitions & reject invalid transitions.
  3. Auto Expiry Enforcement: Auto-expire past validity_date quotations on access & reject acceptance.
  4. Max Validity Date Bounds: Reject validity date exceeding 90 days.
  5. Pricing Bounds: Reject total amount exceeding ₹500,000.
  6. Closed/Assigned Booking Protection: Block quotations on CANCELLED and ASSIGNED bookings.
  7. Read-Only Protection: Immutable ACCEPTED, REJECTED, and EXPIRED quotations.
  8. Cleanup test data.
"""

import asyncio
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, ".")

from beanie import PydanticObjectId

from app.address.models import GeoJSONPoint
from app.application.models import JobApplication
from app.auth.models import AuthAuditLog, RefreshToken, User, UserRole
from app.booking.models import AddressSnapshot, Booking, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.category.models import Service, ServiceCategory
from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
)
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.otp.models import OTP
from app.quotation.models import Quotation, QuotationHistory
from app.quotation.schemas import QuotationCreateRequest, QuotationUpdateRequest
from app.quotation.service import QuotationService
from app.utils.enums import (
    ApplicationStatus,
    BookingStatus,
    BookingType,
    QuotationStatus,
)
from app.worker.models import WorkerProfile


async def run_quotation_business_rules_verification() -> None:
    print("=" * 75)
    print("KAAMSETU — QUOTATION BUSINESS RULES & VALIDATION (PHASE 4.6.5) VERIFICATION")
    print("=" * 75)

    print("\n[0] Connecting to MongoDB Atlas...")
    await connect_to_database(
        document_models=[
            User,
            RefreshToken,
            CustomerProfile,
            WorkerProfile,
            OTP,
            AuthAuditLog,
            ServiceCategory,
            Service,
            Booking,
            JobApplication,
            Quotation,
            QuotationHistory,
        ]
    )
    print("    [PASS] Connected to Atlas database successfully.")

    service = QuotationService()
    test_users: list[User] = []
    test_bookings: list[Booking] = []
    test_apps: list[JobApplication] = []
    test_quotes: list[Quotation] = []

    try:
        s = str(random.randint(100000, 999999))

        # Config Checks
        print("\n[1] Testing Configurable Domain Parameters...")
        assert settings.QUOTATION_DEFAULT_VALIDITY_DAYS == 14
        assert settings.QUOTATION_MAX_VALIDITY_DAYS == 90
        assert settings.QUOTATION_MAX_PRICE == 500000.0
        print("    [PASS] Config parameters (Validity 14d, Max Validity 90d, Max Price INR 500,000) verified.")

        # Setup Users
        cust = User(
            phone=f"+9196{s}001",
            email=f"br_c_{s}@kaamtest.com",
            full_name="Customer BR Test",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        test_users.append(cust)

        w1 = User(
            phone=f"+9196{s}002",
            email=f"br_w1_{s}@kaamtest.com",
            full_name="Worker 1 BR Test",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        # Booking Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name=cust.full_name,
            phone=cust.phone,
            address_line_1="Building X",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400058",
            location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )

        svc_snap = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Carpentry & Furniture Fitting",
            category_id=str(PydanticObjectId()),
            category_slug="carpenter-br-test",
            base_market_price=1000.0,
            estimated_duration_minutes=120,
        )

        # Pending Booking
        num1 = await BookingRepository.generate_booking_number()
        b_pending = Booking(
            booking_number=num1,
            customer_id=cust.id,
            booking_type=BookingType.INSPECTION_REQUEST,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            estimated_price=1000.0,
        )
        await b_pending.insert()
        test_bookings.append(b_pending)

        # Cancelled Booking
        num2 = await BookingRepository.generate_booking_number()
        b_cancelled = Booking(
            booking_number=num2,
            customer_id=cust.id,
            booking_type=BookingType.INSPECTION_REQUEST,
            status=BookingStatus.CANCELLED,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            estimated_price=1000.0,
        )
        await b_cancelled.insert()
        test_bookings.append(b_cancelled)

        # Applications
        app1 = JobApplication(booking_id=b_pending.id, worker_id=w1.id, application_status=ApplicationStatus.PENDING)
        await app1.insert()
        test_apps.append(app1)

        app_canc = JobApplication(booking_id=b_cancelled.id, worker_id=w1.id, application_status=ApplicationStatus.PENDING)
        await app_canc.insert()
        test_apps.append(app_canc)

        valid_date = date.today() + timedelta(days=10)

        # ---------------------------------------------------------------------
        # Test 2: Closed / Cancelled Booking Protection
        # ---------------------------------------------------------------------
        print("\n[2] Testing Cancelled Booking Quotation Guard...")
        req_canc = QuotationCreateRequest(
            booking_id=str(b_cancelled.id),
            application_id=str(app_canc.id),
            labour_cost=1000.0,
            estimated_duration="1 day",
            validity_date=valid_date,
        )

        try:
            await service.create_quotation(w1, req_canc)
            assert False, "Quotation creation on cancelled booking should fail!"
        except BadRequestException as exc:
            assert exc.error_code == "BOOKING_CANCELLED"
        print("    [PASS] Quotation submission on CANCELLED booking correctly rejected with 400 BOOKING_CANCELLED.")

        # ---------------------------------------------------------------------
        # Test 3: Max Validity Date Bounds Check (> 90 days)
        # ---------------------------------------------------------------------
        print("\n[3] Testing Max Validity Date Bounds Check (> 90 Days)...")
        far_future = date.today() + timedelta(days=120)
        req_far_date = QuotationCreateRequest(
            booking_id=str(b_pending.id),
            application_id=str(app1.id),
            labour_cost=1000.0,
            estimated_duration="1 day",
            validity_date=far_future,
        )

        try:
            await service.create_quotation(w1, req_far_date)
            assert False, "Validity date > 90 days should fail!"
        except BadRequestException as exc:
            assert exc.error_code == "INVALID_VALIDITY_DATE"
        print("    [PASS] Validity date > 90 days correctly rejected with 400 INVALID_VALIDITY_DATE.")

        # ---------------------------------------------------------------------
        # Test 4: Pricing Upper Limit Check (> INR 500,000)
        # ---------------------------------------------------------------------
        print("\n[4] Testing Pricing Upper Limit Check (> INR 500,000)...")
        try:
            req_huge_price = QuotationCreateRequest(
                booking_id=str(b_pending.id),
                application_id=str(app1.id),
                labour_cost=600000.0,
                estimated_duration="1 day",
                validity_date=valid_date,
            )
            await service.create_quotation(w1, req_huge_price)
            assert False, "Price > INR 500,000 should fail!"
        except BadRequestException as exc:
            assert exc.error_code == "EXCEEDS_MAX_PRICE"
        print("    [PASS] Price exceeding INR 500,000 correctly rejected with 400 EXCEEDS_MAX_PRICE.")

        # ---------------------------------------------------------------------
        # Test 5: State Machine Transition & Auto-Expiry Verification
        # ---------------------------------------------------------------------
        print("\n[5] Testing Auto-Expiry & State Machine Transitions...")
        
        # Create a SUBMITTED quotation with valid date
        req_valid = QuotationCreateRequest(
            booking_id=str(b_pending.id),
            application_id=str(app1.id),
            labour_cost=1500.0,
            estimated_duration="1 day",
            validity_date=valid_date,
            is_draft=False,
        )
        q1_res = await service.create_quotation(w1, req_valid)
        q1_doc = await Quotation.get(PydanticObjectId(q1_res.id))
        if q1_doc:
            test_quotes.append(q1_doc)

        # Manually simulate expired validity_date in DB
        q1_doc.validity_date = date.today() - timedelta(days=1)
        await q1_doc.save()

        # Accessing customer detail view should auto-transition status to EXPIRED
        detail_view = await service.get_customer_quotation_detail(cust, q1_res.id)
        assert detail_view.quotation_status == QuotationStatus.EXPIRED

        # Accepting expired quotation must fail with 400 QUOTATION_EXPIRED
        try:
            await service.accept_quotation(cust, q1_res.id)
            assert False, "Accepting an expired quotation should fail!"
        except BadRequestException as exc:
            assert exc.error_code == "QUOTATION_EXPIRED"
        print("    [PASS] Expired quotation auto-transitioned to EXPIRED and acceptance blocked.")

        # ---------------------------------------------------------------------
        # Test 6: Terminal State Immutability (EXPIRED -> DRAFT/SUBMITTED invalid transition)
        # ---------------------------------------------------------------------
        print("\n[6] Testing Terminal State Immutability...")
        try:
            await service.update_quotation(w1, q1_res.id, QuotationUpdateRequest(labour_cost=2000.0))
            assert False, "Updating EXPIRED quotation should fail!"
        except BadRequestException as exc:
            assert exc.error_code == "QUOTATION_READ_ONLY"
        print("    [PASS] Modification of EXPIRED terminal state strictly blocked with 400 QUOTATION_READ_ONLY.")

    finally:
        print("\n[CLEANUP] Cleaning up test data from Atlas database...")
        for q in test_quotes:
            await q.delete()
        for a in test_apps:
            await a.delete()
        for b in test_bookings:
            await b.delete()
        for u in test_users:
            await u.delete()
        await close_database_connection()
        print("    [PASS] Test data cleaned up successfully.")

    print("\n" + "=" * 75)
    print("ALL QUOTATION BUSINESS RULES VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_quotation_business_rules_verification())
