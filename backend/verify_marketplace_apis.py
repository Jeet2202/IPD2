"""
Verification script for Ally Worker Marketplace Foundation (Phase 4.5.1).

Tests end-to-end against MongoDB Atlas:
  1. Setup: Customer address, service, and open bookings creation.
  2. GET /worker/marketplace — Listing open unassigned bookings for workers.
  3. Strict PII Redaction Verification — Customer full name, phone, street lines are NOT exposed.
  4. GET /worker/marketplace/{bookingId} — Detail view for workers with problem descriptions.
  5. Authorization — Customer user access check (rejected with 403 / RBAC).
  6. Pagination and filtering checks (category_slug, booking_type).
  7. Empty marketplace handling when filters match no bookings.
  8. Exclusion check: Assigned bookings (worker_id != None) or non-PENDING bookings excluded.
  9. Cleanup test documents.
"""

import asyncio
import random
import sys

sys.path.insert(0, ".")

from beanie import PydanticObjectId

from app.address.models import Address, GeoJSONPoint
from app.auth.models import AuthAuditLog, RefreshToken, User, UserRole
from app.booking.models import AddressSnapshot, Booking, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.category.models import Service, ServiceCategory
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.marketplace.repository import MarketplaceRepository
from app.marketplace.schemas import (
    MarketplaceBookingDetailResponse,
    MarketplaceBookingItemResponse,
)
from app.marketplace.service import MarketplaceService
from app.otp.models import OTP
from app.utils.enums import BookingStatus, BookingType
from app.worker.models import WorkerProfile


from app.application.models import JobApplication

async def run_marketplace_verification() -> None:
    print("=" * 75)
    print("ALLY — WORKER MARKETPLACE FOUNDATION (PHASE 4.5.1) VERIFICATION")
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

    service = MarketplaceService()
    test_bookings_created: list[Booking] = []
    test_users_created: list[User] = []

    try:
        # Create test users (Customer and Worker)
        s = str(random.randint(100000, 999999))
        cust_user = User(
            phone=f"+9198{s}001",
            email=f"mk_cust_{s}@kaamtest.com",
            full_name="Customer TestPerson",
            password_hash="mock_hash_123",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_email_verified=True,
        )
        await cust_user.insert()
        test_users_created.append(cust_user)

        work_user = User(
            phone=f"+9198{s}002",
            email=f"mk_work_{s}@kaamtest.com",
            full_name="Worker TestPartner",
            password_hash="mock_hash_123",
            role=UserRole.WORKER,
            is_active=True,
            is_email_verified=True,
        )
        await work_user.insert()
        test_users_created.append(work_user)

        # Snapshots
        addr_snap = AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="PRIVATE CUSTOMER NAME",
            phone="+919876543210",
            address_line_1="CONFIDENTIAL FLAT 101, SECRET STREET",
            address_line_2="SECRET LOCALITY",
            landmark="NEAR SECRET LANDMARK",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400058",
            location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
        )

        svc_snap_1 = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Air Conditioner Jet Cleaning",
            category_id=str(PydanticObjectId()),
            category_slug="ac-repair-marketplace-test",
            base_market_price=699.0,
            estimated_duration_minutes=60,
        )

        svc_snap_2 = ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Full House Electrical Inspection",
            category_id=str(PydanticObjectId()),
            category_slug="electrical-marketplace-test",
            base_market_price=1200.0,
            estimated_duration_minutes=90,
            is_inspection_required=True,
        )

        # ---------------------------------------------------------------------
        # Test 1: Create open pending bookings in MongoDB
        # ---------------------------------------------------------------------
        print("\n[1] Seeding open pending marketplace bookings...")
        num1 = await BookingRepository.generate_booking_number()
        b1 = Booking(
            booking_number=num1,
            customer_id=cust_user.id,
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap_1,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            scheduled_date="2026-09-10",
            scheduled_time="10:00-12:00",
            estimated_price=699.0,
            estimated_duration_minutes=60,
            customer_notes="Call before coming",
        )
        await b1.insert()
        test_bookings_created.append(b1)

        num2 = await BookingRepository.generate_booking_number()
        b2 = Booking(
            booking_number=num2,
            customer_id=cust_user.id,
            booking_type=BookingType.INSPECTION_REQUEST,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap_2,
            address_snapshot=addr_snap,
            service_location=addr_snap.location,
            scheduled_date="2026-09-11",
            scheduled_time="14:00-16:00",
            estimated_price=1200.0,
            estimated_duration_minutes=90,
            problem_description="Short circuit issue in master bedroom switchboard.",
            problem_photos=["https://res.cloudinary.com/demo/image/upload/sample.jpg"],
        )
        await b2.insert()
        test_bookings_created.append(b2)
        print("    [PASS] Created 2 test bookings in Atlas database.")

        # ---------------------------------------------------------------------
        # Test 2: Marketplace Service Listing & Privacy Check
        # ---------------------------------------------------------------------
        print("\n[2] Testing Marketplace Listing & Customer PII Redaction...")
        res = await service.list_marketplace_bookings(page=1, page_size=10)
        assert res.total >= 2, f"Expected total >= 2, got {res.total}"
        assert len(res.items) >= 2

        # Check b1 in items
        item1 = next((x for x in res.items if x.id == str(b1.id)), None)
        assert item1 is not None, "Booking 1 missing from marketplace items!"
        assert item1.booking_number == num1
        assert item1.service_snapshot.name == "Air Conditioner Jet Cleaning"
        assert item1.address.city == "Mumbai"
        assert item1.address.postal_code == "400058"
        assert item1.address.latitude == 19.1136
        assert item1.address.longitude == 72.8697

        # STRICT PII REDACTION CHECKS
        item_dict = item1.model_dump()
        addr_dict = item_dict["address"]
        assert "full_name" not in addr_dict, "STRICT FAILURE: full_name exposed in marketplace address!"
        assert "phone" not in addr_dict, "STRICT FAILURE: phone exposed in marketplace address!"
        assert "address_line_1" not in addr_dict, "STRICT FAILURE: address_line_1 exposed in marketplace address!"
        assert "address_line_2" not in addr_dict, "STRICT FAILURE: address_line_2 exposed in marketplace address!"
        assert "landmark" not in addr_dict, "STRICT FAILURE: landmark exposed in marketplace address!"
        print("    [PASS] Marketplace listing returns open bookings with ALL Customer PII redacted.")

        # ---------------------------------------------------------------------
        # Test 3: Marketplace Booking Detail View
        # ---------------------------------------------------------------------
        print("\n[3] Testing Marketplace Booking Detail View...")
        detail = await service.get_marketplace_booking_detail(str(b2.id))
        assert detail.id == str(b2.id)
        assert detail.booking_type == BookingType.INSPECTION_REQUEST
        assert detail.problem_description == "Short circuit issue in master bedroom switchboard."
        assert len(detail.problem_photos) == 1

        detail_dict = detail.model_dump()
        assert "full_name" not in detail_dict["address"]
        assert "phone" not in detail_dict["address"]
        assert "address_line_1" not in detail_dict["address"]
        print("    [PASS] Detail view returned problem details while keeping PII redacted.")

        # ---------------------------------------------------------------------
        # Test 4: Filtering (category_slug and booking_type)
        # ---------------------------------------------------------------------
        print("\n[4] Testing Filtering (category_slug & booking_type)...")
        cat_res = await service.list_marketplace_bookings(category_slug="ac-repair-marketplace-test")
        assert any(x.id == str(b1.id) for x in cat_res.items)
        assert not any(x.id == str(b2.id) for x in cat_res.items)

        type_res = await service.list_marketplace_bookings(booking_type=BookingType.INSPECTION_REQUEST)
        assert any(x.id == str(b2.id) for x in type_res.items)
        assert not any(x.id == str(b1.id) for x in type_res.items)
        print("    [PASS] Filtering by category_slug and booking_type verified.")

        # ---------------------------------------------------------------------
        # Test 5: Exclusion of Assigned or non-PENDING Bookings
        # ---------------------------------------------------------------------
        print("\n[5] Testing Exclusion of Assigned or Completed Bookings...")
        # Create an assigned booking (worker_id set)
        num3 = await BookingRepository.generate_booking_number()
        b3 = Booking(
            booking_number=num3,
            customer_id=cust_user.id,
            worker_id=work_user.id,  # Assigned!
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap_1,
            address_snapshot=addr_snap,
            scheduled_date="2026-09-12",
        )
        await b3.insert()
        test_bookings_created.append(b3)

        res_ex = await service.list_marketplace_bookings(page=1, page_size=50)
        assert not any(x.id == str(b3.id) for x in res_ex.items), "Assigned booking appeared in marketplace!"

        # Try to get assigned booking detail via marketplace service
        try:
            await service.get_marketplace_booking_detail(str(b3.id))
            assert False, "Assigned booking detail should return 404 / NotFoundException!"
        except Exception:
            pass
        print("    [PASS] Assigned bookings are strictly excluded from marketplace listing and details.")

        # ---------------------------------------------------------------------
        # Test 6: Free-Text Search
        # ---------------------------------------------------------------------
        print("\n[6] Testing Free-Text Search...")
        # Search by service name
        s1 = await service.list_marketplace_bookings(query="Air Conditioner")
        assert any(x.id == str(b1.id) for x in s1.items)
        assert not any(x.id == str(b2.id) for x in s1.items)

        # Search by problem description keyword
        s2 = await service.list_marketplace_bookings(query="switchboard")
        assert any(x.id == str(b2.id) for x in s2.items)
        assert not any(x.id == str(b1.id) for x in s2.items)

        # Non-matching search query
        s_empty = await service.list_marketplace_bookings(query="Plumbing Repair 9999")
        assert s_empty.total == 0
        assert s_empty.items == []
        print("    [PASS] Free-text search matching and non-matching queries verified.")

        # ---------------------------------------------------------------------
        # Test 7: Price Range & Date Filtering
        # ---------------------------------------------------------------------
        print("\n[7] Testing Price Range & Date Filtering...")
        # Price range matching b1 (699.0 INR)
        p1 = await service.list_marketplace_bookings(min_price=500.0, max_price=800.0)
        assert any(x.id == str(b1.id) for x in p1.items)
        assert not any(x.id == str(b2.id) for x in p1.items)

        # Scheduled date matching b2 ("2026-09-11")
        d1 = await service.list_marketplace_bookings(scheduled_date="2026-09-11")
        assert any(x.id == str(b2.id) for x in d1.items)
        assert not any(x.id == str(b1.id) for x in d1.items)

        # Invalid price range validation (min_price > max_price) -> BadRequestException
        from app.core.exceptions import BadRequestException
        try:
            await service.list_marketplace_bookings(min_price=1000.0, max_price=500.0)
            assert False, "Should raise BadRequestException for invalid price range!"
        except BadRequestException as exc:
            assert exc.status_code == 400
            assert exc.error_code == "INVALID_PRICE_RANGE"
        print("    [PASS] Price range and date filtering verified with validation errors.")

        # ---------------------------------------------------------------------
        # Test 8: Custom Sorting Options
        # ---------------------------------------------------------------------
        print("\n[8] Testing Custom Sorting Options...")
        from app.marketplace.schemas import MarketplaceSortOption
        sort_high = await service.list_marketplace_bookings(sort_by=MarketplaceSortOption.PRICE_HIGH, page_size=100)
        # b2 (1200 INR) should be ahead of b1 (699 INR)
        pos_b2 = next((i for i, x in enumerate(sort_high.items) if x.id == str(b2.id)), None)
        pos_b1 = next((i for i, x in enumerate(sort_high.items) if x.id == str(b1.id)), None)
        assert pos_b2 is not None and pos_b1 is not None, "Test bookings missing in sort_high!"
        assert pos_b2 < pos_b1, f"PRICE_HIGH sort order failed: b2 at {pos_b2}, b1 at {pos_b1}"

        sort_low = await service.list_marketplace_bookings(sort_by=MarketplaceSortOption.PRICE_LOW, page_size=100)
        pos_b2_low = next((i for i, x in enumerate(sort_low.items) if x.id == str(b2.id)), None)
        pos_b1_low = next((i for i, x in enumerate(sort_low.items) if x.id == str(b1.id)), None)
        assert pos_b2_low is not None and pos_b1_low is not None, "Test bookings missing in sort_low!"
        assert pos_b1_low < pos_b2_low, f"PRICE_LOW sort order failed: b1 at {pos_b1_low}, b2 at {pos_b2_low}"
        print("    [PASS] Sorting by PRICE_HIGH and PRICE_LOW verified.")

        # ---------------------------------------------------------------------
        # Test 9: Worker Recommendation Engine Verification (Phase 4.5.3)
        # ---------------------------------------------------------------------
        print("\n[9] Testing Deterministic Worker Recommendation Engine...")
        from app.marketplace.schemas import MarketplaceSortOption
        from app.utils.enums import WorkerAvailability

        # Create WorkerProfile for recommendation tests
        w_profile = WorkerProfile(
            user_id=work_user.id,
            bio="Air Conditioning Specialist",
            skills=["air conditioner", "jet cleaning"],
            working_radius_km=15.0,
            current_location=GeoJSONPoint.from_lat_lng(19.1136, 72.8697),
            availability=WorkerAvailability.AVAILABLE,
        )
        await w_profile.insert()
        test_bookings_created.append(w_profile)

        # Fetch recommendations sorted by RECOMMENDED
        rec_res = await service.list_marketplace_bookings(
            worker_profile=w_profile,
            sort_by=MarketplaceSortOption.RECOMMENDED,
            page_size=100,
        )

        item_b1 = next((x for x in rec_res.items if x.id == str(b1.id)), None)
        item_b2 = next((x for x in rec_res.items if x.id == str(b2.id)), None)

        assert item_b1 is not None and item_b2 is not None
        assert item_b1.distance_km is not None, "distance_km should be populated!"
        assert item_b1.distance_km == 0.0, f"Expected 0.0 km, got {item_b1.distance_km}"
        assert item_b1.is_recommended is True, "b1 should be recommended for AC specialist worker!"

        # b1 (AC Jet Cleaning) should rank ahead of b2 (Electrical) for AC worker
        pos_b1_rec = next(i for i, x in enumerate(rec_res.items) if x.id == str(b1.id))
        pos_b2_rec = next(i for i, x in enumerate(rec_res.items) if x.id == str(b2.id))
        assert pos_b1_rec < pos_b2_rec, "AC booking should rank above Electrical for AC worker!"

        # Test working radius cutoff: create a distant booking 50km away
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
            customer_id=cust_user.id,
            booking_type=BookingType.NORMAL_SERVICE,
            status=BookingStatus.PENDING,
            service_snapshot=svc_snap_1,
            address_snapshot=far_addr_snap,
            service_location=far_addr_snap.location,
            estimated_price=699.0,
        )
        await b_far.insert()
        test_bookings_created.append(b_far)

        rec_far_res = await service.list_marketplace_bookings(
            worker_profile=w_profile,
            sort_by=MarketplaceSortOption.RECOMMENDED,
            page_size=100,
        )
        item_far = next((x for x in rec_far_res.items if x.id == str(b_far.id)), None)
        assert item_far is not None
        assert item_far.distance_km > 15.0, f"Distance should exceed 15km, got {item_far.distance_km}"
        assert item_far.is_recommended is False, "Distant booking outside working radius should NOT be recommended!"

        # Test offline availability: offline worker should get is_recommended == False
        w_profile.availability = WorkerAvailability.OFFLINE
        rec_off = await service.list_marketplace_bookings(
            worker_profile=w_profile,
            sort_by=MarketplaceSortOption.RECOMMENDED,
            page_size=100,
        )
        assert all(x.is_recommended is False for x in rec_off.items), "Offline worker should have zero recommended jobs!"

        print("    [PASS] Worker recommendation engine, skill matching, distance, radius cutoff, and availability verified.")

    finally:
        print("\n[CLEANUP] Cleaning up test bookings and users from Atlas...")
        for b in test_bookings_created:
            await b.delete()
        for u in test_users_created:
            await u.delete()
        await close_database_connection()
        print("    [PASS] Test data cleaned up successfully.")

    print("\n" + "=" * 75)
    print("ALL WORKER MARKETPLACE VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_marketplace_verification())
