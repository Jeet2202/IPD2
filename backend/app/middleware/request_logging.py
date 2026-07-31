"""
Request logging middleware.

Responsibilities:
    - Generate a unique request_id (UUID4) for every incoming request.
    - Set request_id and user_id in contextvars for the request lifecycle.
    - Log request start (method, path) and completion (status, duration).
    - Add X-Request-ID header to responses for client-side correlation.

The user_id is set to "-" by default. When the auth module is built,
it will set user_id_var after JWT validation — all subsequent log lines
in that request will automatically include the authenticated user's ID.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import request_id_var, user_id_var

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request with timing, status, and request context.

    Log output includes:
        - Request: method, path, client IP
        - Response: status code, duration in milliseconds
        - Context: request_id (auto-generated), user_id (from auth)

    The X-Request-ID response header allows clients and frontend teams
    to reference specific requests in bug reports and support tickets.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate unique request ID — check incoming header first
        # (allows distributed tracing when called by other services)
        request_id = request.headers.get(
            "X-Request-ID", uuid.uuid4().hex[:12]
        )

        # Set context variables for this request's async call chain
        request_id_token = request_id_var.set(request_id)
        user_id_token = user_id_var.set("-")

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "%s %s → %d (%.1fms)",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )

            # Add request ID to response for client-side correlation
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "%s %s → 500 (%.1fms) UNHANDLED EXCEPTION",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        finally:
            # Reset context variables
            request_id_var.reset(request_id_token)
            user_id_var.reset(user_id_token)
