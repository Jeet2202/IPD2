"""
Ally — Booking Module Tests (Phase 4.4.1)

Follows exactly the same pattern as test_addresses.py:
    - first_name / last_name for registration
    - phone-based login
    - direct DB email-verification bypass
    - httpx.AsyncClient with full base_url
"""

import asyncio
import random
import sys
from datetime import datetime, timezone

import httpx

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 20.0
PASS = "Test@1234!"

_pass_count = 0
_fail_count = 0


def check(label: str, condition: bool, reason: str = "") -> bool:
    global _pass_count, _fail_count
    if condition:
        _pass_count += 1
        return True
    else:
        _fail_count += 1
        print(f"  [FAIL] {label}: {reason}")
        return False


def suite(name: str) -> None:
    print(f"\n[SUITE] {name}")


# ──────────────────────────────────────────────────────────────────────────────
# DB bypass (same as test_addresses.py)
# ──────────────────────────────────────────────────────────────────────────────

async def _verify_phone_in_db(phone: str) -> None:
    from app.auth.models import User
    user = await User.find_one(User.phone == phone)
    if user:
        user.is_email_verified = True
        await user.save()


async def _init_beanie() -> None:
    from app.address.models import Address
    from app.auth.models import AuthAuditLog, RefreshToken, User
    from app.booking.models import Booking
    from app.category.models import Service, ServiceCategory
    from app.customer.models import CustomerProfile
    from app.otp.models import OTP
    from app.worker.models import WorkerProfile
    from app.database import connect_to_database
    await connect_to_database(document_models=[
        User, RefreshToken, CustomerProfile, WorkerProfile,
        OTP, AuthAuditLog, ServiceCategory, Service, Address, Booking,
    ])


# ──────────────────────────────────────────────────────────────────────────────
# User factory
# ──────────────────────────────────────────────────────────────────────────────

async def create_test_user(
    client: httpx.AsyncClient,
    role: str = "customer",
    suffix: str | None = None,
) -> tuple[str, str]:
    """Register, verify, and login. Returns (phone, token)."""
    s = suffix or str(random.randint(10000000, 99999999))
    phone = f"+9193{s}"

    r = await client.post(f"{BASE_URL}/auth/register", json={
        "phone": phone,
        "email": f"bk_test_{s}@kaamtest.com",
        "password": PASS,
        "first_name": "Booking",
        "last_name": f"Tester{role.capitalize()}",
        "role": role,
    }, timeout=TIMEOUT)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Register failed [{role}]: {r.text[:300]}")

    await _verify_phone_in_db(phone)

    r2 = await client.post(f"{BASE_URL}/auth/login", json={
        "phone": phone, "password": PASS
    }, timeout=TIMEOUT)
    if r2.status_code != 200:
        raise RuntimeError(f"Login failed [{role}]: {r2.text[:300]}")

    body = r2.json()
    token = (
        body.get("access_token")
        or (body.get("data") or {}).get("access_token")
        or ((body.get("data") or {}).get("tokens") or {}).get("access_token")
    )
    if not token:
        raise RuntimeError(f"No token in login response: {body}")
    return phone, token


def H(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ──────────────────────────────────────────────────────────────────────────────
# Run Tests
# ──────────────────────────────────────────────────────────────────────────────

async def run_tests():
    print("=" * 60)
    print("  Ally - Booking Module Tests (Phase 4.4.1)")
    print("=" * 60)
    print(f"  Base URL: {BASE_URL}")

    await _init_beanie()

    async with httpx.AsyncClient() as client:

        # ── Health check ──────────────────────────────────────────────────
        health = await client.get("http://localhost:8000/health", timeout=TIMEOUT)
        assert health.status_code == 200, f"Server not reachable: {health.text}"

        # ── Setup ─────────────────────────────────────────────────────────
        print("\n  [SETUP] Creating isolated test users...")
        _, c1_token = await create_test_user(client, "customer")
        _, c2_token = await create_test_user(client, "customer")
        _, w_token = await create_test_user(client, "worker")

        # Create address for customer 1
        addr_res = await client.post(
            f"{BASE_URL}/customer/addresses",
            json={
                "label": "Home",
                "full_name": "Booking Tester",
                "phone": "+919876543210",
                "address_line_1": "123 Test Street, Andheri",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "postal_code": "400058",
                "latitude": 19.1136,
                "longitude": 72.8697,
            },
            headers=H(c1_token),
            timeout=TIMEOUT,
        )
        assert addr_res.status_code == 201, f"Address create failed: {addr_res.text}"
        addr_data = addr_res.json().get("data") or addr_res.json()
        address_id = addr_data.get("id") or addr_data.get("_id")
        assert address_id, "No address_id in response"

        # Find a live service
        svc_res = await client.get(f"{BASE_URL}/services", timeout=TIMEOUT)
        service_id = None
        if svc_res.status_code == 200:
            body = svc_res.json()
            items = (
                body.get("data") or
                body.get("services") or
                (body.get("data") or {}).get("services") or
                []
            )
            if isinstance(items, dict):
                items = items.get("services", []) or items.get("items", [])
        if not service_id:
            # Seed a test category & service directly in DB for testing
            from app.category.models import Service, ServiceCategory
            cat = await ServiceCategory.find_one(ServiceCategory.slug == "test-cat-booking")
            if not cat:
                cat = ServiceCategory(
                    name="Test Category Booking",
                    slug="test-cat-booking",
                    description="Category for booking test",
                    display_order=1,
                    is_active=True,
                )
                await cat.insert()

            svc = await Service.find_one(Service.slug == "test-service-booking")
            if not svc:
                svc = Service(
                    category_id=str(cat.id),
                    category_slug=cat.slug,
                    name="Fan Repair & Cleaning",
                    slug="test-service-booking",
                    description="Test service description",
                    base_market_price=499.0,
                    minimum_price=299.0,
                    maximum_price=999.0,
                    estimated_duration_minutes=45,
                    is_active=True,
                )
                await svc.insert()
            service_id = str(svc.id)

        print(f"  [SETUP] address_id={address_id}")
        print(f"  [SETUP] service_id={service_id}")
        print("  [SETUP] Setup complete OK\n")

        # ─────────────────────────────────────────────────────────────────
        suite("CRUD Tests")
        # ─────────────────────────────────────────────────────────────────

        booking_id = None
        booking_number = None

        if service_id:
            # 1. Create booking (NORMAL_SERVICE)
            r = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={
                    "service_id": service_id,
                    "address_id": address_id,
                    "booking_type": "normal_service",
                    "scheduled_date": "2026-09-01",
                    "scheduled_time": "10:00-12:00",
                    "customer_notes": "Please call before arriving.",
                },
                headers=H(c1_token),
                timeout=TIMEOUT,
            )
            if check("Create NORMAL_SERVICE booking -> 201", r.status_code == 201, r.text[:300]):
                d = r.json().get("data") or r.json()
                booking_id = d.get("id")
                booking_number = d.get("booking_number")
                check("Booking has id", bool(booking_id))
                check("Booking number format KS...", bool(booking_number and booking_number.startswith("KS")), booking_number or "None")
                check("Booking number ≥ 9 chars", len(booking_number or "") >= 9, booking_number or "")
                check("status = pending", d.get("status") == "pending", d.get("status"))
                check("booking_type = normal_service", d.get("booking_type") == "normal_service", d.get("booking_type"))
                check("service_snapshot present", isinstance(d.get("service_snapshot"), dict))
                check("address_snapshot present", isinstance(d.get("address_snapshot"), dict))
                check("snapshot.city = Mumbai", d.get("address_snapshot", {}).get("city") == "Mumbai")
                check("estimated_price set", d.get("estimated_price") is not None)
                check("estimated_duration_minutes set", d.get("estimated_duration_minutes") is not None)
                check("customer_notes persisted", d.get("customer_notes") == "Please call before arriving.")
                check("latitude in response", d.get("latitude") is not None)
                check("longitude in response", d.get("longitude") is not None)
                check("scheduled_date = 2026-09-01", d.get("scheduled_date") == "2026-09-01", d.get("scheduled_date"))
                check("scheduled_time persisted", d.get("scheduled_time") == "10:00-12:00")
                check("worker_id is None", d.get("worker_id") is None)
                check("payment_id is None", d.get("payment_id") is None)
                check("inspection_id is None", d.get("inspection_id") is None)
                check("quotation_id is None", d.get("quotation_id") is None)
                check("address_snapshot.latitude set", d.get("address_snapshot", {}).get("latitude") is not None)
                check("address_snapshot.longitude set", d.get("address_snapshot", {}).get("longitude") is not None)

            # 2. Create INSPECTION_REQUEST
            r2 = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={
                    "service_id": service_id,
                    "address_id": address_id,
                    "booking_type": "inspection_request",
                    "problem_description": "Inspection visit for switchboard check",
                },
                headers=H(c1_token),
                timeout=TIMEOUT,
            )
            if check("Create INSPECTION_REQUEST -> 201", r2.status_code == 201, r2.text[:200]):
                d2 = r2.json().get("data") or r2.json()
                check("booking_type = inspection_request", d2.get("booking_type") == "inspection_request")
                check("status = pending", d2.get("status") == "pending")

            # 3. Get single booking
            if booking_id:
                get_r = await client.get(
                    f"{BASE_URL}/customer/bookings/{booking_id}",
                    headers=H(c1_token), timeout=TIMEOUT,
                )
                if check("Get booking by ID -> 200", get_r.status_code == 200, get_r.text[:200]):
                    gd = get_r.json().get("data") or get_r.json()
                    check("Returns correct booking id", gd.get("id") == booking_id)
                    check("booking_number present", bool(gd.get("booking_number")))

            # 4. List bookings
            list_r = await client.get(
                f"{BASE_URL}/customer/bookings",
                headers=H(c1_token), timeout=TIMEOUT,
            )
            if check("List bookings -> 200", list_r.status_code == 200, list_r.text[:200]):
                ld = list_r.json().get("data") or list_r.json()
                check("List has 'bookings' key", "bookings" in ld, str(list(ld.keys())))
                check("List has 'total' key", "total" in ld, str(list(ld.keys())))
                check("total >= 2", ld.get("total", 0) >= 2, str(ld.get("total")))

            # 5. Status filter
            sf_r = await client.get(
                f"{BASE_URL}/customer/bookings?status=pending",
                headers=H(c1_token), timeout=TIMEOUT,
            )
            if check("List ?status=pending -> 200", sf_r.status_code == 200, sf_r.text[:200]):
                sfd = sf_r.json().get("data") or sf_r.json()
                all_pending = all(b.get("status") == "pending" for b in sfd.get("bookings", []))
                check("All results status=pending", all_pending)

            # 6. Pagination
            pg_r = await client.get(
                f"{BASE_URL}/customer/bookings?page=1&page_size=1",
                headers=H(c1_token), timeout=TIMEOUT,
            )
            if check("Pagination page_size=1 -> 200", pg_r.status_code == 200, pg_r.text[:200]):
                pgd = pg_r.json().get("data") or pg_r.json()
                check("page_size=1 returns <= 1 result", len(pgd.get("bookings", [])) <= 1)

            # 7. Empty booking history for new customer (c2_token)
            empty_r = await client.get(
                f"{BASE_URL}/customer/bookings",
                headers=H(c2_token), timeout=TIMEOUT,
            )
            if check("New customer empty bookings -> 200", empty_r.status_code == 200, empty_r.text[:200]):
                ed = empty_r.json().get("data") or empty_r.json()
                check("New customer total = 0", ed.get("total") == 0)
                check("New customer bookings is empty list", ed.get("bookings") == [])

        # ─────────────────────────────────────────────────────────────────
        suite("Validation Tests")
        # ─────────────────────────────────────────────────────────────────

        # Invalid service_id (not hex)
        v1 = await client.post(
            f"{BASE_URL}/customer/bookings",
            json={"service_id": "invalid", "address_id": "60d5ec49f1a2c8b1f8e4e1b2"},
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Non-hex service_id -> 422", v1.status_code == 422, f"Got {v1.status_code}")

        # Invalid address_id
        v2 = await client.post(
            f"{BASE_URL}/customer/bookings",
            json={"service_id": "60d5ec49f1a2c8b1f8e4e1a1", "address_id": "bad"},
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Non-hex address_id -> 422", v2.status_code == 422, f"Got {v2.status_code}")

        # Missing required fields
        v3 = await client.post(
            f"{BASE_URL}/customer/bookings",
            json={},
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Empty payload -> 422", v3.status_code == 422, f"Got {v3.status_code}")

        # Non-existent service (valid hex, not in DB)
        v4 = await client.post(
            f"{BASE_URL}/customer/bookings",
            json={"service_id": "aaaaaaaaaaaaaaaaaaaaaaaa", "address_id": address_id},
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Non-existent service -> 404", v4.status_code == 404, f"Got {v4.status_code}: {v4.text[:100]}")

        # Non-existent address (valid hex)
        if service_id:
            v5 = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": "aaaaaaaaaaaaaaaaaaaaaaaa"},
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Non-existent address -> 404", v5.status_code == 404, f"Got {v5.status_code}: {v5.text[:100]}")

            # Past date validation
            v_past = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": address_id, "scheduled_date": "2020-01-01"},
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Past scheduled_date -> 422", v_past.status_code == 422, f"Got {v_past.status_code}")

            # Invalid booking_type validation
            v_type = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": address_id, "booking_type": "invalid_type"},
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Invalid booking_type -> 422", v_type.status_code == 422, f"Got {v_type.status_code}")

            # Soft-deleted address validation
            del_addr_res = await client.post(
                f"{BASE_URL}/customer/addresses",
                json={
                    "label": "Other",
                    "full_name": "Temporary Address",
                    "phone": "+919876543210",
                    "address_line_1": "999 Delete Lane",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400058",
                },
                headers=H(c1_token), timeout=TIMEOUT,
            )
            del_addr_data = del_addr_res.json().get("data") or del_addr_res.json()
            del_addr_id = del_addr_data.get("id") or del_addr_data.get("_id")
            await client.delete(f"{BASE_URL}/customer/addresses/{del_addr_id}", headers=H(c1_token), timeout=TIMEOUT)

            v_del = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": del_addr_id},
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Deleted address -> 404", v_del.status_code == 404, f"Got {v_del.status_code}")

            # Address without GPS coordinates / location validation
            no_loc_res = await client.post(
                f"{BASE_URL}/customer/addresses",
                json={
                    "label": "Office",
                    "full_name": "No GPS Address",
                    "phone": "+919876543210",
                    "address_line_1": "123 Remote Road",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400059",
                },
                headers=H(c1_token), timeout=TIMEOUT,
            )
            no_loc_data = no_loc_res.json().get("data") or no_loc_res.json()
            no_loc_id = no_loc_data.get("id") or no_loc_data.get("_id")
            if no_loc_id:
                v_noloc = await client.post(
                    f"{BASE_URL}/customer/bookings",
                    json={"service_id": service_id, "address_id": no_loc_id},
                    headers=H(c1_token), timeout=TIMEOUT,
                )
                check("Address without location -> 400", v_noloc.status_code == 400, f"Got {v_noloc.status_code}")

        # ─────────────────────────────────────────────────────────────────
        suite("Scheduling Tests")
        # ─────────────────────────────────────────────────────────────────

        # GET /customer/bookings/slots for valid future date
        slots_res = await client.get(
            f"{BASE_URL}/customer/bookings/slots?date=2026-09-01",
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("GET /bookings/slots -> 200", slots_res.status_code == 200, slots_res.text[:200])
        if slots_res.status_code == 200:
            sd = slots_res.json().get("data") or slots_res.json()
            check("Slots response has 'slots' key", "slots" in sd)
            check("Slots response is_date_available = true", sd.get("is_date_available") is True)
            check("Slots list is not empty", len(sd.get("slots", [])) > 0)

        # GET /customer/bookings/slots for date exceeding max advance window (e.g. year 2028)
        far_slots = await client.get(
            f"{BASE_URL}/customer/bookings/slots?date=2028-01-01",
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Far future date -> 200", far_slots.status_code == 200)
        if far_slots.status_code == 200:
            fsd = far_slots.json().get("data") or far_slots.json()
            check("Far future date is_date_available = false", fsd.get("is_date_available") is False)

        # Booking creation with date exceeding max window (60 days)
        if service_id:
            max_win_res = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": address_id, "scheduled_date": "2028-01-01"},
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Max advance window exceeded -> 400", max_win_res.status_code == 400, f"Got {max_win_res.status_code}")

        # Booking creation with past time slot on today
        if service_id:
            today_str = datetime.now().strftime("%Y-%m-%d")
            past_slot_res = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={
                    "service_id": service_id,
                    "address_id": address_id,
                    "scheduled_date": today_str,
                    "scheduled_time": "00:00 - 01:00",
                },
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Past time slot on today -> 400", past_slot_res.status_code == 400, f"Got {past_slot_res.status_code}")

        # ─────────────────────────────────────────────────────────────────
        suite("Inspection Request Tests")
        # ─────────────────────────────────────────────────────────────────

        if service_id:
            # Successful inspection request with problem_description and problem_photos
            insp_res = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={
                    "service_id": service_id,
                    "address_id": address_id,
                    "booking_type": "inspection_request",
                    "problem_description": "AC unit is leaking water heavily into the living room.",
                    "problem_photos": ["https://res.cloudinary.com/demo/image/upload/sample.jpg"],
                    "scheduled_date": "2026-09-02",
                    "scheduled_time": "10:00 - 12:00",
                },
                headers=H(c1_token), timeout=TIMEOUT,
            )
            if check("Create INSPECTION_REQUEST with description -> 201", insp_res.status_code == 201, insp_res.text[:200]):
                id_data = insp_res.json().get("data") or insp_res.json()
                check("booking_type = inspection_request", id_data.get("booking_type") == "inspection_request")
                check("problem_description persisted", id_data.get("problem_description") == "AC unit is leaking water heavily into the living room.")
                check("problem_photos persisted", len(id_data.get("problem_photos", [])) == 1)

            # Missing problem_description on INSPECTION_REQUEST -> 422
            insp_missing = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={
                    "service_id": service_id,
                    "address_id": address_id,
                    "booking_type": "inspection_request",
                    "scheduled_date": "2026-09-02",
                },
                headers=H(c1_token), timeout=TIMEOUT,
            )
            check("Missing problem_description on inspection -> 422", insp_missing.status_code == 422, f"Got {insp_missing.status_code}")

        # ─────────────────────────────────────────────────────────────────
        suite("Authorization & Ownership Tests")
        # ─────────────────────────────────────────────────────────────────

        # Unauthenticated list -> 401
        u1 = await client.get(f"{BASE_URL}/customer/bookings", timeout=TIMEOUT)
        check("Unauthenticated list -> 401", u1.status_code == 401, f"Got {u1.status_code}")

        # Unauthenticated create -> 401
        u2 = await client.post(
            f"{BASE_URL}/customer/bookings",
            json={"service_id": "60d5ec49f1a2c8b1f8e4e1a1", "address_id": address_id},
            timeout=TIMEOUT,
        )
        check("Unauthenticated create -> 401", u2.status_code == 401, f"Got {u2.status_code}")

        # Worker cannot create customer booking -> 403
        if service_id:
            u3 = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": address_id},
                headers=H(w_token), timeout=TIMEOUT,
            )
            check("Worker creates booking -> 403", u3.status_code == 403, f"Got {u3.status_code}")

        # Customer 2 uses Customer 1's address -> 403
        if service_id:
            u4 = await client.post(
                f"{BASE_URL}/customer/bookings",
                json={"service_id": service_id, "address_id": address_id},
                headers=H(c2_token), timeout=TIMEOUT,
            )
            check("C2 booking with C1 address -> 403", u4.status_code == 403, f"Got {u4.status_code}: {u4.text[:100]}")

        # Customer 2 GET Customer 1's booking -> 403
        if booking_id:
            u5 = await client.get(
                f"{BASE_URL}/customer/bookings/{booking_id}",
                headers=H(c2_token), timeout=TIMEOUT,
            )
            check("C2 GET C1 booking -> 403", u5.status_code == 403, f"Got {u5.status_code}")

        # Non-existent booking -> 404
        u6 = await client.get(
            f"{BASE_URL}/customer/bookings/aaaaaaaaaaaaaaaaaaaaaaaa",
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Non-existent booking GET -> 404", u6.status_code == 404, f"Got {u6.status_code}")

        # ─────────────────────────────────────────────────────────────────
        suite("Regression — Address Module")
        # ─────────────────────────────────────────────────────────────────

        reg1 = await client.get(
            f"{BASE_URL}/customer/addresses",
            headers=H(c1_token), timeout=TIMEOUT,
        )
        check("Address list still -> 200", reg1.status_code == 200, f"Got {reg1.status_code}: {reg1.text[:100]}")
        if reg1.status_code == 200:
            ra = reg1.json().get("data") or reg1.json()
            check("Address list has 'addresses' key", "addresses" in ra)
            check("Address list has 'total' key", "total" in ra)

    # ── Results ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Results: {_pass_count} passed, {_fail_count} failed")
    if _fail_count == 0:
        print("  ALL BOOKING MODULE TESTS PASSED")
    else:
        print("  SOME TESTS FAILED — see above")
    print("=" * 60)
    if _fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_tests())
