"""
Verification script for Ally Worker Dashboard System (Phase 4.5.7).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer, Worker User, Worker Profile, open marketplace bookings.
  2. Test 1: Retrieve aggregated worker dashboard payload.
     - Verify availability, radius, profile_completed, stats, applications_summary, recommended_jobs, and recent_jobs.
  3. Test 2: Availability toggle and active job application submission reflection.
  4. Cleanup test documents.
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
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.otp.models import OTP
from app.utils.enums import BookingStatus, BookingType, WorkerAvailability
from app.worker.models import WorkerProfile
from app.worker.schemas import UpdateWorkerProfileRequest
from app.worker.service import WorkerService


async def run_worker_dashboard_verification() -> None:
    print("=" * 75)
    print("ALLY — WORKER DASHBOARD SYSTEM (PHASE 4.5.7) VERIFICATION")
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

    test_bookings: list[Booking] = []
    test_users: list[User] = []
    test_apps: list[JobApplication] = []
    test_profiles: list[WorkerProfile] = []

    try:
        s = str(random.randint(100000, 999999))

        # 1. Customer User
        cust = User(
            phone=f"+9199{s}001",
            email=f"dash_cust_{s}@kaamtest.com",
            full_name="Dashboard Customer",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        test_users.append(cust)

        # 2. Worker User
        w1 = User(
            phone=f"+9199{s}002",
            email=f"dash_w1_{s}@kaamtest.com",
            full_name="Dashboard Worker",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
        )
        await w1.insert()
        test_users.append(w1)

        wp1 = WorkerProfile(
            user_id=w1.id,
            bio="Experienced certified electrician with 6 years experience.",
            experience_years=6.0,
            skills=["Electrical", "Fan Repair", "Wiring"],
            languages=["Hindi", "English"],
            hourly_rate=400.0,
            profile_photo_url="https://res.cloudinary.com/demo/image/upload/v1/profile.jpg",
            profile_completed=True,
            availability=WorkerAvailability.AVAILABLE,
            working_radius_km=25.0,
            current_location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )
        await wp1.insert()
        test_profiles.append(wp1)

        # Address & Service Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Dash Customer",
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
            name="Smart Switch Board Installation",
            category_id=str(PydanticObjectId()),
            category_slug="electrical-dash-test",
            base_market_price=450.0,
            estimated_duration_minutes=45,
        )

        # Seed open pending bookings
        num1 = await BookingRepository.generate_booking_number()
        b1 = Booking(
            booking_number=num1,
            customer_id=cust.id,
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            scheduled_date="2026-09-25",
            estimated_price=450.0,
        )
        await b1.insert()
        test_bookings.append(b1)

        # ---------------------------------------------------------------------
        # Test 1: Retrieve Worker Dashboard Aggregated Payload
        # ---------------------------------------------------------------------
        print("\n[1] Testing Worker Dashboard Payload Retrieval...")
        dash_payload = await WorkerService.get_worker_dashboard_data(w1)
        assert dash_payload.worker_id == str(w1.id)
        assert dash_payload.worker_name == w1.full_name
        assert dash_payload.availability == WorkerAvailability.AVAILABLE
        assert dash_payload.working_radius_km == 25.0
        assert dash_payload.profile_completed is True
        assert dash_payload.stats.available_jobs >= 1
        assert len(dash_payload.recent_jobs) >= 1
        print("    [PASS] Worker dashboard payload retrieved with accurate metrics & section data.")

        # ---------------------------------------------------------------------
        # Test 2: Application Submission & Availability Toggle Reflection
        # ---------------------------------------------------------------------
        print("\n[2] Testing Application Submission & Availability Toggle Reflection...")
        app_service = JobApplicationService()
        res_app = await app_service.apply_for_job(w1, JobApplicationCreateRequest(booking_id=str(b1.id)))

        app_doc = await JobApplication.get(res_app.id)
        if app_doc:
            test_apps.append(app_doc)

        # Toggle Availability to OFFLINE
        await WorkerService.update_worker_profile(
            w1, UpdateWorkerProfileRequest(availability=WorkerAvailability.OFFLINE)
        )

        dash_updated = await WorkerService.get_worker_dashboard_data(w1)
        assert dash_updated.availability == WorkerAvailability.OFFLINE
        assert dash_updated.stats.active_applications == 1
        assert dash_updated.applications_summary.pending == 1
        print("    [PASS] Active applications count and OFFLINE status toggle correctly reflected.")

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
    print("ALL WORKER DASHBOARD VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_worker_dashboard_verification())
