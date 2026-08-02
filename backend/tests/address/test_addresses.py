"""
Automated live tests for Address Management (Phase 4.3.1).
Requires the uvicorn dev server to be running on port 8000.
Uses direct DB access to bypass email verification (dev environment only).

Usage:
    python tests/address/test_addresses.py
"""

import asyncio
import os
import random
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000/api/v1")
PASS = "TestPass123!"

VALID_ADDRESS = {
    "label": "Home",
    "full_name": "Rajesh Kumar",
    "phone": "+919876543210",
    "address_line_1": "Flat 4B, Sunrise Apartments, MG Road",
    "address_line_2": "Andheri West",
    "landmark": "Near Metro Station",
    "city": "Mumbai",
    "state": "Maharashtra",
    "country": "India",
    "postal_code": "400058",
    "latitude": 19.1136,
    "longitude": 72.8697,
}

VALID_ADDRESS_2 = {
    "label": "Office",
    "full_name": "Rajesh Kumar",
    "phone": "+919876543210",
    "address_line_1": "Unit 12, Tech Park, Powai",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400076",
}

PASS_COUNT = 0
FAIL_COUNT = 0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ok(label: str) -> None:
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  [PASS] {label}")


def fail(label: str, detail: str = "") -> None:
    global FAIL_COUNT
    FAIL_COUNT += 1
    print(f"  [FAIL] {label}: {detail}")


def check(cond: bool, label: str, detail: str = "") -> None:
    ok(label) if cond else fail(label, detail)


async def safe_request(
    method: str,
    url: str,
    *,
    headers: dict,
    json: dict | None = None,
    retry: bool = True,
) -> httpx.Response:
    """
    Make an HTTP request, retrying with a fresh client on ReadError.

    DELETE responses on uvicorn dev server (Windows) may cause connection
    pool corruption. A fresh client recovers cleanly.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as c:
        try:
            return await c.request(method, url, headers=headers, json=json)
        except httpx.ReadError:
            if retry:
                # Retry with brand-new connection
                async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as c2:
                    return await c2.request(method, url, headers=headers, json=json)
            raise


async def _verify_phone_in_db(phone: str) -> None:
    """Directly mark phone's user as email-verified in MongoDB (dev only). DB must be connected."""
    from app.auth.models import User
    user = await User.find_one(User.phone == phone)
    if user:
        user.is_email_verified = True
        await user.save()


async def create_test_user(client: httpx.AsyncClient, role: str = "customer") -> tuple[str, str]:
    """Register a fresh test user, verify email, and return (phone, token)."""
    suffix = random.randint(10000000, 99999999)
    phone = f"+9193{suffix}"
    email = f"addr_test_{suffix}@kaamtest.com"

    r = await client.post("/auth/register", json={
        "phone": phone,
        "email": email,
        "password": PASS,
        "first_name": "Addr",
        "last_name": "Tester",
        "role": role,
    })
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Registration failed for {phone}: {r.text[:300]}")

    await _verify_phone_in_db(phone)

    r = await client.post("/auth/login", json={"phone": phone, "password": PASS})
    if r.status_code != 200:
        raise RuntimeError(f"Login failed for {phone}: {r.text[:300]}")
    resp_data = r.json()
    # Login response: {data: {tokens: {access_token: ...}}}
    token = (
        resp_data.get("access_token")
        or (resp_data.get("data") or {}).get("access_token")
        or ((resp_data.get("data") or {}).get("tokens") or {}).get("access_token")
    )
    if not token:
        raise RuntimeError(f"No token in login response: {resp_data}")
    return phone, token


# ---------------------------------------------------------------------------
# Test Suites
# ---------------------------------------------------------------------------


async def test_address_crud(token: str, client: httpx.AsyncClient) -> str:
    print("\n[SUITE] CRUD Tests")
    h = {"Authorization": f"Bearer {token}"}

    # Create first address -> auto-default
    r = await client.post("/customer/addresses", json=VALID_ADDRESS, headers=h)
    check(r.status_code == 201, "Create address -> 201", r.text[:200])
    if r.status_code != 201:
        return ""
    d = r.json()
    check(d["is_default"] is True, "First address auto-set as default")
    check(d["label"] == "Home", "Label = Home")
    check(d["city"] == "Mumbai", "City persisted")
    check(d["postal_code"] == "400058", "Postal code persisted")
    check(d["latitude"] == 19.1136, "Latitude persisted")
    addr_id = d["id"]

    # Get single
    r = await client.get(f"/customer/addresses/{addr_id}", headers=h)
    check(r.status_code == 200, "Get single address -> 200")
    check(r.json()["id"] == addr_id, "Correct address returned")

    # List
    r = await client.get("/customer/addresses", headers=h)
    check(r.status_code == 200, "List addresses -> 200")
    check(r.json()["total"] >= 1, "At least 1 address in list")
    check("addresses" in r.json(), "Response has 'addresses' key")

    # Update (partial)
    r = await client.put(
        f"/customer/addresses/{addr_id}",
        json={"city": "Pune", "landmark": "Near Shivaji Nagar"},
        headers=h,
    )
    check(r.status_code == 200, "Update address -> 200")
    check(r.json()["city"] == "Pune", "City updated to Pune")
    check(r.json()["landmark"] == "Near Shivaji Nagar", "Landmark updated")

    return addr_id


async def test_default_logic(token: str, client: httpx.AsyncClient) -> tuple[str, str]:
    print("\n[SUITE] Default Logic Tests")
    h = {"Authorization": f"Bearer {token}"}

    r = await client.post("/customer/addresses", json=VALID_ADDRESS_2, headers=h)
    check(r.status_code == 201, "Create second address -> 201", r.text[:200])
    if r.status_code != 201:
        return "", ""
    addr2 = r.json()
    check(addr2["is_default"] is False, "Second address NOT auto-default")
    addr2_id = addr2["id"]

    r = await client.get("/customer/addresses", headers=h)
    addresses = r.json()["addresses"]
    defaults = [a for a in addresses if a["is_default"]]
    check(len(defaults) == 1, "Exactly 1 default after second address created")

    r = await client.patch(f"/customer/addresses/{addr2_id}/default", headers=h)
    check(r.status_code == 200, "PATCH /default -> 200")
    check(r.json()["is_default"] is True, "addr2 is now default")

    r = await client.get("/customer/addresses", headers=h)
    addresses = r.json()["addresses"]
    defaults = [a for a in addresses if a["is_default"]]
    check(len(defaults) == 1, "Still exactly 1 default after switching")
    check(defaults[0]["id"] == addr2_id, "addr2 is the new default")

    # Idempotent call
    r = await client.patch(f"/customer/addresses/{addr2_id}/default", headers=h)
    check(r.status_code == 200, "Idempotent set default -> 200")

    addr1_id = next((a["id"] for a in addresses if a["id"] != addr2_id), "")
    return addr1_id, addr2_id


async def test_soft_delete_and_auto_promote(
    token: str,
    client: httpx.AsyncClient,
    addr1_id: str,
    addr2_id: str,
) -> None:
    print("\n[SUITE] Soft-Delete & Auto-Promote Tests")
    h = {"Authorization": f"Bearer {token}"}

    # addr2 is default — delete it (use safe_request to isolate from pool corruption)
    r = await safe_request("DELETE", f"/customer/addresses/{addr2_id}", headers=h)
    check(r.status_code == 200, "Delete default address -> 200")

    # addr2 -> 404
    r = await safe_request("GET", f"/customer/addresses/{addr2_id}", headers=h)
    check(r.status_code == 404, "Deleted address returns 404")

    # addr1 auto-promoted
    if addr1_id:
        r = await safe_request("GET", f"/customer/addresses/{addr1_id}", headers=h)
        check(r.status_code == 200, "addr1 still accessible")
        check(r.json()["is_default"] is True, "addr1 auto-promoted to default")
        await safe_request("DELETE", f"/customer/addresses/{addr1_id}", headers=h)


async def test_security(
    token1: str,
    token2: str,
    worker_token: str | None,
    client: httpx.AsyncClient,
) -> None:
    print("\n[SUITE] Security Tests")
    h1 = {"Authorization": f"Bearer {token1}"}
    h2 = {"Authorization": f"Bearer {token2}"}

    r = await client.post("/customer/addresses", json=VALID_ADDRESS, headers=h1)
    check(r.status_code == 201, "Customer 1 creates address -> 201", r.text[:200])
    if r.status_code != 201:
        return
    addr_id = r.json()["id"]

    r = await client.get(f"/customer/addresses/{addr_id}", headers=h2)
    check(r.status_code == 403, "Customer 2 reading customer 1 address -> 403")

    r = await client.put(
        f"/customer/addresses/{addr_id}", json={"city": "Delhi"}, headers=h2
    )
    check(r.status_code == 403, "Customer 2 updating customer 1 address -> 403")

    r = await client.delete(f"/customer/addresses/{addr_id}", headers=h2)
    check(r.status_code == 403, "Customer 2 deleting customer 1 address -> 403")

    r = await client.patch(f"/customer/addresses/{addr_id}/default", headers=h2)
    check(r.status_code == 403, "Customer 2 set-default on customer 1 address -> 403")

    if worker_token:
        wh = {"Authorization": f"Bearer {worker_token}"}
        r = await client.get("/customer/addresses", headers=wh)
        check(r.status_code == 403, "Worker accessing customer addresses -> 403")

    r = await client.get("/customer/addresses")
    check(r.status_code == 401, "Unauthenticated list -> 401")

    await safe_request("DELETE", f"/customer/addresses/{addr_id}", headers=h1)


async def test_validation(token: str, client: httpx.AsyncClient) -> None:
    print("\n[SUITE] Validation Tests")
    h = {"Authorization": f"Bearer {token}"}

    bad = {**VALID_ADDRESS, "phone": "9876543210"}  # no +91
    r = await client.post("/customer/addresses", json=bad, headers=h)
    check(r.status_code == 422, "Invalid phone (no +91) -> 422")

    bad = {**VALID_ADDRESS, "postal_code": "12345"}  # 5 digits
    r = await client.post("/customer/addresses", json=bad, headers=h)
    check(r.status_code == 422, "Invalid postal code (5 digits) -> 422")

    bad = {k: v for k, v in VALID_ADDRESS.items() if k != "longitude"}
    r = await client.post("/customer/addresses", json=bad, headers=h)
    check(r.status_code == 422, "lat without lng -> 422")

    bad = {k: v for k, v in VALID_ADDRESS.items() if k != "address_line_1"}
    r = await client.post("/customer/addresses", json=bad, headers=h)
    check(r.status_code == 422, "Missing address_line_1 -> 422")

    bad = {**VALID_ADDRESS, "address_line_1": "AB"}  # min_length=5
    r = await client.post("/customer/addresses", json=bad, headers=h)
    check(r.status_code == 422, "address_line_1 too short -> 422")


# ---------------------------------------------------------------------------
# Main Runner
# ---------------------------------------------------------------------------


async def run_tests() -> None:
    print("=" * 60)
    print("  KaamSetu - Address Management Tests (Phase 4.3.1)")
    print("=" * 60)
    print(f"  Base URL: {BASE_URL}")
    print()

    # Connect DB once for the whole test run (for email verification bypass)
    from app.address.models import Address
    from app.auth.models import AuthAuditLog, RefreshToken, User
    from app.category.models import Service, ServiceCategory
    from app.customer.models import CustomerProfile
    from app.database import close_database_connection, connect_to_database
    from app.otp.models import OTP
    from app.worker.models import WorkerProfile

    await connect_to_database(
        document_models=[
            User, RefreshToken, CustomerProfile, WorkerProfile,
            OTP, AuthAuditLog, ServiceCategory, Service, Address,
        ]
    )

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        print("  [SETUP] Creating isolated test users via registration...")
        try:
            _, token1 = await create_test_user(client, "customer")
            _, token2 = await create_test_user(client, "customer")
            _, worker_token = await create_test_user(client, "worker")
            print("  [SETUP] Test users created and verified OK")
        except RuntimeError as e:
            print(f"  [ERROR] Setup failed: {e}")
            await close_database_connection()
            sys.exit(1)

        addr_id = await test_address_crud(token1, client)

        if addr_id:
            addr1_id, addr2_id = await test_default_logic(token1, client)
            if addr1_id and addr2_id:
                await test_soft_delete_and_auto_promote(token1, client, addr1_id, addr2_id)

        await test_security(token1, token2, worker_token, client)
        await test_validation(token1, client)

    await close_database_connection()

    print("\n" + "=" * 60)
    print(f"  Results: {PASS_COUNT} passed, {FAIL_COUNT} failed")
    if FAIL_COUNT == 0:
        print("  ALL ADDRESS MANAGEMENT TESTS PASSED")
    else:
        print("  SOME TESTS FAILED - review output above")
    print("=" * 60)

    if FAIL_COUNT > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_tests())
