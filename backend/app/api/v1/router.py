"""
API v1 aggregate router — includes all feature module routers.

Architecture:
    Each feature module (auth, jobs, etc.) has its own APIRouter.
    This file imports all of them and registers them under /api/v1
    with proper URL prefixes and OpenAPI tags.

    main.py includes only this one router:
        app.include_router(v1_router)

Adding a new feature:
    1. Create the feature router in app/{feature}/router.py
    2. Import it here
    3. Add v1_router.include_router(...) with prefix and tags
    4. Add a tag entry in OPENAPI_TAGS (in app/api/tags.py)

URL structure:
    /api/v1/auth/...
    /api/v1/customers/...
    /api/v1/workers/...
    /api/v1/jobs/...
    /api/v1/pricing/...
    /api/v1/inspections/...
    /api/v1/notifications/...
    /api/v1/uploads/...
    /api/v1/reviews/...
    /api/v1/admin/...
"""

from fastapi import APIRouter

# ---------------------------------------------------------------------------
# Feature Router Imports
# ---------------------------------------------------------------------------
from app.address.router import router as address_router
from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.booking.router import router as booking_router
from app.category.router import router as category_router
from app.customer.router import router as customer_router
from app.home.router import router as home_router
from app.inspection.router import router as inspection_router
from app.jobs.router import router as jobs_router
from app.notifications.router import router as notifications_router
from app.pricing.router import router as pricing_router
from app.reviews.router import router as reviews_router
from app.service.router import router as service_router
from app.uploads.router import router as uploads_router
from app.worker.router import router as worker_router

# ---------------------------------------------------------------------------
# V1 Aggregate Router
# ---------------------------------------------------------------------------

v1_router = APIRouter(prefix="/api/v1")

# --- Home, Services & Categories ---
v1_router.include_router(
    home_router,
    prefix="",
    tags=["Home"],
)
v1_router.include_router(
    service_router,
    prefix="",
    tags=["Services"],
)
v1_router.include_router(
    category_router,
    prefix="/categories",
    tags=["Categories"],
)
v1_router.include_router(
    category_router,
    prefix="/category",
    tags=["Categories"],
    include_in_schema=False,
)

# --- Auth ---
# Registration, login, token refresh, OTP verification.
# Public endpoints (no auth required for register/login).
v1_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

# --- Customers ---
# Customer profile management and booking history.
# Requires authenticated customer role.
v1_router.include_router(
    customer_router,
    prefix="/customer",
    tags=["Customers"],
)
v1_router.include_router(
    customer_router,
    prefix="/customers",
    tags=["Customers"],
    include_in_schema=False,
)

# --- Addresses ---
# Customer address management (CRUD + default management).
# Requires authenticated customer role.
v1_router.include_router(
    address_router,
    prefix="/customer",
    tags=["Addresses"],
)

# --- Bookings ---
# Service booking creation, listing, and retrieval.
# Requires authenticated customer role.
v1_router.include_router(
    booking_router,
    prefix="/customer",
    tags=["Bookings"],
)

# --- Workers ---
# Worker profiles, availability, and public worker listing.
# Public listing endpoints + worker-only profile management.
v1_router.include_router(
    worker_router,
    prefix="/worker",
    tags=["Workers"],
)
v1_router.include_router(
    worker_router,
    prefix="/workers",
    tags=["Workers"],
    include_in_schema=False,
)

# --- Jobs ---
# Job creation, listing, acceptance, and lifecycle management.
# Core marketplace transaction flow.
v1_router.include_router(
    jobs_router,
    prefix="/jobs",
    tags=["Jobs"],
)

# --- Pricing ---
# Service pricing catalog. Public read, admin write.
v1_router.include_router(
    pricing_router,
    prefix="/pricing",
    tags=["Pricing"],
)

# --- Inspections ---
# Pre-job and post-job inspection management.
v1_router.include_router(
    inspection_router,
    prefix="/inspections",
    tags=["Inspections"],
)

# --- Notifications ---
# Push/in-app notification management for the current user.
v1_router.include_router(
    notifications_router,
    prefix="/notifications",
    tags=["Notifications"],
)

# --- Uploads ---
# File and image upload handling via Cloudinary.
v1_router.include_router(
    uploads_router,
    prefix="/uploads",
    tags=["Uploads"],
)

# --- Reviews ---
# Worker reviews and ratings from customers.
v1_router.include_router(
    reviews_router,
    prefix="/reviews",
    tags=["Reviews"],
)

# --- Admin ---
# Platform administration, user management, analytics.
# Requires authenticated admin role.
v1_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"],
)
