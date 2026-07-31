"""
Middleware registration — single function to configure the full stack.

Execution order (outermost → innermost):
    Request  →  RequestLogging → GZip → TrustedHost → CORS → RateLimit → SecurityHeaders → Route
    Response ←  RequestLogging ← GZip ← TrustedHost ← CORS ← RateLimit ← SecurityHeaders ← Route

Why this order:
    - RequestLogging outermost: captures timing/status for ALL responses,
      including rejected hosts and CORS errors.
    - GZip: compresses response bodies before the timer finishes.
    - TrustedHost: rejects spoofed Host headers early.
    - CORS: handles preflight OPTIONS before they hit other middleware.
    - RateLimit: checks rate limits after CORS (preflight shouldn't count).
    - SecurityHeaders innermost: adds headers to actual route responses.

In FastAPI, last-added = first-executed (LIFO), so we add in reverse order.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """
    Register all middleware on the FastAPI app in the correct order.

    Called once from main.py after app creation. This is the single
    place to audit and modify the middleware stack.

    LIFO order: first added = innermost, last added = outermost.
    """

    # 1. SecurityHeaders (innermost — adds headers to route responses)
    #    OWASP-recommended headers: X-Content-Type-Options, X-Frame-Options,
    #    HSTS, CSP, Referrer-Policy, Permissions-Policy.
    app.add_middleware(SecurityHeadersMiddleware)
    logger.debug("Middleware registered: SecurityHeaders")

    # 2. RateLimitMiddleware (placeholder — disabled by default)
    #    Activate by setting RATE_LIMIT_ENABLED=true in .env.
    #    Currently passes all requests through.
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        enabled=settings.RATE_LIMIT_ENABLED,
    )
    logger.debug("Middleware registered: RateLimit (enabled=%s)", settings.RATE_LIMIT_ENABLED)

    # 3. CORS (handles preflight OPTIONS requests)
    #    Configured via ALLOWED_ORIGINS in .env.
    #    Development: ["*"] allows all origins.
    #    Production: restrict to frontend domain(s).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("Middleware registered: CORS (origins=%s)", settings.ALLOWED_ORIGINS)

    # 4. TrustedHost (rejects requests with spoofed Host headers)
    #    Prevents DNS rebinding attacks. In development, ["*"] allows all.
    #    In production, set to your actual domain(s).
    if settings.TRUSTED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS,
        )
        logger.debug("Middleware registered: TrustedHost (hosts=%s)", settings.TRUSTED_HOSTS)

    # 5. GZip (compresses responses above minimum size)
    #    Reduces bandwidth for JSON responses. minimum_size prevents
    #    compressing tiny responses where overhead > savings.
    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.GZIP_MINIMUM_SIZE,
    )
    logger.debug("Middleware registered: GZip (min_size=%d bytes)", settings.GZIP_MINIMUM_SIZE)

    # 6. RequestLogging (outermost — captures everything)
    #    Generates request_id, logs method/path/status/duration,
    #    adds X-Request-ID response header.
    app.add_middleware(RequestLoggingMiddleware)
    logger.debug("Middleware registered: RequestLogging")

    logger.info("Middleware stack configured (%d layers)", 6)
