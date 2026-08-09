"""
Rate limiting middleware — placeholder.

This middleware defines the interface for request rate limiting.
Currently passes all requests through. When implemented, it will
use Redis or an in-memory store to track request counts per client.

Implementation options (for future):
    - Redis-backed: Use Redis INCR + EXPIRE for distributed rate limiting.
      Required when running multiple app instances behind a load balancer.
    - In-memory: Use a dict with TTL for single-instance deployments.
      Simpler but doesn't share state across processes.

Rate limit strategy:
    - Per-IP for unauthenticated requests.
    - Per-user-ID for authenticated requests (after auth module).
    - Different limits per endpoint group (e.g., auth endpoints
      get stricter limits to prevent brute-force attacks).
"""

import logging
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Sliding window request log: client_key -> list of timestamp floats
_request_history: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory sliding window rate limiting middleware.

    Enforces:
        - Stricter limits (15 requests/min) on sensitive auth/OTP routes (/auth/login, /auth/register, /auth/otp/*).
        - Standard limit (60 requests/min default) on all other API endpoints.
        - Returns HTTP 429 Too Many Requests with Retry-After header when exceeded.
    """

    def __init__(
        self,
        app: object,
        requests_per_minute: int = 60,
        enabled: bool = True,
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.enabled = enabled

    def _get_client_key(self, request: Request) -> str:
        """Derive client identifier from X-Forwarded-For or client.host."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        elif request.client:
            ip = request.client.host
        else:
            ip = "127.0.0.1"
        return f"{ip}:{request.url.path}"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self.enabled:
            return await call_next(request)

        path = request.url.path
        now = time.time()
        window_seconds = 60.0

        # Define limit based on path sensitivity
        if any(sensitive in path for sensitive in ["/auth/login", "/auth/register", "/auth/otp"]):
            limit = 15
        else:
            limit = self.requests_per_minute

        client_key = self._get_client_key(request)
        history = _request_history[client_key]

        # Prune timestamps older than window_seconds
        cutoff = now - window_seconds
        _request_history[client_key] = [t for t in history if t > cutoff]
        valid_history = _request_history[client_key]

        if len(valid_history) >= limit:
            retry_after = int(window_seconds - (now - valid_history[0])) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": None,
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(retry_after),
                },
            )

        valid_history.append(now)
        response = await call_next(request)
        remaining = max(0, limit - len(valid_history))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
