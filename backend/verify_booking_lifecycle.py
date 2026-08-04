"""
Ally — Phase 4.7.1: Booking Lifecycle Foundation Automated Verification

Verifies:
1. Valid sequential status transitions by assigned worker.
2. Prevention of skipped transitions (e.g. ASSIGNED -> IN_PROGRESS).
3. Prevention of retrograde transitions (e.g. ARRIVED -> WORKER_EN_ROUTE).
4. Prevention of status updates on cancelled or completed bookings.
5. Unauthorized worker update prevention (403 UNAUTHORIZED_WORKER).
6. Customer update prevention on worker status endpoint (403 WORKER_ROLE_REQUIRED).
7. Status inspection endpoint GET /bookings/{id}/status.
"""

import asyncio, secrets
from datetime import date, datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, PydanticObjectId

from app.core.config import settings
from app.auth.models import User
from app.utils.enums import UserRole, BookingStatus, BookingType, QuotationStatus, ApplicationStatus
from app.booking.models import Booking, AddressSnapshot, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.booking.service import BookingService
from app.booking.schemas import UpdateBookingStatusRequest
from app.application.models import JobApplication
from app.quotation.models import Quotation
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException


from app.database import connect_to_database, close_database_connection


async def main():
    print("===========================================================================")
    print("ALLY — BOOKING LIFECYCLE FOUNDATION (PHASE 4.7.1) VERIFICATION")
    print("===========================================================================\n")

    await connect_to_database(document_models=[User, Booking, JobApplication, Quotation])

    print("[0] Initializing database & creating test fixtures...")
    ts = secrets.token_hex(4)

    # 1. Create Customer
    cust = User(
        email=f"lc_cust_{ts}@kaamtest.com",
        phone=f"+9199{ts[:8]}",
        full_name="Lifecycle Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await cust.save()

    # 2. Create Assigned Worker (Worker 1)
    w1 = User(
        email=f"lc_w1_{ts}@kaamtest.com",
        phone=f"+9198{ts[:8]}",
        full_name="Assigned Worker One",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w1.save()

    # 3. Create Unassigned Worker (Worker 2)
    w2 = User(
        email=f"lc_w2_{ts}@kaamtest.com",
        phone=f"+9197{ts[:8]}",
        full_name="Other Worker Two",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w2.save()

    # 4. Create Booking
    b_num = await BookingRepository.generate_booking_number()
    booking = Booking(
        booking_number=b_num,
        customer_id=cust.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.PENDING,
        service_snapshot=ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="Electrical Repair",
            category_id=str(PydanticObjectId()),
            category_slug="electrician",
            base_market_price=500.0,
            estimated_duration_minutes=60,
        ),
        address_snapshot=AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Lifecycle Customer",
            phone=cust.phone,
            address_line_1="123 Test St",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
        ),
    )
    booking = await BookingRepository.create(booking)
    print(f"    [PASS] Test Booking created: {booking.booking_number} (ID: {booking.id})")

    # -------------------------------------------------------------------------
    # TEST 1: Status Inspection (PENDING)
    # -------------------------------------------------------------------------
    print("\n[1] Testing GET /bookings/{id}/status for Customer...")
    status_res = await BookingService.get_booking_status(cust, str(booking.id))
    assert status_res.current_status == BookingStatus.PENDING.value
    assert BookingStatus.ASSIGNED.value in status_res.next_allowed_statuses
    assert BookingStatus.CANCELLED.value in status_res.next_allowed_statuses
    print("    [PASS] Status inspection returned correct current & next allowed statuses.")

    # -------------------------------------------------------------------------
    # TEST 2: Assign Worker & Transition PENDING -> ASSIGNED
    # -------------------------------------------------------------------------
    print("\n[2] Assigning Worker 1 to booking...")
    booking.worker_id = w1.id
    booking.status = BookingStatus.ASSIGNED
    booking.assigned_at = datetime.now(timezone.utc)
    await booking.save()
    print(f"    [PASS] Booking status set to ASSIGNED (Worker ID: {w1.id})")

    # -------------------------------------------------------------------------
    # TEST 3: Reject Unauthorized Worker Update (Worker 2 -> 403)
    # -------------------------------------------------------------------------
    print("\n[3] Testing unauthorized status update attempt by Worker 2...")
    try:
        await BookingService.update_booking_status_by_worker(
            worker_user=w2,
            booking_id=str(booking.id),
            new_status=BookingStatus.WORKER_EN_ROUTE,
        )
        assert False, "Should have raised ForbiddenException"
    except ForbiddenException as e:
        assert e.error_code == "UNAUTHORIZED_WORKER"
        print("    [PASS] Unauthorized worker update correctly blocked with 403 UNAUTHORIZED_WORKER.")

    # -------------------------------------------------------------------------
    # TEST 4: Reject Customer Updating Worker Execution Status (403)
    # -------------------------------------------------------------------------
    print("\n[4] Testing Customer status update attempt on worker endpoint...")
    try:
        await BookingService.update_booking_status_by_worker(
            worker_user=cust,
            booking_id=str(booking.id),
            new_status=BookingStatus.WORKER_EN_ROUTE,
        )
        assert False, "Should have raised ForbiddenException"
    except ForbiddenException as e:
        assert e.error_code == "WORKER_ROLE_REQUIRED"
        print("    [PASS] Customer status update correctly blocked with 403 WORKER_ROLE_REQUIRED.")

    # -------------------------------------------------------------------------
    # TEST 5: Reject Status Skipping (ASSIGNED -> IN_PROGRESS)
    # -------------------------------------------------------------------------
    print("\n[5] Testing status skipping rejection (ASSIGNED -> IN_PROGRESS)...")
    try:
        await BookingService.update_booking_status_by_worker(
            worker_user=w1,
            booking_id=str(booking.id),
            new_status=BookingStatus.IN_PROGRESS,
        )
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "INVALID_STATUS_TRANSITION"
        print("    [PASS] Status skipping correctly blocked with 400 INVALID_STATUS_TRANSITION.")

    # -------------------------------------------------------------------------
    # TEST 6: Valid Step-by-Step Transition Sequence
    # ASSIGNED -> WORKER_EN_ROUTE -> ARRIVED -> IN_PROGRESS -> WORK_COMPLETED -> CUSTOMER_CONFIRMED
    # -------------------------------------------------------------------------
    print("\n[6] Testing valid sequential transitions...")

    # Step 6a: ASSIGNED -> WORKER_EN_ROUTE
    res_en_route = await BookingService.update_booking_status_by_worker(
        worker_user=w1,
        booking_id=str(booking.id),
        new_status=BookingStatus.WORKER_EN_ROUTE,
    )
    assert res_en_route.status == BookingStatus.WORKER_EN_ROUTE.value
    print("    [PASS] ASSIGNED -> WORKER_EN_ROUTE verified.")

    # Step 6b: WORKER_EN_ROUTE -> ARRIVED
    res_arrived = await BookingService.update_booking_status_by_worker(
        worker_user=w1,
        booking_id=str(booking.id),
        new_status=BookingStatus.ARRIVED,
    )
    assert res_arrived.status == BookingStatus.ARRIVED.value
    print("    [PASS] WORKER_EN_ROUTE -> ARRIVED verified.")

    # Step 6c: Reject Retrograde (ARRIVED -> WORKER_EN_ROUTE)
    try:
        await BookingService.update_booking_status_by_worker(
            worker_user=w1,
            booking_id=str(booking.id),
            new_status=BookingStatus.WORKER_EN_ROUTE,
        )
        assert False, "Should have raised BadRequestException for retrograde"
    except BadRequestException as e:
        assert e.error_code == "INVALID_STATUS_TRANSITION"
        print("    [PASS] Retrograde transition (ARRIVED -> WORKER_EN_ROUTE) correctly blocked.")

    # Step 6d: ARRIVED -> IN_PROGRESS
    res_in_progress = await BookingService.update_booking_status_by_worker(
        worker_user=w1,
        booking_id=str(booking.id),
        new_status=BookingStatus.IN_PROGRESS,
    )
    assert res_in_progress.status == BookingStatus.IN_PROGRESS.value
    assert res_in_progress.started_at is not None
    print("    [PASS] ARRIVED -> IN_PROGRESS verified with started_at timestamp.")

    # Step 6e: IN_PROGRESS -> WORK_COMPLETED
    res_completed = await BookingService.update_booking_status_by_worker(
        worker_user=w1,
        booking_id=str(booking.id),
        new_status=BookingStatus.WORK_COMPLETED,
    )
    assert res_completed.status == BookingStatus.WORK_COMPLETED.value
    assert res_completed.completed_at is not None
    print("    [PASS] IN_PROGRESS -> WORK_COMPLETED verified with completed_at timestamp.")

    # Step 6f: WORK_COMPLETED -> CUSTOMER_CONFIRMED
    res_confirmed = await BookingService.update_booking_status_by_worker(
        worker_user=w1,
        booking_id=str(booking.id),
        new_status=BookingStatus.CUSTOMER_CONFIRMED,
    )
    assert res_confirmed.status == BookingStatus.CUSTOMER_CONFIRMED.value
    print("    [PASS] WORK_COMPLETED -> CUSTOMER_CONFIRMED verified.")

    # -------------------------------------------------------------------------
    # TEST 7: Reject Updating Terminal / Completed Booking
    # -------------------------------------------------------------------------
    print("\n[7] Testing update attempt on terminal completed booking...")
    try:
        await BookingService.update_booking_status_by_worker(
            worker_user=w1,
            booking_id=str(booking.id),
            new_status=BookingStatus.IN_PROGRESS,
        )
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code in ("BOOKING_TERMINATED", "INVALID_STATUS_TRANSITION")
        print("    [PASS] Update attempt on completed booking correctly blocked.")

    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test fixtures...")
    await booking.delete()
    await cust.delete()
    await w1.delete()
    await w2.delete()
    print("    [PASS] Test data cleaned up successfully.")

    await close_database_connection()
    print("\n===========================================================================")
    print("ALL BOOKING LIFECYCLE FOUNDATION VERIFICATION TESTS PASSED!")
    print("===========================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
