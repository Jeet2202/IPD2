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
from app.application.router import router as application_router
from app.auth.router import router as auth_router
from app.booking.router import router as booking_router
from app.category.router import router as category_router
from app.customer.router import router as customer_router
from app.engagement.router import router as engagement_router
from app.fraud.router import router as fraud_router
from app.home.router import router as home_router
from app.inspection.router import router as inspection_router
from app.jobs.router import router as jobs_router
from app.marketplace.router import router as marketplace_router
from app.moderation.router import (
    disputes_router,
    moderation_router,
    reports_router,
)
from app.notifications.router import router as notifications_router
from app.pricing.router import router as pricing_router
from app.privacy.router import router as privacy_router
from app.quotation.router import router as quotation_router
from app.referral.router import router as referral_router
from app.review.router import router as review_domain_router
from app.reviews.router import router as reviews_router
from app.security_center.router import router as security_router
from app.service.router import router as service_router
from app.support.router import router as support_router
from app.trust.router import router as trust_router
from app.trust_intelligence.router import router as trust_intelligence_router
from app.uploads.router import router as uploads_router
from app.verification.router import router as verification_router
from app.worker.router import router as worker_router
from app.payments.router import router as payments_router

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

# --- Addresses ---
# IMPORTANT: Must be registered BEFORE quotation_router at /customer prefix.
# The quotation router has a GET /{quotation_id} catch-all that would shadow
# /customer/addresses if registered first.
v1_router.include_router(
    address_router,
    prefix="/customer",
    tags=["Addresses"],
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

# --- Bookings ---
# Service booking creation, listing, and retrieval.
# Requires authenticated customer role.
v1_router.include_router(
    booking_router,
    prefix="/customer",
    tags=["Bookings"],
)
v1_router.include_router(
    booking_router,
    prefix="",
    tags=["Bookings"],
    include_in_schema=False,
)

# --- Worker Marketplace & Applications ---
# Marketplace booking discovery for workers and job application submission.
# Requires authenticated worker role.
v1_router.include_router(
    marketplace_router,
    prefix="/worker/marketplace",
    tags=["Worker Marketplace"],
)
v1_router.include_router(
    application_router,
    prefix="/worker/applications",
    tags=["Worker Applications"],
)
v1_router.include_router(
    quotation_router,
    prefix="",
    tags=["Quotations"],
)
v1_router.include_router(
    quotation_router,
    prefix="/worker/quotations",
    tags=["Quotations"],
    include_in_schema=False,
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
    review_domain_router,
    prefix="",
    tags=["Ratings & Reviews"],
)
v1_router.include_router(
    reviews_router,
    prefix="/reviews",
    tags=["Reviews"],
)

# --- Trust & Safety ---
# Core trust, risk assessment, policy configuration, and audit logging.
v1_router.include_router(
    trust_router,
    prefix="/trust",
    tags=["Trust & Safety"],
)

# --- Worker Verification ---
# Worker document upload, verification workflow, admin review, and trust badges.
v1_router.include_router(
    verification_router,
    prefix="/verification",
    tags=["Worker Verification"],
)

# --- Fraud Detection & Abuse Prevention ---
# Rule-based fraud detection, risk assessment, alert management, and abuse reporting.
v1_router.include_router(
    fraud_router,
    prefix="/fraud",
    tags=["Fraud Detection & Abuse Prevention"],
)

# --- Reporting, Moderation & Dispute Resolution ---
# User reports, evidence files, moderation reviews, escalations, and formal dispute cases.
v1_router.include_router(
    reports_router,
)
v1_router.include_router(
    moderation_router,
)
v1_router.include_router(
    disputes_router,
)

# --- Privacy & Compliance ---
# User privacy controls, consent management, JSON/CSV exports, grace period deletion, retention rules.
v1_router.include_router(
    privacy_router,
    prefix="/privacy",
    tags=["Privacy & Compliance"],
)

# --- Security Monitoring & Audit Center ---
# Centralized security event logs, auth monitoring, API health, security alerts, and dashboard summaries.
v1_router.include_router(
    security_router,
    prefix="/security",
    tags=["Security Monitoring & Audit Center"],
)

# --- Trust Intelligence & Risk Assessment ---
# Centralized trust intelligence, department risk scoring, trend analytics, and metric recommendations.
v1_router.include_router(
    trust_intelligence_router,
    prefix="/trust/intelligence",
    tags=["Trust Intelligence & Risk Assessment"],
)

# --- Customer Engagement ---
# Favorites, Recently Viewed, Saved Searches, Personalization & Home Feed.
v1_router.include_router(
    engagement_router,
    prefix="/engagement",
    tags=["Customer Engagement"],
)

# --- Referrals & Rewards ---
# Referral code management, friend invitations, tracking, reward points ledger, and achievement badges.
v1_router.include_router(
    referral_router,
    prefix="",
    tags=["Referrals & Rewards"],
)

# --- Help Center & Customer Support ---
# FAQs, Knowledge Base articles, support tickets, feedback, SOS, and React Admin support management.
v1_router.include_router(
    support_router,
    prefix="",
    tags=["Help Center & Customer Support"],
)

# --- Admin ---
# Platform administration, user management, analytics.
# Requires authenticated admin role.
v1_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"],
)

# --- Real-Time Sockets ---
# Socket.IO infrastructure health and connection status
from app.api.v1.endpoints.sockets import router as sockets_router
v1_router.include_router(
    sockets_router,
    prefix="/sockets",
    tags=["Real-Time"],
)

# --- Payments (Razorpay) ---
# Order creation, payment verification, webhook, refunds.
v1_router.include_router(
    payments_router,
    prefix="/payments",
    tags=["Payments"],
)
