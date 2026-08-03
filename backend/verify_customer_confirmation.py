"""
KaamSetu — Phase 4.7.3: Customer Confirmation & Service Acceptance Automated Verification

Verifies:
1. Customer completion review endpoint GET /customer/bookings/{id}/completion.
2. Customer confirmation endpoint PUT /customer/bookings/{id}/confirm.
3. Automatic Timeline Event recording for "Customer Confirmed Completion".
4. Rejection of confirmation by non-owner customer (403 BOOKING_ACCESS_DENIED).
5. Rejection of confirmation on incomplete bookings (400 BOOKING_NOT_WORK_COMPLETED).
6. Rejection of duplicate confirmation (400 SAME_STATUS_TRANSITION).
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
from app.booking.schemas import CompleteJobRequest, ConfirmCompletionRequest
from app.application.models import JobApplication
from app.quotation.models import Quotation
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException


async def main():
    print("===========================================================================")
    print("KAAMSETU — CUSTOMER CONFIRMATION (PHASE 4.7.3) VERIFICATION")
    print("===========================================================================\n")

    await connect_to_database(document_models=[User, Booking, JobApplication, Quotation])

    print("[0] Initializing database & creating test fixtures...")
    ts = secrets.token_hex(4)

    # 1. Create Customer 1 (Owner)
    c1 = User(
        email=f"conf_c1_{ts}@kaamtest.com",
        phone=f"+9199{ts[:8]}",
        full_name="Owner Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await c1.save()

    # 2. Create Customer 2 (Non-owner)
    c2 = User(
        email=f"conf_c2_{ts}@kaamtest.com",
        phone=f"+9198{ts[:8]}",
        full_name="Other Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await c2.save()

    # 3. Create Assigned Worker
    w1 = User(
        email=f"conf_w1_{ts}@kaamtest.com",
        phone=f"+9197{ts[:8]}",
        full_name="Execution Worker",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w1.save()

    # 4. Create Booking
    b_num = await BookingRepository.generate_booking_number()
    booking = Booking(
        booking_number=b_num,
        customer_id=c1.id,
        worker_id=w1.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.ASSIGNED,
        assigned_at=datetime.now(timezone.utc),
        service_snapshot=ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Plumbing Pipe Repair",
            category_id=str(PydanticObjectId()),
            category_slug="plumber",
            base_market_price=850.0,
            estimated_duration_minutes=45,
        ),
        address_snapshot=AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Owner Customer",
            phone=c1.phone,
            address_line_1="789 Confirmation Rd",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
        ),
    )
    booking = await BookingRepository.create(booking)
    print(f"    [PASS] Test Booking created: {booking.booking_number} (ID: {booking.id})")

    # -------------------------------------------------------------------------
    # TEST 1: Reject Confirmation on Incomplete Booking (ASSIGNED)
    # -------------------------------------------------------------------------
    print("\n[1] Testing premature confirmation rejection (ASSIGNED -> CUSTOMER_CONFIRMED)...")
    try:
        await BookingService.confirm_booking_completion(c1, str(booking.id))
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "BOOKING_NOT_WORK_COMPLETED"
        print("    [PASS] Premature confirmation blocked with 400 BOOKING_NOT_WORK_COMPLETED.")

    # -------------------------------------------------------------------------
    # TEST 2: Execute Job to WORK_COMPLETED state
    # -------------------------------------------------------------------------
    print("\n[2] Executing worker steps (ASSIGNED -> EN_ROUTE -> ARRIVED -> IN_PROGRESS -> WORK_COMPLETED)...")
    await BookingService.start_travel(w1, str(booking.id))
    await BookingService.mark_arrived(w1, str(booking.id))
    await BookingService.start_work(w1, str(booking.id))

    b_photos = ["https://res.cloudinary.com/kaamsetu/pipe_before.jpg"]
    a_photos = ["https://res.cloudinary.com/kaamsetu/pipe_after.jpg"]
    comp_res = await BookingService.complete_work(
        worker_user=w1,
        booking_id=str(booking.id),
        payload=CompleteJobRequest(
            completion_notes="Replaced faulty PVC joint and tested water flow.",
            work_summary="Joint replacement & leak fix completed.",
            before_photos=b_photos,
            after_photos=a_photos,
        ),
    )
    assert comp_res.status == BookingStatus.WORK_COMPLETED.value
    print("    [PASS] Job execution advanced to WORK_COMPLETED.")

    # -------------------------------------------------------------------------
    # TEST 3: GET /customer/bookings/{id}/completion Payload Inspection
    # -------------------------------------------------------------------------
    print("\n[3] Testing GET /customer/bookings/{id}/completion review payload...")
    review_res = await BookingService.get_customer_completion_review(c1, str(booking.id))
    assert review_res.booking_id == str(booking.id)
    assert review_res.service_name == "Plumbing Pipe Repair"
    assert review_res.status == BookingStatus.WORK_COMPLETED.value
    assert len(review_res.before_photos) == 1
    assert len(review_res.after_photos) == 1
    assert review_res.completion_notes == "Replaced faulty PVC joint and tested water flow."
    assert len(review_res.timeline) >= 4
    print("    [PASS] Completion review payload returned all completion details & timeline events.")

    # -------------------------------------------------------------------------
    # TEST 4: Reject Unauthorized Customer Confirmation (Customer 2)
    # -------------------------------------------------------------------------
    print("\n[4] Testing unauthorized customer confirmation attempt (Customer 2)...")
    try:
        await BookingService.confirm_booking_completion(c2, str(booking.id))
        assert False, "Should have raised ForbiddenException"
    except ForbiddenException as e:
        assert e.error_code == "BOOKING_ACCESS_DENIED"
        print("    [PASS] Unauthorized customer confirmation blocked with 403 BOOKING_ACCESS_DENIED.")

    # -------------------------------------------------------------------------
    # TEST 5: Successful Customer Confirmation (Customer 1)
    # -------------------------------------------------------------------------
    print("\n[5] Testing successful customer confirmation (Customer 1)...")
    conf_res = await BookingService.confirm_booking_completion(
        customer_user=c1,
        booking_id=str(booking.id),
        notes="Plumbing work verified. No leaks found. Satisfied with work.",
    )
    assert conf_res.status == BookingStatus.CUSTOMER_CONFIRMED.value
    assert len(conf_res.timeline) >= 5
    assert conf_res.timeline[-1].title == "Customer Confirmed Completion"
    assert conf_res.timeline[-1].status == BookingStatus.CUSTOMER_CONFIRMED.value
    print("    [PASS] Confirmation successful. Status: CUSTOMER_CONFIRMED, Timeline Event logged.")

    # -------------------------------------------------------------------------
    # TEST 6: Reject Duplicate Confirmation Attempt
    # -------------------------------------------------------------------------
    print("\n[6] Testing duplicate confirmation rejection...")
    try:
        await BookingService.confirm_booking_completion(c1, str(booking.id))
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code in ("SAME_STATUS_TRANSITION", "BOOKING_TERMINATED")
        print("    [PASS] Duplicate confirmation attempt correctly blocked.")

    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test fixtures...")
    await booking.delete()
    await c1.delete()
    await c2.delete()
    await w1.delete()
    await close_database_connection()
    print("    [PASS] Test data cleaned up successfully.")

    print("\n===========================================================================")
    print("ALL CUSTOMER CONFIRMATION VERIFICATION TESTS PASSED!")
    print("===========================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
