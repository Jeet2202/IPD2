"""
Verification script for all 3 Booking Types:
1. PREDEFINED_SERVICE / NORMAL_SERVICE
2. CUSTOM_SERVICE
3. INSPECTION_REQUEST
"""

import asyncio
from datetime import date
from beanie import PydanticObjectId, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.address.models import Address
from app.auth.models import User
from app.application.models import JobApplication
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.booking.schemas import CreateBookingRequest
from app.booking.service import BookingService
from app.category.models import Service, ServiceCategory
from app.database import connect_to_database, close_database_connection
from app.utils.enums import BookingType, UserRole


async def run_verification():
    print("===========================================================================")
    print("VERIFYING ALL 3 BOOKING TYPES (PREDEFINED, CUSTOM, INSPECTION)")
    print("===========================================================================")

    await connect_to_database(document_models=[User, Address, ServiceCategory, Service, Booking, JobApplication])

    # 1. Setup Test Customer User
    customer = await User.find_one(User.email == "test_booking_types_cust@kaamsetu.com")
    if not customer:
        customer = User(
            email="test_booking_types_cust@kaamsetu.com",
            password_hash="dummy_password_hash",
            full_name="Test Customer",
            phone="+919999999999",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True,
        )
        await customer.insert()

    address = await Address.find_one(Address.customer_id == customer.id)
    if address:
        await address.delete()
    address = Address(
        customer_id=customer.id,
        label="Home",
        full_name="Test Customer",
        phone="+919999999999",
        address_line_1="123 Test St",
        locality="Andheri East",
        city="Mumbai",
        state="Maharashtra",
        country="India",
        pincode="400001",
        postal_code="400001",
        latitude=19.0760,
        longitude=72.8777,
        location={"type": "Point", "coordinates": [72.8777, 19.0760]},
        service_location={"type": "Point", "coordinates": [72.8777, 19.0760]},
        is_default=True,
    )
    await address.insert()

    # 3. Setup Test Category & Service
    category = await ServiceCategory.find_one(ServiceCategory.slug == "electrical")
    if not category:
        category = ServiceCategory(
            name="Electrical",
            slug="electrical",
            description="Electrical Services",
            is_active=True,
        )
        await category.insert()

    service = await Service.find_one(Service.slug == "fan-repair")
    if not service:
        service = Service(
            name="Fan Repair",
            slug="fan-repair",
            category_id=str(category.id),
            category_slug=category.slug,
            description="Fix fan speed or noise issues",
            base_market_price=299.0,
            estimated_duration_minutes=30,
            is_active=True,
        )
        await service.insert()

    # ---------------------------------------------------------------------------
    # Test 1: PREDEFINED_SERVICE / NORMAL_SERVICE
    # ---------------------------------------------------------------------------
    print("\n[1] Testing PREDEFINED_SERVICE / NORMAL_SERVICE creation...")
    req1 = CreateBookingRequest(
        service_id=str(service.id),
        address_id=str(address.id),
        booking_type=BookingType.NORMAL_SERVICE,
        scheduled_date=date.today(),
        scheduled_time="10:00 - 12:00",
        customer_notes="Please call before arrival",
    )
    res1 = await BookingService.create_booking(str(customer.id), req1)
    assert res1.booking_type == "normal_service"
    assert res1.service_snapshot.name == "Fan Repair"
    print(f"    [PASS] Predefined Booking created: {res1.booking_number} (ID: {res1.id})")

    # ---------------------------------------------------------------------------
    # Test 2: CUSTOM_SERVICE
    # ---------------------------------------------------------------------------
    print("\n[2] Testing CUSTOM_SERVICE creation...")
    req2 = CreateBookingRequest(
        address_id=str(address.id),
        booking_type=BookingType.CUSTOM_SERVICE,
        category_slug="electrical",
        custom_title="Rewire Bedroom Outlet & Install Chandelier",
        custom_description="Need complete wiring check and heavy light fitting.",
        urgency="urgent",
        scheduled_date=date.today(),
        scheduled_time="14:00 - 16:00",
    )
    res2 = await BookingService.create_booking(str(customer.id), req2)
    assert res2.booking_type == "custom_service"
    assert res2.custom_title == "Rewire Bedroom Outlet & Install Chandelier"
    print(f"    [PASS] Custom Service Booking created: {res2.booking_number} (ID: {res2.id})")

    # ---------------------------------------------------------------------------
    # Test 3: INSPECTION_REQUEST
    # ---------------------------------------------------------------------------
    print("\n[3] Testing INSPECTION_REQUEST creation...")
    req3 = CreateBookingRequest(
        address_id=str(address.id),
        booking_type=BookingType.INSPECTION_REQUEST,
        category_slug="plumbing",
        type_of_work="Water Leakage",
        problem_description="Water seeping through kitchen ceiling tile.",
        inspection_charge=99.0,
        scheduled_date=date.today(),
        scheduled_time="16:00 - 18:00",
    )
    res3 = await BookingService.create_booking(str(customer.id), req3)
    assert res3.booking_type == "inspection_request"
    assert res3.problem_description == "Water seeping through kitchen ceiling tile."
    print(f"    [PASS] Inspection Request Booking created: {res3.booking_number} (ID: {res3.id})")

    # Clean up test bookings
    await Booking.find(Booking.customer_id == customer.id).delete()
    print("\n===========================================================================")
    print("ALL 3 BOOKING TYPES CREATED AND VERIFIED SUCCESSFULLY WITH 0 ERRORS!")
    print("===========================================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
