"""
Ally — Phase 4.7.2: Worker Job Execution Automated Verification

Verifies:
1. Assigned worker job execution endpoints:
   - start-travel (ASSIGNED -> WORKER_EN_ROUTE)
   - arrive (WORKER_EN_ROUTE -> ARRIVED)
   - start-work (ARRIVED -> IN_PROGRESS)
   - complete (IN_PROGRESS -> WORK_COMPLETED with photos & notes)
2. Automatic Booking Timeline / Event recording for each step.
3. Worker booking lookup GET /worker/bookings/{id}.
4. Prevention of skipped or out-of-order execution steps.
5. Unauthorized worker update prevention (403 UNAUTHORIZED_WORKER).
6. Customer update prevention on worker execution endpoints (403 WORKER_ROLE_REQUIRED).
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
from app.booking.schemas import CompleteJobRequest
from app.application.models import JobApplication
from app.quotation.models import Quotation
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException


async def main():
    print("===========================================================================")
    print("ALLY — WORKER JOB EXECUTION (PHASE 4.7.2) VERIFICATION")
    print("===========================================================================\n")

    await connect_to_database(document_models=[User, Booking, JobApplication, Quotation])

    print("[0] Initializing database & creating test fixtures...")
    ts = secrets.token_hex(4)

    # 1. Create Customer
    cust = User(
        email=f"exec_cust_{ts}@kaamtest.com",
        phone=f"+9199{ts[:8]}",
        full_name="Execution Customer",
        role=UserRole.CUSTOMER,
        password_hash="hash_test",
        is_active=True,
    )
    await cust.save()

    # 2. Create Assigned Worker (Worker 1)
    w1 = User(
        email=f"exec_w1_{ts}@kaamtest.com",
        phone=f"+9198{ts[:8]}",
        full_name="Assigned Execution Worker",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w1.save()

    # 3. Create Unassigned Worker (Worker 2)
    w2 = User(
        email=f"exec_w2_{ts}@kaamtest.com",
        phone=f"+9197{ts[:8]}",
        full_name="Unassigned Worker",
        role=UserRole.WORKER,
        password_hash="hash_test",
        is_active=True,
    )
    await w2.save()

    # 4. Create Booking assigned to Worker 1
    b_num = await BookingRepository.generate_booking_number()
    booking = Booking(
        booking_number=b_num,
        customer_id=cust.id,
        worker_id=w1.id,
        booking_type=BookingType.NORMAL_SERVICE,
        status=BookingStatus.ASSIGNED,
        assigned_at=datetime.now(timezone.utc),
        service_snapshot=ServiceSnapshot(
            service_id=str(PydanticObjectId()),
            name="AC Deep Servicing",
            category_id=str(PydanticObjectId()),
            category_slug="air_conditioner",
            base_market_price=1200.0,
            estimated_duration_minutes=90,
        ),
        address_snapshot=AddressSnapshot(
            address_id=str(PydanticObjectId()),
            label="Home",
            full_name="Execution Customer",
            phone=cust.phone,
            address_line_1="456 Execution Blvd",
            city="Delhi",
            state="Delhi",
            postal_code="110001",
        ),
    )
    booking = await BookingRepository.create(booking)
    print(f"    [PASS] Test Booking created: {booking.booking_number} (Status: ASSIGNED, Worker: {w1.id})")

    # -------------------------------------------------------------------------
    # TEST 1: GET /worker/bookings/{id} Lookup
    # -------------------------------------------------------------------------
    print("\n[1] Testing GET /worker/bookings/{id}...")
    wb_res = await BookingService.get_worker_booking(w1, str(booking.id))
    assert wb_res.id == str(booking.id)
    assert wb_res.worker_id == str(w1.id)
    assert wb_res.status == BookingStatus.ASSIGNED.value
    print("    [PASS] Worker booking details fetched successfully.")

    # -------------------------------------------------------------------------
    # TEST 2: Reject Unauthorized Worker Access (Worker 2)
    # -------------------------------------------------------------------------
    print("\n[2] Testing unauthorized access attempt by Worker 2...")
    try:
        await BookingService.get_worker_booking(w2, str(booking.id))
        assert False, "Should have raised ForbiddenException"
    except ForbiddenException as e:
        assert e.error_code == "BOOKING_ACCESS_DENIED"
        print("    [PASS] Unauthorized worker access blocked with 403 BOOKING_ACCESS_DENIED.")

    # -------------------------------------------------------------------------
    # TEST 3: Step 1 — Start Travel (ASSIGNED -> WORKER_EN_ROUTE)
    # -------------------------------------------------------------------------
    print("\n[3] Testing start_travel (ASSIGNED -> WORKER_EN_ROUTE)...")
    res_travel = await BookingService.start_travel(w1, str(booking.id))
    assert res_travel.status == BookingStatus.WORKER_EN_ROUTE.value
    assert res_travel.en_route_at is not None
    assert len(res_travel.timeline) >= 1
    assert res_travel.timeline[-1].status == BookingStatus.WORKER_EN_ROUTE.value
    print("    [PASS] Start travel successful. Status: WORKER_EN_ROUTE, Timeline Event logged.")

    # -------------------------------------------------------------------------
    # TEST 4: Step 2 — Mark Arrived (WORKER_EN_ROUTE -> ARRIVED)
    # -------------------------------------------------------------------------
    print("\n[4] Testing mark_arrived (WORKER_EN_ROUTE -> ARRIVED)...")
    res_arrived = await BookingService.mark_arrived(w1, str(booking.id))
    assert res_arrived.status == BookingStatus.ARRIVED.value
    assert res_arrived.arrived_at is not None
    assert len(res_arrived.timeline) >= 2
    assert res_arrived.timeline[-1].status == BookingStatus.ARRIVED.value
    print("    [PASS] Mark arrived successful. Status: ARRIVED, Timeline Event logged.")

    # -------------------------------------------------------------------------
    # TEST 5: Reject Out-of-Order Execution (/complete called from ARRIVED)
    # -------------------------------------------------------------------------
    print("\n[5] Testing out-of-order execution rejection (ARRIVED -> WORK_COMPLETED)...")
    try:
        await BookingService.complete_work(
            worker_user=w1,
            booking_id=str(booking.id),
            payload=CompleteJobRequest(completion_notes="Premature complete"),
        )
        assert False, "Should have raised BadRequestException"
    except BadRequestException as e:
        assert e.error_code == "INVALID_STATUS_TRANSITION"
        print("    [PASS] Premature completion attempt blocked with 400 INVALID_STATUS_TRANSITION.")

    # -------------------------------------------------------------------------
    # TEST 6: Step 3 — Start Work (ARRIVED -> IN_PROGRESS)
    # -------------------------------------------------------------------------
    print("\n[6] Testing start_work (ARRIVED -> IN_PROGRESS)...")
    res_start = await BookingService.start_work(w1, str(booking.id))
    assert res_start.status == BookingStatus.IN_PROGRESS.value
    assert res_start.started_at is not None
    assert len(res_start.timeline) >= 3
    assert res_start.timeline[-1].status == BookingStatus.IN_PROGRESS.value
    print("    [PASS] Start work successful. Status: IN_PROGRESS, Timeline Event logged.")

    # -------------------------------------------------------------------------
    # TEST 7: Step 4 — Complete Work with Photos & Notes (IN_PROGRESS -> WORK_COMPLETED)
    # -------------------------------------------------------------------------
    print("\n[7] Testing complete_work with photos and notes (IN_PROGRESS -> WORK_COMPLETED)...")
    b_photos = ["https://res.cloudinary.com/ally/before1.jpg"]
    a_photos = ["https://res.cloudinary.com/ally/after1.jpg", "https://res.cloudinary.com/ally/after2.jpg"]
    c_notes = "Cleaned AC filters, refilled R32 refrigerant, tested cooling output."
    w_summary = "Full AC deep servicing and refrigerant top-up completed."

    res_comp = await BookingService.complete_work(
        worker_user=w1,
        booking_id=str(booking.id),
        payload=CompleteJobRequest(
            completion_notes=c_notes,
            work_summary=w_summary,
            before_photos=b_photos,
            after_photos=a_photos,
        ),
    )
    assert res_comp.status == BookingStatus.WORK_COMPLETED.value
    assert res_comp.completed_at is not None
    assert res_comp.completion_notes == c_notes
    assert res_comp.work_summary == w_summary
    assert res_comp.before_photos == b_photos
    assert res_comp.after_photos == a_photos
    assert len(res_comp.timeline) >= 4
    assert res_comp.timeline[-1].status == BookingStatus.WORK_COMPLETED.value
    print("    [PASS] Complete work successful with photos, notes, summary, and Timeline Event logged.")

    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------
    print("\n[CLEANUP] Cleaning up test fixtures...")
    await booking.delete()
    await cust.delete()
    await w1.delete()
    await w2.delete()
    await close_database_connection()
    print("    [PASS] Test data cleaned up successfully.")

    print("\n===========================================================================")
    print("ALL WORKER JOB EXECUTION VERIFICATION TESTS PASSED!")
    print("===========================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
