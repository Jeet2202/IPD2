"""
Verification script for Ally Worker Job Application System (Phase 4.5.4).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer, Worker 1, Worker 2 users, and open PENDING booking.
  2. Test 1: Worker 1 successfully applies for booking.
     - Booking status REMAINS PENDING (No assignment occurs!).
  3. Test 2: Duplicate application prevention (409 DUPLICATE_APPLICATION).
  4. Test 3: Closed/assigned booking application rejection (400 BOOKING_NOT_AVAILABLE).
  5. Test 4: Inactive worker application rejection (403 WORKER_INACTIVE).
  6. Test 5: Unauthorized application access (Worker 2 accessing Worker 1's app -> 403 UNAUTHORIZED_APPLICATION_ACCESS).
  7. Test 6: Worker application listing history.
  8. Cleanup test documents.
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
)
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.otp.models import OTP
from app.utils.enums import ApplicationStatus, BookingStatus, BookingType, WorkerAvailability
from app.worker.models import WorkerProfile


async def run_job_application_verification() -> None:
    print("=" * 75)
    print("ALLY — WORKER JOB APPLICATION SYSTEM (PHASE 4.5.4) VERIFICATION")
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

    service = JobApplicationService()
    test_bookings: list[Booking] = []
    test_users: list[User] = []
    test_apps: list[JobApplication] = []
    test_profiles: list[WorkerProfile] = []

    try:
        s = str(random.randint(100000, 999999))

        # 1. Customer User
        cust = User(
            phone=f"+9197{s}001",
            email=f"app_cust_{s}@kaamtest.com",
            full_name="Customer AppTest",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        test_users.append(cust)

        # 2. Worker 1 (Active)
        w1 = User(
            phone=f"+9197{s}002",
            email=f"app_w1_{s}@kaamtest.com",
            full_name="Worker One",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        wp1 = WorkerProfile(
            user_id=w1.id,
            profile_completed=True,
            availability=WorkerAvailability.AVAILABLE,
            working_radius_km=50.0,
            current_location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )
        await wp1.insert()
        test_profiles.append(wp1)

        # 3. Worker 2 (Active)
        w2 = User(
            phone=f"+9197{s}003",
            email=f"app_w2_{s}@kaamtest.com",
            full_name="Worker Two",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w2.insert()
        test_users.append(w2)

        wp2 = WorkerProfile(
            user_id=w2.id,
            profile_completed=True,
            availability=WorkerAvailability.AVAILABLE,
            working_radius_km=50.0,
            current_location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )
        await wp2.insert()
        test_profiles.append(wp2)

        # 4. Inactive Worker
        w_inactive = User(
            phone=f"+9197{s}004",
            email=f"app_inact_{s}@kaamtest.com",
            full_name="Inactive Worker",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=False,  # INACTIVE!
        )
        await w_inactive.insert()
        test_users.append(w_inactive)

        wp_inactive = WorkerProfile(
            user_id=w_inactive.id,
            profile_completed=True,
            availability=WorkerAvailability.AVAILABLE,
        )
        await wp_inactive.insert()
        test_profiles.append(wp_inactive)

        # Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Sanitized Name",
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
            name="Ceiling Fan Repair & Installation",
            category_id=str(PydanticObjectId()),
            category_slug="electrical-app-test",
            base_market_price=350.0,
            estimated_duration_minutes=45,
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
            scheduled_date="2026-09-15",
            estimated_price=350.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # ---------------------------------------------------------------------
        # Test 1: Worker 1 successfully applies for booking
        # ---------------------------------------------------------------------
        print("\n[1] Testing Worker 1 Job Application Submission...")
        req1 = JobApplicationCreateRequest(
            booking_id=str(b1.id),
            cover_letter="I have 5 years experience in electrical fan repair.",
        )
        res1 = await service.apply_for_job(w1, req1)
        assert res1.booking_id == str(b1.id)
        assert res1.worker_id == str(w1.id)
        assert res1.application_status == ApplicationStatus.PENDING
        assert res1.booking_number == num1

        # Track for cleanup
        app1_doc = await JobApplication.get(res1.id)
        if app1_doc:
            test_apps.append(app1_doc)

        # VERIFY CRITICAL BUSINESS RULE: BOOKING STATUS REMAINS PENDING AND UNASSIGNED!
        b1_refreshed = await Booking.get(b1.id)
        assert b1_refreshed is not None
        assert b1_refreshed.status == BookingStatus.PENDING, "STRICT FAILURE: Applying altered booking status!"
        assert b1_refreshed.worker_id is None, "STRICT FAILURE: Applying assigned worker to booking!"
        print("    [PASS] Worker application created successfully. Target booking remains open PENDING & unassigned.")

        # ---------------------------------------------------------------------
        # Test 2: Duplicate application prevention (409 Conflict)
        # ---------------------------------------------------------------------
        print("\n[2] Testing Duplicate Application Rejection...")
        try:
            await service.apply_for_job(w1, req1)
            assert False, "Duplicate application should have been rejected with ConflictException!"
        except ConflictException as exc:
            assert exc.status_code == 409
            assert exc.error_code == "DUPLICATE_APPLICATION"
        print("    [PASS] Duplicate application correctly rejected with 409 DUPLICATE_APPLICATION.")

        # ---------------------------------------------------------------------
        # Test 3: Closed or assigned booking application rejection
        # ---------------------------------------------------------------------
        print("\n[3] Testing Application Rejection on Closed/Assigned Booking...")
        num2 = await BookingRepository.generate_booking_number()
        b_closed = Booking(
            booking_number=num2,
            customer_id=cust.id,
            worker_id=w1.id,  # Assigned!
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.ACCEPTED,  # Closed!
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
        )
        await b_closed.insert()
        test_bookings.append(b_closed)

        req_closed = JobApplicationCreateRequest(booking_id=str(b_closed.id))
        try:
            await service.apply_for_job(w2, req_closed)
            assert False, "Application on closed booking should have been rejected!"
        except BadRequestException as exc:
            assert exc.status_code == 400
            assert exc.error_code == "BOOKING_NOT_AVAILABLE"
        print("    [PASS] Closed/assigned booking application rejected with 400 BOOKING_NOT_AVAILABLE.")

        # ---------------------------------------------------------------------
        # Test 4: Inactive worker application rejection
        # ---------------------------------------------------------------------
        print("\n[4] Testing Application Rejection for Inactive Worker...")
        try:
            await service.apply_for_job(w_inactive, req1)
            assert False, "Inactive worker application should have been rejected!"
        except ForbiddenException as exc:
            assert exc.status_code == 403
            assert exc.error_code == "WORKER_INACTIVE"
        print("    [PASS] Inactive worker application rejected with 403 WORKER_INACTIVE.")

        # ---------------------------------------------------------------------
        # Test 5: Unauthorized application detail access
        # ---------------------------------------------------------------------
        print("\n[5] Testing Unauthorized Application Detail Access...")
        # Worker 1 can view own application
        own_app = await service.get_worker_application_detail(w1, res1.id)
        assert own_app.id == res1.id

        # Worker 2 attempting to view Worker 1's application
        try:
            await service.get_worker_application_detail(w2, res1.id)
            assert False, "Cross-worker application view should be rejected!"
        except ForbiddenException as exc:
            assert exc.status_code == 403
            assert exc.error_code == "UNAUTHORIZED_APPLICATION_ACCESS"
        print("    [PASS] Cross-worker application access strictly blocked with 403 UNAUTHORIZED_APPLICATION_ACCESS.")

        # ---------------------------------------------------------------------
        # Test 6: Worker application listing history
        # ---------------------------------------------------------------------
        print("\n[6] Testing Worker Application Listing History...")
        w1_apps = await service.list_worker_applications(w1, page=1, page_size=20)
        assert w1_apps.total >= 1
        assert any(x.id == res1.id for x in w1_apps.items)

        w2_apps = await service.list_worker_applications(w2, page=1, page_size=20)
        assert not any(x.id == res1.id for x in w2_apps.items), "Worker 1's application appeared in Worker 2's list!"
        print("    [PASS] Worker application history correctly scoped to owning worker.")

        # ---------------------------------------------------------------------
        # Test 7: Worker Availability Validation (OFFLINE / BUSY)
        # ---------------------------------------------------------------------
        print("\n[7] Testing Worker Availability Validation (OFFLINE / BUSY)...")
        w3 = User(
            phone=f"+9197{s}005",
            email=f"app_w3_{s}@kaamtest.com",
            full_name="Worker Three Offline",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w3.insert()
        test_users.append(w3)

        wp_offline = WorkerProfile(
            user_id=w3.id,
            profile_completed=True,
            availability=WorkerAvailability.OFFLINE,
        )
        await wp_offline.insert()
        test_profiles.append(wp_offline)

        try:
            await service.apply_for_job(w3, JobApplicationCreateRequest(booking_id=str(b1.id)))
            assert False, "Offline worker application should have been rejected!"
        except BadRequestException as exc:
            assert exc.status_code == 400
            assert exc.error_code == "WORKER_NOT_AVAILABLE"
        print("    [PASS] Offline worker application rejected with 400 WORKER_NOT_AVAILABLE.")

        # ---------------------------------------------------------------------
        # Test 8: GeoJSON Service Radius Validation
        # ---------------------------------------------------------------------
        print("\n[8] Testing GeoJSON Service Radius Validation...")
        w4 = User(
            phone=f"+9197{s}006",
            email=f"app_w4_{s}@kaamtest.com",
            full_name="Worker Four Radius Test",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w4.insert()
        test_users.append(w4)

        # Worker located in Mumbai (19.1136, 72.8697) with small radius of 5 km
        wp_radius = WorkerProfile(
            user_id=w4.id,
            profile_completed=True,
            working_radius_km=5.0,
            current_location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
            availability=WorkerAvailability.AVAILABLE,
        )
        await wp_radius.insert()
        test_profiles.append(wp_radius)

        # Create booking 50 km away in Pune (18.5204, 73.8567)
        far_addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Far",
            full_name="Far Person",
            phone="+919000000000",
            address_line_1="Far Street",
            city="Pune",
            state="Maharashtra",
            country="India",
            postal_code="411001",
            location=GeoJSONPoint.from_lat_lng(18.5204, 73.8567),
        )
        num_far = await BookingRepository.generate_booking_number()
        b_far = Booking(
            booking_number=num_far,
            customer_id=cust.id,
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=far_addr_snap,
            service_location=far_addr_snap.location,
            estimated_price=350.0,
        )
        await b_far.insert()
        test_bookings.append(b_far)

        try:
            await service.apply_for_job(w4, JobApplicationCreateRequest(booking_id=str(b_far.id)))
            assert False, "Distant booking outside working radius should have been rejected!"
        except BadRequestException as exc:
            assert exc.status_code == 400
            assert exc.error_code == "OUTSIDE_SERVICE_RADIUS"
        print("    [PASS] Booking outside service radius rejected with 400 OUTSIDE_SERVICE_RADIUS.")

        # ---------------------------------------------------------------------
        # Test 9: Application Pagination
        # ---------------------------------------------------------------------
        print("\n[9] Testing Application History Pagination...")
        pag_res = await service.list_worker_applications(w1, page=1, page_size=1)
        assert pag_res.page == 1
        assert pag_res.page_size == 1
        assert len(pag_res.items) == 1
        print("    [PASS] Application listing pagination parameters verified.")

    finally:
        print("\n[CLEANUP] Cleaning up test applications, bookings, profiles, and users from Atlas...")
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
    print("ALL WORKER JOB APPLICATION VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_job_application_verification())
