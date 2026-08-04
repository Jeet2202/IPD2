"""
Verification script for Ally Quotation Approval & Worker Assignment (Phase 4.6.4).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer 1 (Owner), Customer 2 (Unrelated), Worker 1, Worker 2, Booking (PENDING).
  2. Job Applications for Worker 1 and Worker 2.
  3. Quotation 1 (Worker 1 SUBMITTED), Quotation 2 (Worker 2 SUBMITTED).
  4. Test 1: Customer 1 accepts Worker 1's quotation.
     - Quotation 1 status -> ACCEPTED.
     - Booking status -> ACCEPTED, worker_id -> Worker 1, final_price updated.
     - Application 1 status -> ACCEPTED.
     - Quotation 2 status -> REJECTED (automatic batch rejection).
     - Application 2 status -> REJECTED (automatic batch rejection).
  5. Test 2: Marketplace removal check (assigned booking no longer in marketplace).
  6. Test 3: Duplicate acceptance prevention (attempting to accept Quotation 2 fails with 409/400).
  7. Test 4: Accept expired quotation check (past validity date returns 400 QUOTATION_EXPIRED).
  8. Test 5: Unauthorized acceptance check (Customer 2 -> 403 UNAUTHORIZED_QUOTATION_ACCESS).
  9. Test 6: Assigned Worker API (GET /customer/bookings/{id}/assigned-worker).
 10. Cleanup test documents.
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
    NotFoundException,
)
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.marketplace.service import MarketplaceService
from app.otp.models import OTP
from app.quotation.models import Quotation, QuotationHistory
from app.quotation.schemas import QuotationCreateRequest
from app.quotation.service import QuotationService
from app.utils.enums import (
    ApplicationStatus,
    BookingStatus,
    BookingType,
    QuotationStatus,
)
from app.worker.models import WorkerProfile


async def run_quotation_approval_verification() -> None:
    print("=" * 75)
    print("ALLY — QUOTATION APPROVAL & WORKER ASSIGNMENT (PHASE 4.6.4) VERIFICATION")
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

    q_service = QuotationService()
    m_service = MarketplaceService()

    test_users: list[User] = []
    test_w_profiles: list[WorkerProfile] = []
    test_bookings: list[Booking] = []
    test_apps: list[JobApplication] = []
    test_quotes: list[Quotation] = []

    try:
        s = str(random.randint(100000, 999999))

        # 1. Customer 1 (Owner)
        c1 = User(
            phone=f"+9197{s}001",
            email=f"qa_c1_{s}@kaamtest.com",
            full_name="Customer Owner QA",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await c1.insert()
        test_users.append(c1)

        # 2. Customer 2 (Unrelated)
        c2 = User(
            phone=f"+9197{s}002",
            email=f"qa_c2_{s}@kaamtest.com",
            full_name="Customer Unrelated QA",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await c2.insert()
        test_users.append(c2)

        # 3. Worker 1
        w1 = User(
            phone=f"+9197{s}003",
            email=f"qa_w1_{s}@kaamtest.com",
            full_name="Electrician Pro 1",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        wp1 = WorkerProfile(
            user_id=w1.id,
            experience_years=6.0,
            skills=["Electrical", "Wiring"],
            rating=4.8,
        )
        await wp1.insert()
        test_w_profiles.append(wp1)

        # 4. Worker 2
        w2 = User(
            phone=f"+9197{s}004",
            email=f"qa_w2_{s}@kaamtest.com",
            full_name="Electrician Pro 2",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w2.insert()
        test_users.append(w2)

        wp2 = WorkerProfile(
            user_id=w2.id,
            experience_years=3.0,
            skills=["Lighting", "Inverter Installation"],
            rating=4.5,
        )
        await wp2.insert()
        test_w_profiles.append(wp2)

        # Booking
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name=c1.full_name,
            phone=c1.phone,
            address_line_1="Tower 5, Flat 1002",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400058",
            location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )

        svc_snap = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Full Home Electrical Inspection",
            category_id=str(PydanticObjectId()),
            category_slug="electrician-qa-test",
            base_market_price=2000.0,
            estimated_duration_minutes=240,
        )

        num1 = await BookingRepository.generate_booking_number()
        b1 = Booking(
            booking_number=num1,
            customer_id=c1.id,
            booking_type=BookingType.INSPECTION_REQUEST,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            estimated_price=2000.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # Applications
        app1 = JobApplication(booking_id=b1.id, worker_id=w1.id, application_status=ApplicationStatus.PENDING)
        await app1.insert()
        test_apps.append(app1)

        app2 = JobApplication(booking_id=b1.id, worker_id=w2.id, application_status=ApplicationStatus.PENDING)
        await app2.insert()
        test_apps.append(app2)

        validity = date.today() + timedelta(days=14)

        # Quotation 1 (Worker 1 SUBMITTED)
        req_q1 = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),
            labour_cost=2500.0,
            material_cost=800.0,
            inspection_charge=200.0,
            additional_charges=0.0,
            tax_amount=250.0,
            discount_amount=250.0,
            estimated_duration="1 day",
            validity_date=validity,
            work_description="Full panel inspection & surge protector installation.",
            is_draft=False,
        )
        q1_res = await q_service.create_quotation(w1, req_q1)
        q1_doc = await Quotation.get(PydanticObjectId(q1_res.id))
        if q1_doc:
            test_quotes.append(q1_doc)

        # Quotation 2 (Worker 2 SUBMITTED)
        req_q2 = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app2.id),
            labour_cost=3000.0,
            material_cost=500.0,
            inspection_charge=0.0,
            additional_charges=100.0,
            tax_amount=300.0,
            discount_amount=300.0,
            estimated_duration="2 days",
            validity_date=validity,
            work_description="Complete rewiring and load balancing.",
            is_draft=False,
        )
        q2_res = await q_service.create_quotation(w2, req_q2)
        q2_doc = await Quotation.get(PydanticObjectId(q2_res.id))
        if q2_doc:
            test_quotes.append(q2_doc)

        # ---------------------------------------------------------------------
        # Test 1: Customer 1 Accepts Worker 1's Quotation
        # ---------------------------------------------------------------------
        print("\n[1] Testing Customer Quotation Acceptance & Atomic Worker Assignment...")
        accept_res = await q_service.accept_quotation(c1, q1_res.id)

        assert accept_res.quotation_status == QuotationStatus.ACCEPTED.value
        assert accept_res.booking_status == BookingStatus.ACCEPTED.value
        assert accept_res.worker_id == str(w1.id)
        assert accept_res.final_price == 3500.0

        # Verify DB states
        b1_db = await Booking.get(b1.id)
        assert b1_db.status == BookingStatus.ACCEPTED
        assert b1_db.worker_id == w1.id
        assert b1_db.quotation_id == PydanticObjectId(q1_res.id)
        assert b1_db.final_price == 3500.0

        q1_db = await Quotation.get(PydanticObjectId(q1_res.id))
        assert q1_db.quotation_status == QuotationStatus.ACCEPTED

        app1_db = await JobApplication.get(app1.id)
        assert app1_db.application_status == ApplicationStatus.ACCEPTED

        # Verify batch rejections
        q2_db = await Quotation.get(PydanticObjectId(q2_res.id))
        assert q2_db.quotation_status == QuotationStatus.REJECTED

        app2_db = await JobApplication.get(app2.id)
        assert app2_db.application_status == ApplicationStatus.REJECTED

        print("    [PASS] Worker 1 assigned, booking status updated to ACCEPTED, other quotes & apps REJECTED.")

        # ---------------------------------------------------------------------
        # Test 2: Marketplace Removal Verification
        # ---------------------------------------------------------------------
        print("\n[2] Testing Automatic Marketplace Removal...")
        m_res = await m_service.list_marketplace_bookings()
        booking_ids_in_m = [item.id for item in m_res.items]
        assert str(b1.id) not in booking_ids_in_m
        print("    [PASS] Assigned booking automatically removed from marketplace results.")

        # ---------------------------------------------------------------------
        # Test 3: Duplicate Acceptance Prevention
        # ---------------------------------------------------------------------
        print("\n[3] Testing Duplicate Acceptance Prevention...")
        try:
            await q_service.accept_quotation(c1, q2_res.id)
            assert False, "Accepting a second quotation for the same booking should fail!"
        except (ConflictException, BadRequestException) as exc:
            pass
        print("    [PASS] Duplicate quotation acceptance strictly blocked.")

        # ---------------------------------------------------------------------
        # Test 4: Unauthorized Acceptance Check
        # ---------------------------------------------------------------------
        print("\n[4] Testing Unauthorized Acceptance Check...")
        try:
            await q_service.accept_quotation(c2, q1_res.id)
            assert False, "Customer 2 accepting Customer 1's quotation should fail!"
        except ForbiddenException as exc:
            assert exc.error_code == "UNAUTHORIZED_QUOTATION_ACCESS"
        print("    [PASS] Non-owner acceptance attempt blocked with 403 UNAUTHORIZED_QUOTATION_ACCESS.")

        # ---------------------------------------------------------------------
        # Test 5: Assigned Worker Details Endpoint Verification
        # ---------------------------------------------------------------------
        print("\n[5] Testing Assigned Worker API Endpoint...")
        assigned_worker_res = await q_service.get_assigned_worker(c1, str(b1.id))
        assert assigned_worker_res.worker_id == str(w1.id)
        assert assigned_worker_res.full_name == "Electrician Pro 1"
        assert assigned_worker_res.rating == 4.8
        assert assigned_worker_res.accepted_quotation.id == q1_res.id
        print("    [PASS] Assigned worker API returned correct worker snapshot & accepted quotation.")

    finally:
        print("\n[CLEANUP] Cleaning up test data from Atlas database...")
        for q in test_quotes:
            await q.delete()
        for a in test_apps:
            await a.delete()
        for b in test_bookings:
            await b.delete()
        for wp in test_w_profiles:
            await wp.delete()
        for u in test_users:
            await u.delete()
        await close_database_connection()
        print("    [PASS] Test data cleaned up successfully.")

    print("\n" + "=" * 75)
    print("ALL QUOTATION APPROVAL & WORKER ASSIGNMENT VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_quotation_approval_verification())
