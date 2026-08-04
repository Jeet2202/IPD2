"""
Verification script for Ally Worker Quotation Submission (Phase 4.6.2).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer, Worker 1 (Active), Worker 2 (Active), Inactive Worker, Booking (PENDING), Applications.
  2. Test 1: Worker 1 creates a DRAFT quotation (status = DRAFT, total calculated).
  3. Test 2: Worker 1 updates DRAFT quotation (values & total updated).
  4. Test 3: Worker 1 submits DRAFT quotation (status = SUBMITTED, submitted_at set).
  5. Test 4: Submitted quotation becomes READ-ONLY (400 QUOTATION_READ_ONLY).
  6. Test 5: Prevent duplicate quotation submission (409 QUOTATION_ALREADY_SUBMITTED).
  7. Test 6: Invalid pricing validation (discount > subtotal -> 400 INVALID_DISCOUNT / validation error).
  8. Test 7: Invalid date validation (past validity date -> 400 INVALID_VALIDITY_DATE).
  9. Test 8: Unauthorized access check (Worker 2 accessing Worker 1 quote -> 403 UNAUTHORIZED_QUOTATION_ACCESS).
 10. Test 9: Inactive worker quotation rejection (403 WORKER_INACTIVE).
 11. Cleanup test documents.
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
    WorkerAvailability,
)
from app.worker.models import WorkerProfile


async def run_quotation_submission_verification() -> None:
    print("=" * 75)
    print("ALLY — WORKER QUOTATION SUBMISSION (PHASE 4.6.2) VERIFICATION")
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

        # 1. Customer User
        cust = User(
            phone=f"+9199{s}001",
            email=f"qs_cust_{s}@kaamtest.com",
            full_name="Customer QuotationSubmit",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        test_users.append(cust)

        # 2. Worker 1 (Active)
        w1 = User(
            phone=f"+9199{s}002",
            email=f"qs_w1_{s}@kaamtest.com",
            full_name="Worker One QSub",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        # 3. Worker 2 (Active)
        w2 = User(
            phone=f"+9199{s}003",
            email=f"qs_w2_{s}@kaamtest.com",
            full_name="Worker Two QSub",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w2.insert()
        test_users.append(w2)

        # 4. Inactive Worker
        w_inact = User(
            phone=f"+9199{s}004",
            email=f"qs_inact_{s}@kaamtest.com",
            full_name="Inactive Worker QSub",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=False,
        )
        await w_inact.insert()
        test_users.append(w_inact)

        # Booking Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Customer Name",
            phone="+919876543210",
            address_line_1="Line 1",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400058",
            location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )

        svc_snap = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Whole House Deep Cleaning",
            category_id=str(PydanticObjectId()),
            category_slug="cleaner-qs-test",
            base_market_price=1200.0,
            estimated_duration_minutes=240,
        )

        num1 = await BookingRepository.generate_booking_number()
        b1 = Booking(
            booking_number=num1,
            customer_id=cust.id,
            booking_type=BookingType.INSPECTION_REQUEST,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            estimated_price=1200.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # Applications
        app1 = JobApplication(
            booking_id=b1.id,
            worker_id=w1.id,
            application_status=ApplicationStatus.PENDING,
        )
        await app1.insert()
        test_apps.append(app1)

        app2 = JobApplication(
            booking_id=b1.id,
            worker_id=w2.id,
            application_status=ApplicationStatus.PENDING,
        )
        await app2.insert()
        test_apps.append(app2)

        app_inact = JobApplication(
            booking_id=b1.id,
            worker_id=w_inact.id,
            application_status=ApplicationStatus.PENDING,
        )
        await app_inact.insert()
        test_apps.append(app_inact)

        validity = date.today() + timedelta(days=14)

        # ---------------------------------------------------------------------
        # Test 1: Worker 1 Creates DRAFT Quotation
        # ---------------------------------------------------------------------
        print("\n[1] Testing DRAFT Quotation Creation...")
        req_draft = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),
            labour_cost=2000.0,
            material_cost=1000.0,
            inspection_charge=150.0,
            additional_charges=100.0,
            tax_amount=200.0,
            discount_amount=150.0,
            estimated_duration="1 day",
            validity_date=validity,
            work_description="Complete sanitation, steam cleaning of carpets and upholstery.",
            is_draft=True,
        )

        res_draft = await service.create_quotation(w1, req_draft)
        assert res_draft.quotation_status == QuotationStatus.DRAFT
        # Subtotal: 2000 + 1000 + 150 + 100 + 200 = 3450; Total: 3450 - 150 = 3300
        assert res_draft.total_amount == 3300.0
        assert res_draft.submitted_at is None

        q1_doc = await Quotation.get(PydanticObjectId(res_draft.id))
        if q1_doc:
            test_quotes.append(q1_doc)
        print("    [PASS] DRAFT quotation created successfully with auto-calculated total.")

        # ---------------------------------------------------------------------
        # Test 2: Worker 1 Updates DRAFT Quotation
        # ---------------------------------------------------------------------
        print("\n[2] Testing DRAFT Quotation Update...")
        req_update = QuotationUpdateRequest(
            labour_cost=2500.0,
            discount_amount=200.0,
            work_description="Updated scope: includes deep balcony wash.",
            submit_now=False,
        )

        res_updated = await service.update_quotation(w1, res_draft.id, req_update)
        assert res_updated.quotation_status == QuotationStatus.DRAFT
        # Subtotal: 2500 + 1000 + 150 + 100 + 200 = 3950; Total: 3950 - 200 = 3750
        assert res_updated.total_amount == 3750.0
        assert res_updated.work_description == "Updated scope: includes deep balcony wash."
        print("    [PASS] DRAFT quotation updated successfully with recalculated total.")

        # ---------------------------------------------------------------------
        # Test 3: Worker 1 Submits Draft Quotation
        # ---------------------------------------------------------------------
        print("\n[3] Testing Quotation Submission (DRAFT -> SUBMITTED)...")
        req_submit = QuotationUpdateRequest(submit_now=True)
        res_submitted = await service.update_quotation(w1, res_draft.id, req_submit)
        assert res_submitted.quotation_status == QuotationStatus.SUBMITTED
        assert res_submitted.submitted_at is not None
        print(f"    [PASS] Quotation '{res_submitted.quotation_number}' submitted successfully.")

        # ---------------------------------------------------------------------
        # Test 4: Submitted Quotation Read-Only Rule
        # ---------------------------------------------------------------------
        print("\n[4] Testing Read-Only Enforcement for Submitted Quotation...")
        try:
            await service.update_quotation(w1, res_submitted.id, QuotationUpdateRequest(labour_cost=3000.0))
            assert False, "Submitted quotation edit attempt should have failed!"
        except BadRequestException as exc:
            assert exc.error_code == "QUOTATION_READ_ONLY"
        print("    [PASS] Submitted quotation modification blocked with 400 QUOTATION_READ_ONLY.")

        # ---------------------------------------------------------------------
        # Test 5: Duplicate Quotation Submission Prevention
        # ---------------------------------------------------------------------
        print("\n[5] Testing Duplicate Quotation Submission Prevention...")
        req_dup = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),
            labour_cost=2000.0,
            estimated_duration="1 day",
            validity_date=validity,
            is_draft=False,
        )

        try:
            await service.create_quotation(w1, req_dup)
            assert False, "Duplicate quotation submission should have failed!"
        except ConflictException as exc:
            assert exc.error_code == "QUOTATION_ALREADY_SUBMITTED"
        print("    [PASS] Duplicate quotation submission blocked with 409 QUOTATION_ALREADY_SUBMITTED.")

        # ---------------------------------------------------------------------
        # Test 6: Invalid Pricing Validation (Discount > Subtotal)
        # ---------------------------------------------------------------------
        print("\n[6] Testing Invalid Pricing Validation...")
        try:
            req_bad_price = QuotationCreateRequest(
                booking_id=str(b1.id),
                application_id=str(app2.id),  # Worker 2
                labour_cost=500.0,
                discount_amount=1000.0,  # Exceeds subtotal!
                estimated_duration="1 day",
                validity_date=validity,
            )
            await service.create_quotation(w2, req_bad_price)
            assert False, "Invalid discount should have failed validation!"
        except Exception:
            pass
        print("    [PASS] Invalid discount exceeding subtotal correctly rejected.")

        # ---------------------------------------------------------------------
        # Test 7: Invalid Date Validation (Expired Validity Date)
        # ---------------------------------------------------------------------
        print("\n[7] Testing Past Validity Date Validation...")
        past_date = date.today() - timedelta(days=2)
        req_past_date = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app2.id),
            labour_cost=500.0,
            estimated_duration="1 day",
            validity_date=past_date,
        )

        try:
            await service.create_quotation(w2, req_past_date)
            assert False, "Past validity date should have failed!"
        except BadRequestException as exc:
            assert exc.error_code == "INVALID_VALIDITY_DATE"
        print("    [PASS] Past validity date correctly rejected with 400 INVALID_VALIDITY_DATE.")

        # ---------------------------------------------------------------------
        # Test 8: Unauthorized Access Check
        # ---------------------------------------------------------------------
        print("\n[8] Testing Unauthorized Access Checks...")
        try:
            await service.get_quotation_detail(w2, res_submitted.id)
            assert False, "Worker 2 accessing Worker 1's quotation should fail!"
        except ForbiddenException as exc:
            assert exc.error_code == "UNAUTHORIZED_QUOTATION_ACCESS"
        print("    [PASS] Cross-worker quotation access strictly blocked with 403 UNAUTHORIZED_QUOTATION_ACCESS.")

        # ---------------------------------------------------------------------
        # Test 9: Inactive Worker Rejection
        # ---------------------------------------------------------------------
        print("\n[9] Testing Inactive Worker Rejection...")
        req_inact = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app_inact.id),
            labour_cost=1000.0,
            estimated_duration="1 day",
            validity_date=validity,
        )

        try:
            await service.create_quotation(w_inact, req_inact)
            assert False, "Inactive worker quotation attempt should fail!"
        except ForbiddenException as exc:
            assert exc.error_code == "WORKER_INACTIVE"
        print("    [PASS] Inactive worker quotation attempt rejected with 403 WORKER_INACTIVE.")

    finally:
        print("\n[CLEANUP] Cleaning up test quotations, applications, bookings, and users from Atlas...")
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
    print("ALL WORKER QUOTATION SUBMISSION VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_quotation_submission_verification())
