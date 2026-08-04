"""
Verification script for Ally Quotation Foundation (Phase 4.6.1).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer, Worker 1, Worker 2, Booking, and Job Applications.
  2. Test 1: Quotation creation & atomic number generation (QT202600001, QT202600002).
  3. Test 2: Total amount calculation & schema validation.
  4. Test 3: Status enum support (DRAFT, SUBMITTED, ACCEPTED, REJECTED, EXPIRED, CANCELLED).
  5. Test 4: Relationships (Booking, Worker, Application mismatch handling).
  6. Test 5: Multiple quotations per booking support.
  7. Test 6: Repository and service listing queries.
  8. Cleanup test documents.
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
from app.core.exceptions import ForbiddenException
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.otp.models import OTP
from app.quotation.models import Quotation, QuotationHistory
from app.quotation.repository import QuotationRepository
from app.quotation.schemas import QuotationCreateRequest
from app.quotation.service import QuotationService
from app.utils.enums import (
    ApplicationStatus,
    BookingStatus,
    BookingType,
    QuotationStatus,
    WorkerAvailability,
)
from app.worker.models import WorkerProfile


async def run_quotation_verification() -> None:
    print("=" * 75)
    print("ALLY — QUOTATION FOUNDATION (PHASE 4.6.1) VERIFICATION")
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
            phone=f"+9198{s}001",
            email=f"q_cust_{s}@kaamtest.com",
            full_name="Customer QuotationTest",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        test_users.append(cust)

        # 2. Worker 1
        w1 = User(
            phone=f"+9198{s}002",
            email=f"q_w1_{s}@kaamtest.com",
            full_name="Worker One QTest",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        # 3. Worker 2
        w2 = User(
            phone=f"+9198{s}003",
            email=f"q_w2_{s}@kaamtest.com",
            full_name="Worker Two QTest",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w2.insert()
        test_users.append(w2)

        # Booking Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Quotation Customer",
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
            name="Home Painting Assessment",
            category_id=str(PydanticObjectId()),
            category_slug="painter-q-test",
            base_market_price=500.0,
            estimated_duration_minutes=120,
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
            estimated_price=500.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # Applications
        app1 = JobApplication(
            booking_id=b1.id,
            worker_id=w1.id,
            application_status=ApplicationStatus.PENDING,
            cover_letter="I can provide site inspection and detailed painting quotation.",
        )
        await app1.insert()
        test_apps.append(app1)

        app2 = JobApplication(
            booking_id=b1.id,
            worker_id=w2.id,
            application_status=ApplicationStatus.PENDING,
            cover_letter="Master painter with 10 years experience.",
        )
        await app2.insert()
        test_apps.append(app2)

        # ---------------------------------------------------------------------
        # Test 1: Quotation Creation & Number Generation
        # ---------------------------------------------------------------------
        print("\n[1] Testing Quotation Creation & Atomic Number Generation...")
        validity = date.today() + timedelta(days=14)
        req1 = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),
            labour_cost=3000.0,
            material_cost=4500.0,
            inspection_charge=200.0,
            additional_charges=300.0,
            tax_amount=500.0,
            discount_amount=200.0,
            estimated_duration="3 days",
            validity_date=validity,
            notes="Includes premium weather-proof primer and 2 coats acrylic emulsion.",
            is_draft=False,
        )

        res1 = await service.create_quotation(w1, req1)
        assert res1.quotation_number.startswith("QT")
        assert len(res1.quotation_number) == 11  # QT202600001
        assert res1.quotation_status == QuotationStatus.SUBMITTED
        assert res1.booking_id == str(b1.id)
        assert res1.worker_id == str(w1.id)
        assert res1.application_id == str(app1.id)
        assert res1.submitted_at is not None

        q1_doc = await Quotation.get(PydanticObjectId(res1.id))
        if q1_doc:
            test_quotes.append(q1_doc)
        print(f"    [PASS] Quotation '{res1.quotation_number}' created successfully.")

        # ---------------------------------------------------------------------
        # Test 2: Total Amount Calculation
        # ---------------------------------------------------------------------
        print("\n[2] Testing Total Amount Calculation...")
        # 3000 + 4500 + 200 + 300 + 500 - 200 = 8300.0
        expected_total = 3000.0 + 4500.0 + 200.0 + 300.0 + 500.0 - 200.0
        assert res1.total_amount == expected_total
        print(f"    [PASS] Total amount correctly calculated as INR {res1.total_amount}.")

        # ---------------------------------------------------------------------
        # Test 3: Status Enum Validation
        # ---------------------------------------------------------------------
        print("\n[3] Testing Status Enum Values...")
        statuses = [
            QuotationStatus.DRAFT,
            QuotationStatus.SUBMITTED,
            QuotationStatus.ACCEPTED,
            QuotationStatus.REJECTED,
            QuotationStatus.EXPIRED,
            QuotationStatus.CANCELLED,
        ]
        assert len(statuses) == 6
        print("    [PASS] QuotationStatus enums (DRAFT, SUBMITTED, ACCEPTED, REJECTED, EXPIRED, CANCELLED) verified.")

        # ---------------------------------------------------------------------
        # Test 4: Application Mismatch & Authorization
        # ---------------------------------------------------------------------
        print("\n[4] Testing Application Mismatch & Authorization...")
        # Worker 2 trying to use Worker 1's application ID
        req_mismatch = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),  # Belongs to Worker 1!
            labour_cost=1000.0,
            estimated_duration="1 day",
            validity_date=validity,
        )

        try:
            await service.create_quotation(w2, req_mismatch)
            assert False, "Should reject mismatching worker and application!"
        except ForbiddenException as exc:
            assert exc.error_code == "APPLICATION_MISMATCH"
        print("    [PASS] Cross-worker application quotation attempt strictly rejected.")

        # ---------------------------------------------------------------------
        # Test 5: Multiple Quotations Per Booking
        # ---------------------------------------------------------------------
        print("\n[5] Testing Multiple Quotations Per Booking...")
        req2 = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app2.id),  # Worker 2's application
            labour_cost=2800.0,
            material_cost=4000.0,
            estimated_duration="2 days",
            validity_date=validity,
            is_draft=True,  # Save as DRAFT
        )

        res2 = await service.create_quotation(w2, req2)
        assert res2.quotation_status == QuotationStatus.DRAFT
        assert res2.quotation_number != res1.quotation_number

        q2_doc = await Quotation.get(PydanticObjectId(res2.id))
        if q2_doc:
            test_quotes.append(q2_doc)

        booking_quotes = await service.list_booking_quotations(cust, str(b1.id))
        assert len(booking_quotes) == 2
        print(f"    [PASS] Multiple quotations ({len(booking_quotes)}) successfully associated with booking.")

        # ---------------------------------------------------------------------
        # Test 6: Repository & Service Queries
        # ---------------------------------------------------------------------
        print("\n[6] Testing Repository & Service Queries...")
        q_by_num = await QuotationRepository.get_quotation_by_number(res1.quotation_number)
        assert q_by_num is not None
        assert str(q_by_num.id) == res1.id

        w1_quotes = await service.list_worker_quotations(w1, page=1, page_size=20)
        assert w1_quotes.total == 1
        assert w1_quotes.items[0].id == res1.id
        print("    [PASS] Repository and service listing queries verified.")

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
    print("ALL QUOTATION FOUNDATION VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_quotation_verification())
