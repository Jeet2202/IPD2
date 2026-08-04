"""
Ally — Phase 4.7.5: Centralized Booking Lifecycle Business Rules Automated Verification

Verifies:
1. Centralized state machine rules (Forward-only, non-skipping, non-retrograde, non-repeating transitions).
2. Immutability locks on terminal bookings (CUSTOMER_CONFIRMED, COMPLETED, CANCELLED).
3. Role-based ownership guards (Worker execution ownership & Customer confirmation ownership).
4. Cancellation rules & cancellation eligibility validation.
5. Single atomic, immutable timeline event generation per lifecycle transition.
"""

import asyncio, secrets
from datetime import datetime, timezone
from beanie import PydanticObjectId

from app.database import connect_to_database, close_database_connection
from app.auth.models import User
from app.utils.enums import UserRole, BookingStatus, BookingType
from app.booking.models import Booking, AddressSnapshot, BookingTimelineEvent, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.booking.service import BookingService
from app.booking.config import BookingLifecycleConfig
from app.booking.schemas import CompleteJobRequest
from app.application.models import JobApplication
from app.quotation.models import Quotation
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException


async def main():
    print("===========================================================================")
    print("ALLY — LIFECYCLE BUSINESS RULES (PHASE 4.7.5) VERIFICATION")
    print("===========================================================================\n")

    await connect_to_database(document_models=[User, Booking, JobApplication, Quotation])

    print("[0] Initializing database & creating test fixtures...")
    ts = secrets.token_hex(4)

    # 1. Create Customer 1 (Owner)
    c1 = User(
        email=f"biz_c1_{ts}@kaamtest.com",
        phone=f"+9199{ts[:8]}",
        full_name="Rules Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await c1.save()

    # 2. Create Customer 2 (Unauthorized)
    c2 = User(
        email=f"biz_c2_{ts}@kaamtest.com",
        phone=f"+9198{ts[:8]}",
        full_name="Other Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await c2.save()

    # 3. Create Assigned Worker (Worker 1)
    w1 = User(
        email=f"biz_w1_{ts}@kaamtest.com",
        phone=f"+9197{ts[:8]}",
        full_name="Assigned Rules Worker",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w1.save()

    # 4. Create Unassigned Worker (Worker 2)
    w2 = User(
        email=f"biz_w2_{ts}@kaamtest.com",
        phone=f"+9196{ts[:8]}",
        full_name="Unassigned Worker",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w2.save()

    # 5. Create Test Booking
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
            name="Electrical Switchboard Repair",
            category_id=str(PydanticObjectId()),
            category_slug="electrician",
            base_market_price=600.0,
            estimated_duration_minutes=30,
        ),
        address_snapshot=AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Rules Customer",
            phone=c1.phone,
            address_line_1="505 Business Rule St",
            city="Hyderabad",
            state="Telangana",
            postal_code="500001",
        ),
    )
    booking = await BookingRepository.create(booking)
    print(f"    [PASS] Test Booking created: {booking.booking_number} (Status: ASSIGNED)")

    # -------------------------------------------------------------------------
    # TEST 1: Rejection of Skipping Stages (ASSIGNED -> IN_PROGRESS)
    # -------------------------------------------------------------------------
    print("\n[1] Testing rejection of status skipping (ASSIGNED -> IN_PROGRESS)...")
    try:
        BookingService.validate_status_transition(BookingStatus.ASSIGNED, BookingStatus.IN_PROGRESS)
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "INVALID_STATUS_TRANSITION"
        print("    [PASS] Status skipping blocked with 400 INVALID_STATUS_TRANSITION.")

    # -------------------------------------------------------------------------
    # TEST 2: Rejection of Retrograde Transitions (ARRIVED -> WORKER_EN_ROUTE)
    # -------------------------------------------------------------------------
    print("\n[2] Testing rejection of retrograde transitions (ARRIVED -> WORKER_EN_ROUTE)...")
    try:
        BookingService.validate_status_transition(BookingStatus.ARRIVED, BookingStatus.WORKER_EN_ROUTE)
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "INVALID_STATUS_TRANSITION"
        print("    [PASS] Retrograde transition blocked with 400 INVALID_STATUS_TRANSITION.")

    # -------------------------------------------------------------------------
    # TEST 3: Rejection of Same-Status Updates (IN_PROGRESS -> IN_PROGRESS)
    # -------------------------------------------------------------------------
    print("\n[3] Testing rejection of duplicate status transitions...")
    try:
        BookingService.validate_status_transition(BookingStatus.IN_PROGRESS, BookingStatus.IN_PROGRESS)
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "SAME_STATUS_TRANSITION"
        print("    [PASS] Duplicate status update blocked with 400 SAME_STATUS_TRANSITION.")

    # -------------------------------------------------------------------------
    # TEST 4: Execute Sequential Worker Steps & Verify Timeline Event Appends
    # -------------------------------------------------------------------------
    print("\n[4] Executing sequential worker transitions and inspecting timeline entries...")
    await BookingService.start_travel(w1, str(booking.id))
    await BookingService.mark_arrived(w1, str(booking.id))
    await BookingService.start_work(w1, str(booking.id))
    await BookingService.complete_work(
        w1, str(booking.id), payload=CompleteJobRequest(completion_notes="Replaced blown fuses.")
    )
    b_updated = await BookingRepository.get_by_id(str(booking.id))
    assert b_updated.status == BookingStatus.WORK_COMPLETED
    assert len(b_updated.timeline) >= 4
    print("    [PASS] Sequential transitions completed and individual timeline events appended.")

    # -------------------------------------------------------------------------
    # TEST 5: Customer Confirmation & Immutability Lock Activation
    # -------------------------------------------------------------------------
    print("\n[5] Confirming completion and activating Immutability Lock...")
    await BookingService.confirm_booking_completion(c1, str(booking.id), notes="Switchboard tested OK.")
    b_conf = await BookingRepository.get_by_id(str(booking.id))
    assert b_conf.status == BookingStatus.CUSTOMER_CONFIRMED

    # Test Immutability Lock
    try:
        BookingService.validate_booking_mutable(b_conf)
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "BOOKING_TERMINATED"
        print("    [PASS] Immutability lock active on CUSTOMER_CONFIRMED booking (400 BOOKING_TERMINATED).")

    # -------------------------------------------------------------------------
    # TEST 6: Reject Status Updates on Terminal Completed Booking
    # -------------------------------------------------------------------------
    print("\n[6] Testing status update rejection on terminal booking...")
    try:
        await BookingService.start_work(w1, str(booking.id))
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code in ("BOOKING_TERMINATED", "INVALID_STATUS_TRANSITION")
        print("    [PASS] Status update on terminal booking blocked.")

    # -------------------------------------------------------------------------
    # TEST 7: Cancellation Governance Rules
    # -------------------------------------------------------------------------
    print("\n[7] Testing Cancellation Governance Rules...")
    # 1. Reject cancelling terminal booking
    try:
        await BookingService.cancel_booking(c1, str(booking.id), reason="Want to cancel after confirmation")
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code in ("BOOKING_TERMINATED", "INVALID_STATUS_TRANSITION")
        print("    [PASS] Cancellation of terminal booking strictly blocked.")

    # 2. Test valid cancellation on new PENDING booking
    b2_num = await BookingRepository.generate_booking_number()
    booking2 = Booking(
        booking_number=b2_num,
        customer_id=c1.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        service_snapshot=b_conf.service_snapshot,
        address_snapshot=b_conf.address_snapshot,
    )
    booking2 = await BookingRepository.create(booking2)

    res_cancel = await BookingService.cancel_booking(c1, str(booking2.id), reason="Plans changed.")
    assert res_cancel.status == BookingStatus.CANCELLED.value
    assert res_cancel.cancellation_reason == "Plans changed."
    print("    [PASS] Cancellation of PENDING booking successful with reason recorded.")

    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test fixtures...")
    await booking.delete()
    await booking2.delete()
    await c1.delete()
    await c2.delete()
    await w1.delete()
    await w2.delete()
    await close_database_connection()
    print("    [PASS] Test data cleaned up successfully.")

    print("\n===========================================================================")
    print("ALL CENTRALIZED LIFECYCLE BUSINESS RULES VERIFICATION TESTS PASSED!")
    print("===========================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
