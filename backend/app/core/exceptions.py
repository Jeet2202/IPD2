"""
Application exception classes and error response schema.

Architecture:
    - AppException is the base for all application-level errors.
    - Subclasses map to specific HTTP status codes.
    - ErrorResponse is the standard JSON shape for ALL API errors.
    - Feature modules raise these exceptions; exception handlers
      catch them and serialize ErrorResponse to the client.

Usage in feature modules:
    from app.core.exceptions import NotFoundException

    raise NotFoundException(
        message="Worker with ID abc123 not found",
        error_code="WORKER_NOT_FOUND",
    )

Error code convention:
    - Use UPPER_SNAKE_CASE
    - Prefix with feature name: WORKER_NOT_FOUND, JOB_ALREADY_ASSIGNED
    - Generic codes for infrastructure: VALIDATION_ERROR, DATABASE_ERROR
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Standard Error Response Schema
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """
    Standard JSON error response returned by all exception handlers.

    Every error from this API — validation, auth, database, or unhandled —
    uses this exact shape. Frontend clients check 'success' and display
    'message'. 'request_id' links to server logs for debugging.
    """

    success: bool = False
    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g., VALIDATION_ERROR)",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        ...,
        description="Human-readable error description safe for display",
        examples=["Invalid input data"],
    )
    details: list = Field(
        default_factory=list,
        description="Additional error context (field errors, debug info)",
    )
    request_id: str = Field(
        default="-",
        description="Request ID for log correlation",
    )


# ---------------------------------------------------------------------------
# Base Application Exception
# ---------------------------------------------------------------------------

class AppException(Exception):
    """
    Base exception for all application-level errors.

    All feature modules should raise subclasses of this, never raw
    HTTPException or generic Python exceptions. The exception handlers
    in exception_handlers.py catch this and serialize ErrorResponse.

    Args:
        message: Human-readable error description (safe for production).
        error_code: Machine-readable code (UPPER_SNAKE_CASE).
        status_code: HTTP status code (set by subclasses, not callers).
        details: Optional list of extra context (field errors, etc.).
    """

    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str = "APP_ERROR",
        status_code: int = 500,
        details: list | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


# ---------------------------------------------------------------------------
# HTTP-Mapped Exception Subclasses
# ---------------------------------------------------------------------------

class BadRequestException(AppException):
    """400 — Client sent invalid or malformed data."""

    def __init__(
        self,
        message: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 400, details)


class UnauthorizedException(AppException):
    """401 — Missing or invalid authentication credentials."""

    def __init__(
        self,
        message: str = "Authentication required",
        error_code: str = "UNAUTHORIZED",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 401, details)


class ForbiddenException(AppException):
    """403 — Authenticated but not authorized for this action."""

    def __init__(
        self,
        message: str = "Access denied",
        error_code: str = "FORBIDDEN",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 403, details)


class NotFoundException(AppException):
    """404 — Requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 404, details)


class ConflictException(AppException):
    """409 — Action conflicts with current resource state."""

    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 409, details)


class RateLimitException(AppException):
    """429 — Too many requests from this client."""

    def __init__(
        self,
        message: str = "Too many requests",
        error_code: str = "RATE_LIMITED",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 429, details)


class DatabaseException(AppException):
    """500 — Database operation failed (wraps Motor/Beanie errors)."""

    def __init__(
        self,
        message: str = "Database operation failed",
        error_code: str = "DATABASE_ERROR",
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, 500, details)
