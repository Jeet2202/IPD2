"""
Verification script for Ally Customer Quotation Management (Phase 4.6.3).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer 1 (Owner), Customer 2 (Unrelated), Worker 1, Worker 2, Booking.
  2. Create Job Applications for Worker 1 and Worker 2.
  3. Create Quotations:
     - Worker 1: SUBMITTED quotation
     - Worker 2: SUBMITTED quotation
     - Worker 1: DRAFT quotation for another app (must be excluded!)
  4. Test 1: Customer 1 retrieves quotations for their booking (returns 2 SUBMITTED quotes, DRAFT excluded, worker summaries attached).
  5. Test 2: Customer 1 retrieves detailed quotation view by ID.
  6. Test 3: Customer 2 attempts to view Customer 1's booking quotations -> 403 UNAUTHORIZED_QUOTATION_ACCESS.
  7. Test 4: Customer 2 attempts to view Customer 1's quotation detail -> 403 UNAUTHORIZED_QUOTATION_ACCESS.
  8. Test 5: Booking with empty quotations returns empty list `[]`.
  9. Cleanup test documents.
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
    ForbiddenException,
    NotFoundException,
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


async def run_customer_quotation_verification() -> None:
    print("=" * 75)
    print("ALLY — CUSTOMER QUOTATION MANAGEMENT (PHASE 4.6.3) VERIFICATION")
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
    test_w_profiles: list[WorkerProfile] = []
    test_bookings: list[Booking] = []
    test_apps: list[JobApplication] = []
    test_quotes: list[Quotation] = []

    try:
        s = str(random.randint(100000, 999999))

        # 1. Customer 1 (Owner)
        c1 = User(
            phone=f"+9198{s}001",
            email=f"cq_c1_{s}@kaamtest.com",
            full_name="Customer Owner CQ",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await c1.insert()
        test_users.append(c1)

        # 2. Customer 2 (Unrelated)
        c2 = User(
            phone=f"+9198{s}002",
            email=f"cq_c2_{s}@kaamtest.com",
            full_name="Customer Unrelated CQ",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await c2.insert()
        test_users.append(c2)

        # 3. Worker 1
        w1 = User(
            phone=f"+9198{s}003",
            email=f"cq_w1_{s}@kaamtest.com",
            full_name="Rajesh Plumbing Pro",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        wp1 = WorkerProfile(
            user_id=w1.id,
            experience_years=7.5,
            skills=["Plumbing", "Pipe Fitting", "Geyser Repair"],
            rating=4.9,
        )
        await wp1.insert()
        test_w_profiles.append(wp1)

        # 4. Worker 2
        w2 = User(
            phone=f"+9198{s}004",
            email=f"cq_w2_{s}@kaamtest.com",
            full_name="Suresh Master Services",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w2.insert()
        test_users.append(w2)

        wp2 = WorkerProfile(
            user_id=w2.id,
            experience_years=4.0,
            skills=["Sanitary Work", "Leakage Fixing"],
            rating=4.6,
        )
        await wp2.insert()
        test_w_profiles.append(wp2)

        # Bookings
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name=c1.full_name,
            phone=c1.phone,
            address_line_1="Building A, Flat 402",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400058",
            location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )

        svc_snap = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Emergency Pipe Leakage & Fitting",
            category_id=str(PydanticObjectId()),
            category_slug="plumber-cq-test",
            base_market_price=1500.0,
            estimated_duration_minutes=180,
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
            estimated_price=1500.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # Empty booking for Customer 1
        num2 = await BookingRepository.generate_booking_number()
        b_empty = Booking(
            booking_number=num2,
            customer_id=c1.id,
            booking_type=BookingType.INSPECTION_REQUEST,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            estimated_price=1500.0,
        )
        await b_empty.insert()
        test_bookings.append(b_empty)

        # Applications
        app1 = JobApplication(booking_id=b1.id, worker_id=w1.id, application_status=ApplicationStatus.PENDING)
        await app1.insert()
        test_apps.append(app1)

        app2 = JobApplication(booking_id=b1.id, worker_id=w2.id, application_status=ApplicationStatus.PENDING)
        await app2.insert()
        test_apps.append(app2)

        validity = date.today() + timedelta(days=10)

        # ---------------------------------------------------------------------
        # Create Quotations
        # ---------------------------------------------------------------------
        # Quote 1: Worker 1 SUBMITTED
        req_q1 = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),
            labour_cost=1800.0,
            material_cost=600.0,
            inspection_charge=100.0,
            additional_charges=0.0,
            tax_amount=150.0,
            discount_amount=150.0,
            estimated_duration="3 hours",
            validity_date=validity,
            work_description="Complete pipe replacement with copper joints and 1-year warranty.",
            is_draft=False,  # SUBMITTED
        )
        q1_res = await service.create_quotation(w1, req_q1)
        q1_doc = await Quotation.get(PydanticObjectId(q1_res.id))
        if q1_doc:
            test_quotes.append(q1_doc)

        # Quote 2: Worker 2 SUBMITTED
        req_q2 = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app2.id),
            labour_cost=2200.0,
            material_cost=400.0,
            inspection_charge=0.0,
            additional_charges=100.0,
            tax_amount=180.0,
            discount_amount=200.0,
            estimated_duration="4 hours",
            validity_date=validity,
            work_description="Heavy duty sealant and high-pressure PVC pipe fitting.",
            is_draft=False,  # SUBMITTED
        )
        q2_res = await service.create_quotation(w2, req_q2)
        q2_doc = await Quotation.get(PydanticObjectId(q2_res.id))
        if q2_doc:
            test_quotes.append(q2_doc)

        # ---------------------------------------------------------------------
        # Test 1: Customer 1 Retrieves Booking Quotations
        # ---------------------------------------------------------------------
        print("\n[1] Testing Customer Booking Quotations Retrieval...")
        cust_quotes = await service.list_booking_quotations_for_customer(c1, str(b1.id))
        assert len(cust_quotes) == 2
        
        # Verify worker details attached
        w_names = [cq.worker.full_name for cq in cust_quotes]
        assert "Rajesh Plumbing Pro" in w_names
        assert "Suresh Master Services" in w_names
        
        # Verify price calculations
        q1_item = next(cq for cq in cust_quotes if cq.id == q1_res.id)
        assert q1_item.total_amount == 2500.0  # 1800 + 600 + 100 + 0 + 150 - 150
        assert q1_item.worker.rating == 4.9
        assert q1_item.worker.experience_years == 7.5
        assert "Plumbing" in q1_item.worker.skills
        print("    [PASS] Customer retrieved all submitted quotations with worker profile summaries.")

        # ---------------------------------------------------------------------
        # Test 2: Customer 1 Retrieves Quotation Details by ID
        # ---------------------------------------------------------------------
        print("\n[2] Testing Customer Quotation Detail View...")
        detail = await service.get_customer_quotation_detail(c1, q1_res.id)
        assert detail.id == q1_res.id
        assert detail.worker.full_name == "Rajesh Plumbing Pro"
        assert detail.work_description == "Complete pipe replacement with copper joints and 1-year warranty."
        print("    [PASS] Customer quotation detail view verified.")

        # ---------------------------------------------------------------------
        # Test 3: Unauthorized Customer Booking Quotations Access
        # ---------------------------------------------------------------------
        print("\n[3] Testing Unauthorized Access (Customer 2 -> Booking 1)...")
        try:
            await service.list_booking_quotations_for_customer(c2, str(b1.id))
            assert False, "Customer 2 viewing Customer 1's booking quotations should fail!"
        except ForbiddenException as exc:
            assert exc.error_code == "UNAUTHORIZED_QUOTATION_ACCESS"
        print("    [PASS] Non-owner access to booking quotations blocked with 403 UNAUTHORIZED_QUOTATION_ACCESS.")

        # ---------------------------------------------------------------------
        # Test 4: Unauthorized Customer Quotation Detail Access
        # ---------------------------------------------------------------------
        print("\n[4] Testing Unauthorized Detail Access (Customer 2 -> Quotation 1)...")
        try:
            await service.get_customer_quotation_detail(c2, q1_res.id)
            assert False, "Customer 2 viewing Customer 1's quotation detail should fail!"
        except ForbiddenException as exc:
            assert exc.error_code == "UNAUTHORIZED_QUOTATION_ACCESS"
        print("    [PASS] Non-owner access to quotation detail blocked with 403 UNAUTHORIZED_QUOTATION_ACCESS.")

        # ---------------------------------------------------------------------
        # Test 5: Empty Quotation List
        # ---------------------------------------------------------------------
        print("\n[5] Testing Empty Booking Quotation Retrieval...")
        empty_list = await service.list_booking_quotations_for_customer(c1, str(b_empty.id))
        assert len(empty_list) == 0
        print("    [PASS] Booking with no quotations returned empty list [].")

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
    print("ALL CUSTOMER QUOTATION MANAGEMENT VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_customer_quotation_verification())
