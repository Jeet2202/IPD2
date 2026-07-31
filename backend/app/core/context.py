"""
Request-scoped context variables.

Uses Python's contextvars module to carry per-request state through
the async call chain. Unlike threading.local(), contextvars work
correctly with asyncio — each coroutine gets its own copy.

These are set by the request logging middleware and read by the
logging filter to inject request_id/user_id into every log line.

Usage in any module:
    from app.core.context import request_id_var, user_id_var

    current_request_id = request_id_var.get()  # Returns "-" if not in a request
"""

from contextvars import ContextVar

# Unique ID per HTTP request — set by RequestLoggingMiddleware.
# Default "-" when logging outside a request context (startup, shutdown, tasks).
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# Authenticated user ID — placeholder for the auth module.
# Set to the user's ID after JWT validation in the auth dependency.
# Default "-" for unauthenticated requests.
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")
