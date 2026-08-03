"""
FastAPI application entry point.

Startup sequence:
    1. Logging — configured before anything else logs.
    2. App creation — FastAPI instance with OpenAPI metadata.
    3. Exception handlers — centralized error handling.
    4. Middleware — security, CORS, compression, logging.
    5. Routes — infrastructure (/, /health) + versioned API (/api/v1).
    6. Lifespan — database connect on startup, disconnect on shutdown.

ASGI entry point: `uvicorn app.main:app`
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exception_handlers import register_exception_handlers
from app.database import (
    connect_to_database,
    close_database_connection,
    check_database_health,
)
from app.middleware import register_middleware
from app.api.v1.router import v1_router
from app.api.tags import OPENAPI_TAGS

# ---------------------------------------------------------------------------
# 1. Logging — BEFORE anything else logs
# ---------------------------------------------------------------------------
setup_logging(
    log_level=settings.LOG_LEVEL,
    json_logs=settings.LOG_JSON_FORMAT,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 2. Lifespan — database lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Async lifespan handler — runs on startup and shutdown.

    Startup: Connects to MongoDB with pool config and initializes Beanie.
    Shutdown: Closes the MongoDB connection pool gracefully.

    Document models will be registered here as features are built:
        await connect_to_database(document_models=[User, Service, Booking])
    """
    # --- Startup ---
    logger.info(
        "Starting %s v%s [%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT.value,
    )
    from app.address.models import Address
    from app.application.models import JobApplication
    from app.auth.models import AuthAuditLog, RefreshToken, User
    from app.booking.models import Booking
    from app.category.models import Service, ServiceCategory
    from app.customer.models import CustomerProfile
    from app.otp.models import OTP
    from app.worker.models import WorkerProfile

    await connect_to_database(
        document_models=[
            User,
            RefreshToken,
            CustomerProfile,
            WorkerProfile,
            OTP,
            AuthAuditLog,
            ServiceCategory,
            Service,
            Address,
            Booking,
            JobApplication,
        ]
    )
    yield
    # --- Shutdown ---
    await close_database_connection()
    logger.info("%s shut down.", settings.APP_NAME)


# ---------------------------------------------------------------------------
# 3. App Creation — with OpenAPI metadata
# ---------------------------------------------------------------------------

API_DESCRIPTION = """
## Blue-Collar Service Marketplace API

Production-ready REST API for connecting customers with skilled
blue-collar workers (electricians, plumbers, painters, etc.).

### API Versioning
All business endpoints are under `/api/v1/`. Infrastructure
endpoints (`/health`, `/`) are at the root.

### Authentication
Most endpoints require a JWT Bearer token in the Authorization header.
Obtain tokens via the `/api/v1/auth/login` endpoint.

### Rate Limiting
API requests are rate-limited per client. Check the `X-RateLimit-*`
response headers for your current quota.
"""

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=API_DESCRIPTION,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_tags=OPENAPI_TAGS,
    license_info={
        "name": "Proprietary",
    },
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# 4. Exception Handlers
# ---------------------------------------------------------------------------
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# 5. Middleware Stack
# ---------------------------------------------------------------------------
register_middleware(app)

# ---------------------------------------------------------------------------
# 6. Routes
# ---------------------------------------------------------------------------

# --- Infrastructure (unversioned) ---


@app.get(
    "/",
    tags=["System"],
    summary="API root",
    response_description="Basic API information and links",
)
async def root() -> dict:
    """
    Root endpoint — returns API name, version, and navigation links.

    Use this to verify the API is running and discover key endpoints.
    Not behind authentication — always accessible.
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "docs": settings.docs_url,
        "health": "/health",
        "api": "/api/v1",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    response_description="Service and database status",
)
async def health_check() -> dict:
    """
    Returns service health including database connectivity.

    Used by load balancers, Kubernetes probes, and monitoring dashboards.
    The database field reports pool config and ping status.
    """
    db_health = await check_database_health()

    return {
        "status": "healthy" if db_health.get("status") == "connected" else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "database": db_health,
    }


# --- Versioned API ---
# One line to include all 10 feature modules.
# When v2 is needed: app.include_router(v2_router)
app.include_router(v1_router)
