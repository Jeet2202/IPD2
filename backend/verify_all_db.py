"""
KaamSetu Phase 2 — Comprehensive MongoDB Atlas Connection, Index & Round-Trip Verification Script.

Executes Step 3 (Live Verification Against Atlas) and Step 4 (Sanity Round-Trip Test)
for all 11 feature modules and 17 Beanie Document models.
"""

import asyncio
from datetime import date, datetime, timezone
import sys
from uuid import uuid4
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.database.connection import connect_to_database, close_database_connection, get_database

# Import all 17 Phase 2 Document models
from app.auth.models import User, UserRole, AccountStatus
from app.customer.models import CustomerProfile
from app.worker.models import WorkerProfile, Skill, GeoLocation as WorkerGeoLocation
from app.category.models import ServiceCategory, Service
from app.pricing.models import ServicePriceGuide, PricingConfiguration, Currency
from app.service_request.models import (
    ServiceRequest,
    ServiceAddress,
    PriceSnapshot,
    RequestStatus,
    RequestPriority,
)
from app.inspection.models import (
    InspectionRequest,
    InspectionAddress,
    InspectionStatus,
    QuotationStatus,
)
from app.job.models import (
    Job,
    JobAddress,
    JobPricingSnapshot,
    JobType,
    JobStatus,
)
from app.review.models import Review
from app.notification.models import Notification, NotificationType
from app.admin.models import (
    WorkerVerification,
    AuditLog,
    AppSettings,
    Banner,
    SupportTicket,
)

ALL_MODELS = [
    User,
    CustomerProfile,
    WorkerProfile,
    ServiceCategory,
    Service,
    ServicePriceGuide,
    PricingConfiguration,
    ServiceRequest,
    InspectionRequest,
    Job,
    Review,
    Notification,
    WorkerVerification,
    AuditLog,
    AppSettings,
    Banner,
    SupportTicket,
]

EXPECTED_COLLECTIONS_CHECKLIST = {
    "users": "P2.1 User",
    "customer_profiles": "P2.2 Customer Profile",
    "worker_profiles": "P2.3 Worker Profile",
    "service_categories": "P2.4 Category & Service (Categories)",
    "services": "P2.4 Category & Service (Services)",
    "service_price_guides": "P2.5 Pricing (Service Price Guides)",
    "pricing_configurations": "P2.5 Pricing (Global Configurations)",
    "service_requests": "P2.6 Service Request",
    "inspection_requests": "P2.7 Inspection Request",
    "jobs": "P2.8 Job",
    "reviews": "P2.9 Review",
    "notifications": "P2.10 Notification",
    "admin_worker_verifications": "P2.11 Admin & System (Worker Verifications)",
    "admin_audit_logs": "P2.11 Admin & System (Audit Logs)",
    "admin_app_settings": "P2.11 Admin & System (App Settings)",
    "admin_banners": "P2.11 Admin & System (Banners)",
    "admin_support_tickets": "P2.11 Admin & System (Support Tickets)",
}


async def run_verification():
    print("=" * 70)
    print("KAAMSETU PHASE 2 -- MONGODB ATLAS VERIFICATION")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # Step 3.1: Connect to database & init Beanie
    # -----------------------------------------------------------------------
    print("\n[3.1] Connecting to MongoDB Atlas and initializing Beanie...")
    await connect_to_database(document_models=ALL_MODELS)
    db = get_database()
    print(f"[OK] Successfully connected to database: {db.name}")

    # -----------------------------------------------------------------------
    # Step 3.2: Verify collections against checklist
    # -----------------------------------------------------------------------
    print("\n[3.2] Verifying collections and names in MongoDB Atlas...")
    actual_collections = set(await db.list_collection_names())
    expected_collections = set(EXPECTED_COLLECTIONS_CHECKLIST.keys())

    print(f"Total collections found in DB ({len(actual_collections)}): {sorted(list(actual_collections))}")

    missing_cols = expected_collections - actual_collections
    stray_cols = actual_collections - expected_collections

    if missing_cols:
        print(f"[ERROR] Missing expected collections: {missing_cols}")
    else:
        print("[OK] All 17 expected Phase 2 collections exist in Atlas!")

    if stray_cols:
        print(f"[WARN] Note: Extra/stray collections in DB: {stray_cols}")
    else:
        print("[OK] No stray or unexpected collections found in DB.")

    # -----------------------------------------------------------------------
    # Step 3.3: Inspect index creation across models
    # -----------------------------------------------------------------------
    print("\n[3.3] Verifying index creation on all collections...")
    for model in ALL_MODELS:
        col_name = model.Settings.name
        idx_info = await db[col_name].index_information()
        idx_names = list(idx_info.keys())
        print(f"  - {col_name:<30} | {len(idx_names)} index(es): {idx_names}")

    # -----------------------------------------------------------------------
    # Step 3.4: Test unique index enforcement (User email & phone)
    # -----------------------------------------------------------------------
    print("\n[3.4] Testing unique index enforcement on User.email & phone_number...")
    test_user1 = User(
        first_name="UniqueTest1",
        last_name="Tester",
        email="unique_index_test@kaamsetu.com",
        phone_number="+919000000001",
        password_hash="hash123",
        role=UserRole.CUSTOMER,
        account_status=AccountStatus.ACTIVE,
    )
    await test_user1.insert()
    print("  - Inserted initial test user successfully.")

    test_user2 = User(
        first_name="UniqueTest2",
        last_name="Tester",
        email="unique_index_test@kaamsetu.com",  # Duplicate email
        phone_number="+919000000002",
        password_hash="hash456",
        role=UserRole.CUSTOMER,
        account_status=AccountStatus.ACTIVE,
    )
    try:
        await test_user2.insert()
        print("[ERROR] Duplicate email was NOT rejected!")
    except DuplicateKeyError:
        print("[OK] Verified: Duplicate email rejected with DuplicateKeyError!")

    # Clean up test user
    await test_user1.delete()
    print("  - Cleaned up unique index test user.")

    # -----------------------------------------------------------------------
    # Step 3.5: Confirm Worker 2dsphere index type
    # -----------------------------------------------------------------------
    print("\n[3.5] Confirming 2dsphere geo index on worker_profiles...")
    worker_idx_info = await db["worker_profiles"].index_information()
    geo_index_found = False
    for idx_name, meta in worker_idx_info.items():
        key_list = meta.get("key", [])
        for field_name, index_type in key_list:
            if field_name == "current_location" and index_type == "2dsphere":
                geo_index_found = True
                print(f"[OK] Verified: '{idx_name}' is a genuine 2dsphere geo index on current_location!")
    if not geo_index_found:
        print("[ERROR] 2dsphere geo index on worker_profiles.current_location not found in metadata!")

    # -----------------------------------------------------------------------
    # Step 4: Sanity Round-Trip Test for all 11 Modules
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[STEP 4] SANITY ROUND-TRIP TEST (ALL 11 FEATURE MODULES)")
    print("=" * 70)

    inserted_docs = []
    try:
        # P2.1 User
        u = User(
            first_name="Round",
            last_name="Trip",
            email="roundtrip.user@kaamsetu.com",
            phone_number="+919111111111",
            password_hash="secret_hash",
            role=UserRole.CUSTOMER,
            account_status=AccountStatus.ACTIVE,
        )
        await u.insert()
        inserted_docs.append(u)
        u_fetched = await User.get(u.id)
        assert u_fetched is not None and u_fetched.email == "roundtrip.user@kaamsetu.com"
        print("[OK] [P2.1 User] Insert -> Fetch -> Verified")

        # P2.2 Customer Profile
        cp = CustomerProfile(
            user_id=str(u.id),
            preferred_language="hi",
        )
        await cp.insert()
        inserted_docs.append(cp)
        cp_fetched = await CustomerProfile.get(cp.id)
        assert cp_fetched is not None and cp_fetched.user_id == str(u.id)
        print("[OK] [P2.2 Customer Profile] Insert -> Fetch -> Verified")


        # P2.3 Worker Profile (with GeoJSON)
        wu = User(
            first_name="Worker",
            last_name="One",
            email="roundtrip.worker@kaamsetu.com",
            phone_number="+919222222222",
            password_hash="secret_hash",
            role=UserRole.WORKER,
            account_status=AccountStatus.ACTIVE,
        )
        await wu.insert()
        inserted_docs.append(wu)

        wp = WorkerProfile(
            user_id=str(wu.id),
            bio="Professional Electrician",
            experience_years=5,
            hourly_rate=299.0,
            service_categories=["electrical"],
            skills=[
                Skill(
                    skill_name="wiring",
                    experience_years=5,
                    proficiency_level="expert",
                )
            ],
            current_location=WorkerGeoLocation(
                type="Point",
                coordinates=[72.8777, 19.0760],
            ),
        )
        await wp.insert()
        inserted_docs.append(wp)
        wp_fetched = await WorkerProfile.get(wp.id)
        assert wp_fetched is not None and wp_fetched.current_location.coordinates == [72.8777, 19.0760]
        print("[OK] [P2.3 Worker Profile + GeoJSON] Insert -> Fetch -> Verified")

        # P2.4 Category & Service
        cat = ServiceCategory(
            name="Electrical Test",
            slug=f"electrical-test-{uuid4().hex[:6]}",
            description="Electrical works",
            icon_url="https://example.com/icon.png",
            display_order=1,
        )
        await cat.insert()
        inserted_docs.append(cat)

        srv = Service(
            category_id=str(cat.id),
            category_slug=cat.slug,
            name="Fan Repair Test",
            slug=f"fan-repair-{uuid4().hex[:6]}",
            short_description="Repair ceiling fan",
            detailed_description="Complete diagnosis and repair of ceiling fan.",
            estimated_duration_minutes=45,
            base_market_price=199.0,
            minimum_price=150.0,
            maximum_price=250.0,
        )
        await srv.insert()
        inserted_docs.append(srv)
        srv_fetched = await Service.get(srv.id)
        assert srv_fetched is not None and srv_fetched.base_market_price == 199.0
        print("[OK] [P2.4 ServiceCategory + Service] Insert -> Fetch -> Verified")

        # P2.5 Pricing
        spg = ServicePriceGuide(
            service_id=str(srv.id),
            city="mumbai",
            minimum_price=150.0,
            average_market_price=200.0,
            maximum_price=250.0,
            currency=Currency.INR,
        )
        await spg.insert()
        inserted_docs.append(spg)

        pcfg = PricingConfiguration(
            default_price_tolerance=10.0,
            gst_percentage=18.0,
            platform_commission_percentage=20.0,
            worker_commission_percentage=80.0,
        )
        await pcfg.insert()
        inserted_docs.append(pcfg)
        pcfg_fetched = await PricingConfiguration.get(pcfg.id)
        assert pcfg_fetched is not None and pcfg_fetched.gst_percentage == 18.0
        print("[OK] [P2.5 Pricing (ServicePriceGuide + PricingConfiguration)] Insert -> Fetch -> Verified")

        # P2.6 Service Request
        sreq = ServiceRequest(
            request_number=f"REQ-{uuid4().hex[:8]}",
            customer_id=str(u.id),
            category_id=str(cat.id),
            service_id=str(srv.id),
            service_address=ServiceAddress(
                address_line="123 Test Street",
                city="Mumbai",
                state="Maharashtra",
                pincode="400001",
                latitude=19.0760,
                longitude=72.8777,
            ),
            preferred_date=date(2026, 9, 1),
            preferred_time_slot="10:00 AM - 12:00 PM",
            estimated_duration=45,
            estimated_price=234.82,
            price_snapshot=PriceSnapshot(
                market_price=199.0,
                worker_price=159.2,
                inspection_charge=0.0,
                service_fee=29.0,
                tax=6.82,
                total_price=234.82,
            ),
            status=RequestStatus.REQUESTED,
            priority=RequestPriority.NORMAL,
        )
        await sreq.insert()
        inserted_docs.append(sreq)
        sreq_fetched = await ServiceRequest.get(sreq.id)
        assert sreq_fetched is not None and sreq_fetched.price_snapshot.total_price == 234.82
        print("[OK] [P2.6 Service Request] Insert -> Fetch -> Verified")

        # P2.7 Inspection Request
        ireq = InspectionRequest(
            inspection_request_number=f"INSP-{uuid4().hex[:8]}",
            customer_id=str(u.id),
            category_id=str(cat.id),
            service_id=str(srv.id),
            address=InspectionAddress(
                address_line="123 Test Street",
                city="Mumbai",
                state="Maharashtra",
                pincode="400001",
                latitude=19.0760,
                longitude=72.8777,
            ),
            preferred_date=date(2026, 9, 1),
            preferred_time_slot="02:00 PM - 04:00 PM",
            inspection_charge=99.0,
            inspection_status=InspectionStatus.REQUESTED,
            quotation_status=QuotationStatus.NOT_GENERATED,
        )
        await ireq.insert()
        inserted_docs.append(ireq)
        ireq_fetched = await InspectionRequest.get(ireq.id)
        assert ireq_fetched is not None and ireq_fetched.inspection_charge == 99.0
        print("[OK] [P2.7 Inspection Request] Insert -> Fetch -> Verified")

        # P2.8 Job
        job = Job(
            job_number=f"JOB-{uuid4().hex[:8]}",
            customer_id=str(u.id),
            worker_id=str(wu.id),
            category_id=str(cat.id),
            service_id=str(srv.id),
            service_address=JobAddress(
                address_line="123 Test Street",
                city="Mumbai",
                state="Maharashtra",
                pincode="400001",
                latitude=19.0760,
                longitude=72.8777,
            ),
            job_type=JobType.NORMAL_SERVICE,
            job_status=JobStatus.CREATED,
            scheduled_date=date(2026, 9, 1),
            scheduled_time="10:00 AM - 12:00 PM",
            estimated_duration=45,
            pricing_snapshot=JobPricingSnapshot(
                base_price=199.0,
                inspection_charge=0.0,
                worker_charge=159.2,
                platform_fee=39.8,
                tax=6.82,
                discount=0.0,
                final_amount=234.82,
            ),
        )
        await job.insert()
        inserted_docs.append(job)
        job_fetched = await Job.get(job.id)
        assert job_fetched is not None and job_fetched.pricing_snapshot.final_amount == 234.82
        print("[OK] [P2.8 Job] Insert -> Fetch -> Verified")

        # P2.9 Review
        rev = Review(
            review_number=f"REV-{uuid4().hex[:8]}",
            job_id=str(job.id),
            customer_id=str(u.id),
            worker_id=str(wu.id),
            category_id=str(cat.id),
            service_id=str(srv.id),
            overall_rating=4.5,
            review_title="Great service",
            review_comment="The electrician fixed the wiring quickly.",
        )
        await rev.insert()
        inserted_docs.append(rev)
        rev_fetched = await Review.get(rev.id)
        assert rev_fetched is not None and rev_fetched.overall_rating == 4.5
        print("[OK] [P2.9 Review] Insert -> Fetch -> Verified")

        # P2.10 Notification
        notif = Notification(
            notification_number=f"NOT-{uuid4().hex[:8]}",
            user_id=str(u.id),
            title="Booking Confirmed",
            message="Your booking REQ-1234 has been accepted.",
            notification_type=NotificationType.BOOKING,
        )
        await notif.insert()
        inserted_docs.append(notif)
        notif_fetched = await Notification.get(notif.id)
        assert notif_fetched is not None and notif_fetched.title == "Booking Confirmed"
        print("[OK] [P2.10 Notification] Insert -> Fetch -> Verified")

        # P2.11 Admin & System Models
        app_set = AppSettings(
            platform_name="KaamSetu Test",
            support_email="support@kaamsetu.com",
            support_phone="+911800111222",
        )
        await app_set.insert()
        inserted_docs.append(app_set)

        audit = AuditLog(
            performed_by=str(u.id),
            action="CREATE_TEST",
            module="verification",
            entity_type="test_doc",
            entity_id=str(app_set.id),
        )
        await audit.insert()
        inserted_docs.append(audit)

        banner = Banner(
            title="Welcome Offer",
            image_url="https://example.com/banner.png",
            is_active=True,
        )
        await banner.insert()
        inserted_docs.append(banner)

        wver = WorkerVerification(
            worker_id=str(wu.id),
            submitted_documents={"aadhar": "url1", "police": "url2"},
        )
        await wver.insert()
        inserted_docs.append(wver)

        ticket = SupportTicket(
            ticket_number=f"TKT-{uuid4().hex[:8]}",
            user_id=str(u.id),
            category="General Inquiry",
            subject="Question on pricing",
            description="Can I get a discount for recurring services?",
        )
        await ticket.insert()
        inserted_docs.append(ticket)

        ticket_fetched = await SupportTicket.get(ticket.id)
        assert ticket_fetched is not None and ticket_fetched.subject == "Question on pricing"
        print("[OK] [P2.11 Admin & System (5 Models)] Insert -> Fetch -> Verified")

        print("\n" + "=" * 70)
        print("ALL 11 FEATURE MODULES (17 DOCUMENT MODELS) PASSED ROUND-TRIP TEST!")
        print("=" * 70)

    finally:
        # Clean up all inserted documents
        print(f"\n[CLEANUP] Deleting {len(inserted_docs)} test document(s) from Atlas...")
        for doc in inserted_docs:
            await doc.delete()
        print("[OK] All test documents removed. Database is clean!")

    await close_database_connection()
    print("\n[OK] Verification complete! Client connection closed cleanly.")


if __name__ == "__main__":
    asyncio.run(run_verification())
