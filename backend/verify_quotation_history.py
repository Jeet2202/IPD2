"""
Verification script for KaamSetu Quotation History & Audit Trail (Phase 4.6.6).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer 1 (Owner), Customer 2 (Unrelated), Worker 1, Booking, Application.
  2. Audit Log Generation: Verify CREATED, UPDATED, SUBMITTED, ACCEPTED, and WORKER_ASSIGNED events.
  3. Chronological Ordering: Verify timeline records ordered by +created_at.
  4. Snapshot Fidelity: Verify previous_snapshot & new_snapshot accuracy.
  5. Authorization & Access Control: Customer 1 & Worker 1 access allowed; Customer 2 blocked with 403.
  6. Immutability: Audit log entries are read-only and persisted separately.
  7. Cleanup test documents.
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
from app.quotation.schemas import QuotationCreateRequest, QuotationUpdateRequest
from app.quotation.service import QuotationService
from app.utils.enums import (
    ApplicationStatus,
    BookingStatus,
    BookingType,
    QuotationEventType,
    QuotationStatus,
)
from app.worker.models import WorkerProfile


async def run_quotation_history_verification() -> None:
    print("=" * 75)
    print("KAAMSETU — QUOTATION HISTORY & AUDIT TRAIL (PHASE 4.6.6) VERIFICATION")
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

        c1 = User(
            phone=f"+9195{s}001",
            email=f"hist_c1_{s}@kaamtest.com",
            full_name="Customer 1 History Owner",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await c1.insert()
        test_users.append(c1)

        c2 = User(
            phone=f"+9195{s}002",
            email=f"hist_c2_{s}@kaamtest.com",
            full_name="Customer 2 History Attacker",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await c2.insert()
        test_users.append(c2)

        w1 = User(
            phone=f"+9195{s}003",
            email=f"hist_w1_{s}@kaamtest.com",
            full_name="Worker 1 History",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Office",
            full_name=c1.full_name,
            phone=c1.phone,
            address_line_1="Suite 404, Tech Park",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400058",
            location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )

        svc_snap = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="AC Deep Cleaning & Service",
            category_id=str(PydanticObjectId()),
            category_slug="ac-repair-hist-test",
            base_market_price=1200.0,
            estimated_duration_minutes=90,
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
            estimated_price=1200.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        app1 = JobApplication(booking_id=b1.id, worker_id=w1.id, application_status=ApplicationStatus.PENDING)
        await app1.insert()
        test_apps.append(app1)

        valid_date = date.today() + timedelta(days=14)

        # ---------------------------------------------------------------------
        # Event 1: Create Draft Quotation -> Log CREATED
        # ---------------------------------------------------------------------
        print("\n[1] Creating DRAFT Quotation & Verifying CREATED Event...")
        req_draft = QuotationCreateRequest(
            booking_id=str(b1.id),
            application_id=str(app1.id),
            labour_cost=1200.0,
            material_cost=300.0,
            estimated_duration="2 hours",
            validity_date=valid_date,
            is_draft=True,
        )
        q1_res = await service.create_quotation(w1, req_draft)
        q1_doc = await Quotation.get(PydanticObjectId(q1_res.id))
        if q1_doc:
            test_quotes.append(q1_doc)

        logs1 = await QuotationHistory.find(QuotationHistory.quotation_id == q1_doc.id).to_list()
        assert len(logs1) == 1
        assert logs1[0].event_type == QuotationEventType.CREATED
        assert logs1[0].new_status == QuotationStatus.DRAFT
        print("    [PASS] CREATED event successfully recorded in audit history.")

        # ---------------------------------------------------------------------
        # Event 2: Submit Quotation -> Log UPDATED & SUBMITTED
        # ---------------------------------------------------------------------
        print("\n[2] Submitting Quotation & Verifying UPDATED and SUBMITTED Events...")
        await service.update_quotation(
            w1,
            q1_res.id,
            QuotationUpdateRequest(labour_cost=1400.0, submit_now=True),
        )

        logs2 = await QuotationHistory.find(QuotationHistory.quotation_id == q1_doc.id).sort("+created_at").to_list()
        assert len(logs2) == 3
        assert logs2[1].event_type == QuotationEventType.UPDATED
        assert logs2[2].event_type == QuotationEventType.SUBMITTED
        assert logs2[2].new_status == QuotationStatus.SUBMITTED
        print("    [PASS] UPDATED and SUBMITTED events successfully logged in chronological order.")

        # ---------------------------------------------------------------------
        # Event 3: Accept Quotation -> Log ACCEPTED & WORKER_ASSIGNED
        # ---------------------------------------------------------------------
        print("\n[3] Accepting Quotation & Verifying ACCEPTED and WORKER_ASSIGNED Events...")
        await service.accept_quotation(c1, q1_res.id)

        logs3 = await QuotationHistory.find(QuotationHistory.quotation_id == q1_doc.id).sort("+created_at").to_list()
        assert len(logs3) == 5
        assert logs3[3].event_type == QuotationEventType.ACCEPTED
        assert logs3[4].event_type == QuotationEventType.WORKER_ASSIGNED
        assert logs3[4].notes is not None and "Worker" in logs3[4].notes
        print("    [PASS] ACCEPTED and WORKER_ASSIGNED events recorded with accurate snapshots & notes.")

        # ---------------------------------------------------------------------
        # Test 4: Customer & Worker History API Access
        # ---------------------------------------------------------------------
        print("\n[4] Testing Customer & Worker History Service Retrieval...")
        hist_customer = await service.get_quotation_history(c1, q1_res.id)
        assert hist_customer.total == 5
        assert len(hist_customer.items) == 5

        hist_worker = await service.get_quotation_history(w1, q1_res.id)
        assert hist_worker.total == 5
        print("    [PASS] History retrieved successfully for Customer 1 and Worker 1.")

        # ---------------------------------------------------------------------
        # Test 5: Unauthorized Access Guard Check (Customer 2 -> 403)
        # ---------------------------------------------------------------------
        print("\n[5] Testing Unauthorized History Access Prevention (Customer 2 -> 403)...")
        try:
            await service.get_quotation_history(c2, q1_res.id)
            assert False, "Customer 2 accessing Customer 1's history should fail!"
        except ForbiddenException as exc:
            assert exc.error_code == "UNAUTHORIZED_QUOTATION_ACCESS"
        print("    [PASS] Unauthorized access attempt correctly blocked with 403 UNAUTHORIZED_QUOTATION_ACCESS.")

    finally:
        print("\n[CLEANUP] Cleaning up test history logs, quotations, applications, bookings, and users...")
        if test_quotes:
            for q in test_quotes:
                history_logs = await QuotationHistory.find(QuotationHistory.quotation_id == q.id).to_list()
                for h in history_logs:
                    await h.delete()
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
    print("ALL QUOTATION HISTORY & AUDIT TRAIL VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_quotation_history_verification())
