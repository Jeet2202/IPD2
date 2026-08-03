"""
KaamSetu — Phase 4.7.6: Ratings & Reviews System Automated Verification

Verifies:
1. Review creation POST /customer/reviews for CUSTOMER_CONFIRMED booking.
2. Incremental update of WorkerProfile rating aggregates (rolling weighted averages & rating distribution).
3. Duplicate review submission prevention per booking (400 DUPLICATE_REVIEW).
4. Review attempt rejection on unconfirmed booking (400 BOOKING_NOT_CONFIRMED).
5. Unauthorized customer review rejection (403 BOOKING_ACCESS_DENIED).
6. GET /customer/reviews/{bookingId} inspection.
7. GET /worker/reviews/{workerId} paginated listing.
"""

import asyncio, secrets
from datetime import datetime, timezone
from beanie import PydanticObjectId

from app.database import connect_to_database, close_database_connection
from app.auth.models import User
from app.utils.enums import UserRole, BookingStatus, BookingType
from app.booking.models import Booking, AddressSnapshot, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.booking.service import BookingService
from app.worker.models import WorkerProfile
from app.review.models import Review
from app.review.service import ReviewService
from app.review.schemas import CreateReviewRequest
from app.application.models import JobApplication
from app.quotation.models import Quotation
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException


async def main():
    print("===========================================================================")
    print("KAAMSETU — RATINGS & REVIEWS SYSTEM (PHASE 4.7.6) VERIFICATION")
    print("===========================================================================\n")

    await connect_to_database(document_models=[User, Booking, JobApplication, Quotation, Review, WorkerProfile])

    print("[0] Initializing database & creating test fixtures...")
    ts = secrets.token_hex(4)

    # 1. Create Customer 1 (Owner)
    c1 = User(
        email=f"rev_c1_{ts}@kaamtest.com",
        phone=f"+9199{ts[:8]}",
        full_name="Reviewer Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await c1.save()

    # 2. Create Customer 2 (Unauthorized)
    c2 = User(
        email=f"rev_c2_{ts}@kaamtest.com",
        phone=f"+9198{ts[:8]}",
        full_name="Other Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await c2.save()

    # 3. Create Worker User & Worker Profile
    w1_user = User(
        email=f"rev_w1_{ts}@kaamtest.com",
        phone=f"+9197{ts[:8]}",
        full_name="Reviewed Worker",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w1_user.save()

    w1_profile = WorkerProfile(
        user_id=w1_user.id,
        rating_average=0.0,
        total_reviews=0,
        rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
    )
    await w1_profile.save()

    # 4. Create Booking 1 (Confirmed)
    b1_num = await BookingRepository.generate_booking_number()
    b1 = Booking(
        booking_number=b1_num,
        customer_id=c1.id,
        worker_id=w1_user.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.CUSTOMER_CONFIRMED,
        completed_at=datetime.now(timezone.utc),
        service_snapshot=ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Washing Machine Repair",
            category_id=str(PydanticObjectId()),
            category_slug="appliance_repair",
            base_market_price=900.0,
            estimated_duration_minutes=60,
        ),
        address_snapshot=AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Reviewer Customer",
            phone=c1.phone,
            address_line_1="123 Review Blvd",
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600001",
        ),
    )
    b1 = await BookingRepository.create(b1)

    # 5. Create Booking 2 (In Progress - Unconfirmed)
    b2_num = await BookingRepository.generate_booking_number()
    b2 = Booking(
        booking_number=b2_num,
        customer_id=c1.id,
        worker_id=w1_user.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.IN_PROGRESS,
        service_snapshot=b1.service_snapshot,
        address_snapshot=b1.address_snapshot,
    )
    b2 = await BookingRepository.create(b2)
    print(f"    [PASS] Test Booking 1 created: {b1.booking_number} (CUSTOMER_CONFIRMED)")
    print(f"    [PASS] Test Booking 2 created: {b2.booking_number} (IN_PROGRESS)")

    # -------------------------------------------------------------------------
    # TEST 1: Reject Review on Unconfirmed Booking (b2)
    # -------------------------------------------------------------------------
    print("\n[1] Testing review rejection on unconfirmed booking (IN_PROGRESS)...")
    try:
        await ReviewService.create_review(
            c1,
            CreateReviewRequest(
                booking_id=str(b2.id),
                overall_rating=5.0,
                punctuality_rating=5.0,
                quality_rating=5.0,
                professionalism_rating=5.0,
                communication_rating=5.0,
            ),
        )
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "BOOKING_NOT_CONFIRMED"
        print("    [PASS] Review on unconfirmed booking blocked with 400 BOOKING_NOT_CONFIRMED.")

    # -------------------------------------------------------------------------
    # TEST 2: Reject Review Submission by Unauthorized Customer (c2 on b1)
    # -------------------------------------------------------------------------
    print("\n[2] Testing review rejection for unauthorized customer...")
    try:
        await ReviewService.create_review(
            c2,
            CreateReviewRequest(
                booking_id=str(b1.id),
                overall_rating=5.0,
                punctuality_rating=5.0,
                quality_rating=5.0,
                professionalism_rating=5.0,
                communication_rating=5.0,
            ),
        )
        assert False, "Should have raised ForbiddenException"
    except ForbiddenException as e:
        assert e.error_code == "BOOKING_ACCESS_DENIED"
        print("    [PASS] Unauthorized review attempt blocked with 403 BOOKING_ACCESS_DENIED.")

    # -------------------------------------------------------------------------
    # TEST 3: Successful Review Submission (Review 1: 5.0 Rating)
    # -------------------------------------------------------------------------
    print("\n[3] Submitting Review 1 (Overall: 5.0, Punctuality: 5.0, Quality: 5.0)...")
    rev1 = await ReviewService.create_review(
        c1,
        CreateReviewRequest(
            booking_id=str(b1.id),
            overall_rating=5.0,
            punctuality_rating=5.0,
            quality_rating=5.0,
            professionalism_rating=4.0,
            communication_rating=5.0,
            review_title="Punctual & Expert Service",
            review_comment="Arrived right on time and fixed washing machine noise completely.",
            would_recommend=True,
        ),
    )
    assert rev1.booking_id == str(b1.id)
    assert rev1.overall_rating == 5.0
    print("    [PASS] Review 1 created successfully.")

    # Check Worker Profile Incremental Metrics after Review 1
    w1_p_updated = await WorkerProfile.find_one(WorkerProfile.user_id == w1_user.id)
    assert w1_p_updated.total_reviews == 1
    assert w1_p_updated.rating_average == 5.0
    assert w1_p_updated.rating_distribution[5] == 1
    assert w1_p_updated.recommendation_percentage == 100.0
    print("    [PASS] WorkerProfile metrics updated incrementally (Total: 1, Avg: 5.0).")

    # -------------------------------------------------------------------------
    # TEST 4: Reject Duplicate Review on Same Booking
    # -------------------------------------------------------------------------
    print("\n[4] Testing duplicate review rejection on Booking 1...")
    try:
        await ReviewService.create_review(
            c1,
            CreateReviewRequest(
                booking_id=str(b1.id),
                overall_rating=4.0,
                punctuality_rating=4.0,
                quality_rating=4.0,
                professionalism_rating=4.0,
                communication_rating=4.0,
            ),
        )
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "DUPLICATE_REVIEW"
        print("    [PASS] Duplicate review blocked with 400 DUPLICATE_REVIEW.")

    # -------------------------------------------------------------------------
    # TEST 5: Second Confirmed Booking & Rolling Weighted Average Update (Review 2: 4.0 Rating)
    # -------------------------------------------------------------------------
    print("\n[5] Creating Booking 3 and submitting Review 2 (Overall: 4.0)...")
    b3_num = await BookingRepository.generate_booking_number()
    b3 = Booking(
        booking_number=b3_num,
        customer_id=c1.id,
        worker_id=w1_user.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.CUSTOMER_CONFIRMED,
        completed_at=datetime.now(timezone.utc),
        service_snapshot=b1.service_snapshot,
        address_snapshot=b1.address_snapshot,
    )
    b3 = await BookingRepository.create(b3)

    rev2 = await ReviewService.create_review(
        c1,
        CreateReviewRequest(
            booking_id=str(b3.id),
            overall_rating=4.0,
            punctuality_rating=4.0,
            quality_rating=4.0,
            professionalism_rating=4.0,
            communication_rating=4.0,
            review_title="Good service overall",
            review_comment="Good job done.",
            would_recommend=True,
        ),
    )
    assert rev2.overall_rating == 4.0

    # Expected rolling average = (5.0 + 4.0) / 2 = 4.5
    w1_p_after2 = await WorkerProfile.find_one(WorkerProfile.user_id == w1_user.id)
    assert w1_p_after2.total_reviews == 2
    assert w1_p_after2.rating_average == 4.5
    assert w1_p_after2.rating_distribution[5] == 1
    assert w1_p_after2.rating_distribution[4] == 1
    print("    [PASS] Rolling weighted average formula verified (Total: 2, Avg: 4.5, Star 5: 1, Star 4: 1).")

    # -------------------------------------------------------------------------
    # TEST 6: GET /customer/reviews/{bookingId} Inspection
    # -------------------------------------------------------------------------
    print("\n[6] Testing GET /customer/reviews/{bookingId}...")
    b1_rev = await ReviewService.get_review_by_booking(c1, str(b1.id))
    assert b1_rev.booking_id == str(b1.id)
    assert b1_rev.review_title == "Punctual & Expert Service"
    print("    [PASS] Review by booking ID fetched successfully.")

    # -------------------------------------------------------------------------
    # TEST 7: GET /worker/reviews/{workerId} Paginated Listing
    # -------------------------------------------------------------------------
    print("\n[7] Testing GET /worker/reviews/{workerId} paginated listing...")
    worker_revs = await ReviewService.get_worker_reviews(str(w1_user.id), page=1, page_size=10)
    assert worker_revs.total == 2
    assert len(worker_revs.reviews) == 2
    print("    [PASS] Paginated worker review list retrieved 2 reviews.")

    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test fixtures...")
    await Review.find(Review.worker_id == w1_user.id).delete()
    await b1.delete()
    await b2.delete()
    await b3.delete()
    await c1.delete()
    await c2.delete()
    await w1_profile.delete()
    await w1_user.delete()
    await close_database_connection()
    print("    [PASS] Test data cleaned up successfully.")

    print("\n===========================================================================")
    print("ALL RATINGS & REVIEWS VERIFICATION TESTS PASSED!")
    print("===========================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
