"""
Verification script for Ally Complete Marketplace Business Rules (Phase 4.5.6).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer, Worker (incomplete profile), Open Booking.
  2. Test 1: Booking Visibility Rules (Disabled customer / cancelled status -> Hidden from marketplace).
  3. Test 2: Worker Profile Completion Rule (profile_completed=False -> 403 PROFILE_INCOMPLETE).
  4. Test 3: Worker Availability Rule (OFFLINE / BUSY -> 400 WORKER_NOT_AVAILABLE).
  5. Test 4: Duplicate Application Rule (409 DUPLICATE_APPLICATION).
  6. Test 5: Marketplace Detail View Consistency (Cancelled booking -> 404 MARKETPLACE_BOOKING_NOT_FOUND).
  7. Cleanup test documents.
"""

import asyncio
import random
import sys

sys.path.insert(0, ".")

from beanie import PydanticObjectId

from app.address.models import Address, GeoJSONPoint
from app.application.models import JobApplication
from app.application.schemas import JobApplicationCreateRequest
from app.application.service import JobApplicationService
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
from app.marketplace.rules import MarketplaceRulesEngine
from app.marketplace.service import MarketplaceService
from app.otp.models import OTP
from app.utils.enums import ApplicationStatus, BookingStatus, BookingType, WorkerAvailability
from app.worker.models import WorkerProfile


async def run_marketplace_business_rules_verification() -> None:
    print("=" * 75)
    print("ALLY — MARKETPLACE BUSINESS RULES (PHASE 4.5.6) VERIFICATION")
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
            Address,
            Booking,
            JobApplication,
        ]
    )
    print("    [PASS] Connected to Atlas database successfully.")

    mp_service = MarketplaceService()
    app_service = JobApplicationService()
    test_bookings: list[Booking] = []
    test_users: list[User] = []
    test_apps: list[JobApplication] = []
    test_profiles: list[WorkerProfile] = []

    try:
        s = str(random.randint(100000, 999999))

        # 1. Customer User
        cust = User(
            phone=f"+9198{s}001",
            email=f"rule_cust_{s}@kaamtest.com",
            full_name="Rule Customer",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        test_users.append(cust)

        # 2. Worker User with INCOMPLETE profile
        w1 = User(
            phone=f"+9198{s}002",
            email=f"rule_w1_{s}@kaamtest.com",
            full_name="Rule Worker",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        wp1 = WorkerProfile(
            user_id=w1.id,
            profile_completed=False,  # INCOMPLETE PROFILE!
            availability=WorkerAvailability.AVAILABLE,
            working_radius_km=15.0,
            current_location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )
        await wp1.insert()
        test_profiles.append(wp1)

        # Address & Service Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Rule Test",
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
            name="AC Filter Cleaning & Deep Service",
            category_id=str(PydanticObjectId()),
            category_slug="ac-repair-rule-test",
            base_market_price=599.0,
            estimated_duration_minutes=60,
        )

        # Seed open pending booking
        num1 = await BookingRepository.generate_booking_number()
        b1 = Booking(
            booking_number=num1,
            customer_id=cust.id,
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            scheduled_date="2026-09-20",
            estimated_price=599.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # ---------------------------------------------------------------------
        # Test 1: Booking Visibility Rules (Disabled Customer Account)
        # ---------------------------------------------------------------------
        print("\n[1] Testing Booking Visibility Rules...")
        assert MarketplaceRulesEngine.is_booking_visible(b1, customer_user=cust) is True

        cust.is_active = False  # Deactivate customer!
        await cust.save()

        assert MarketplaceRulesEngine.is_booking_visible(b1, customer_user=cust) is False, \
            "STRICT FAILURE: Booking remained visible when customer account was deactivated!"
        print("    [PASS] Booking automatically hidden when customer account is disabled.")

        # Reactivate customer
        cust.is_active = True
        await cust.save()

        # ---------------------------------------------------------------------
        # Test 2: Worker Profile Completion Rule (profile_completed = False)
        # ---------------------------------------------------------------------
        print("\n[2] Testing Worker Profile Completion Rule...")
        req1 = JobApplicationCreateRequest(booking_id=str(b1.id))
        try:
            await app_service.apply_for_job(w1, req1)
            assert False, "Incomplete profile application should have been rejected with ForbiddenException!"
        except ForbiddenException as exc:
            assert exc.status_code == 403
            assert exc.error_code == "PROFILE_INCOMPLETE"
        print("    [PASS] Incomplete profile application correctly rejected with 403 PROFILE_INCOMPLETE.")

        # Complete profile
        wp1.profile_completed = True
        await wp1.save()

        # ---------------------------------------------------------------------
        # Test 3: Worker Availability Rule (OFFLINE / BUSY)
        # ---------------------------------------------------------------------
        print("\n[3] Testing Worker Availability Rule...")
        wp1.availability = WorkerAvailability.OFFLINE
        await wp1.save()

        try:
            await app_service.apply_for_job(w1, req1)
            assert False, "Offline worker application should have been rejected with BadRequestException!"
        except BadRequestException as exc:
            assert exc.status_code == 400
            assert exc.error_code == "WORKER_NOT_AVAILABLE"
        print("    [PASS] Offline worker application correctly rejected with 400 WORKER_NOT_AVAILABLE.")

        # Set worker back to AVAILABLE
        wp1.availability = WorkerAvailability.AVAILABLE
        await wp1.save()

        # ---------------------------------------------------------------------
        # Test 4: Successful Application & Duplicate Rejection
        # ---------------------------------------------------------------------
        print("\n[4] Testing Successful Application & Duplicate Prevention...")
        res1 = await app_service.apply_for_job(w1, req1)
        assert res1.application_status == ApplicationStatus.PENDING

        app_doc = await JobApplication.get(res1.id)
        if app_doc:
            test_apps.append(app_doc)

        try:
            await app_service.apply_for_job(w1, req1)
            assert False, "Duplicate application should have been rejected!"
        except ConflictException as exc:
            assert exc.status_code == 409
            assert exc.error_code == "DUPLICATE_APPLICATION"
        print("    [PASS] Application created and duplicate attempt rejected with 409 DUPLICATE_APPLICATION.")

        # ---------------------------------------------------------------------
        # Test 5: Marketplace Consistency (Cancelled Booking Removal)
        # ---------------------------------------------------------------------
        print("\n[5] Testing Marketplace Consistency on Cancelled Booking...")
        b1.status = BookingStatus.CANCELLED
        await b1.save()

        try:
            await mp_service.get_marketplace_booking_detail(str(b1.id))
            assert False, "Detail view for cancelled booking should have returned 404!"
        except NotFoundException as exc:
            assert exc.status_code == 404
            assert exc.error_code == "MARKETPLACE_BOOKING_NOT_FOUND"
        print("    [PASS] Cancelled booking automatically removed from marketplace detail view.")

    finally:
        print("\n[CLEANUP] Cleaning up test documents from Atlas...")
        for a in test_apps:
            await a.delete()
        for b in test_bookings:
            await b.delete()
        for p in test_profiles:
            await p.delete()
        for u in test_users:
            await u.delete()
        await close_database_connection()
        print("    [PASS] Test data cleaned up successfully.")

    print("\n" + "=" * 75)
    print("ALL MARKETPLACE BUSINESS RULES VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_marketplace_business_rules_verification())
