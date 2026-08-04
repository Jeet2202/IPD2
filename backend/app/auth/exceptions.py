"""
Authentication and Authorization Exceptions — Ally Service Marketplace.

Provides domain-specific exception classes for authentication failures (401),
authorization / RBAC violations (403), and password policy violations (400).
All classes inherit from Ally's core AppException hierarchy so that
exception_handlers.py serializes them into standardized ErrorResponse JSON.
"""

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    RateLimitException,
    UnauthorizedException,
)


# =============================================================================
# 401 Unauthorized — Authentication Failures
# =============================================================================

class AuthenticationError(UnauthorizedException):
    """Base exception for all authentication and token validation failures (HTTP 401)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_FAILED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class InvalidCredentialsError(AuthenticationError):
    """401 — Invalid email, phone number, or password provided during login."""

    def __init__(
        self,
        message: str = "Invalid email, phone number, or password",
        error_code: str = "INVALID_CREDENTIALS",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class TokenExpiredError(AuthenticationError):
    """401 — JWT access token or refresh token has expired."""

    def __init__(
        self,
        message: str = "Token has expired. Please authenticate again",
        error_code: str = "TOKEN_EXPIRED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class InvalidTokenError(AuthenticationError):
    """401 — JWT is malformed, signature verification failed, or token type mismatch."""

    def __init__(
        self,
        message: str = "Invalid authentication token",
        error_code: str = "INVALID_TOKEN",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class TokenRevokedError(AuthenticationError):
    """401 — Refresh token version mismatch or explicitly revoked token."""

    def __init__(
        self,
        message: str = "Token has been revoked. Please log in again",
        error_code: str = "TOKEN_REVOKED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


# =============================================================================
# 403 Forbidden — Authorization & RBAC Failures
# =============================================================================

class AuthorizationError(ForbiddenException):
    """Base exception for all authorization, RBAC, and account state failures (HTTP 403)."""

    def __init__(
        self,
        message: str = "Access denied",
        error_code: str = "AUTHORIZATION_FAILED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class AccountInactiveError(AuthorizationError):
    """403 — User account is voluntarily deactivated or inactive."""

    def __init__(
        self,
        message: str = "Account is inactive. Please contact support",
        error_code: str = "ACCOUNT_INACTIVE",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class AccountBlockedError(AuthorizationError):
    """403 — User account has been blocked or suspended by an administrator."""

    def __init__(
        self,
        message: str = "Account has been blocked due to policy violations",
        error_code: str = "ACCOUNT_BLOCKED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class AccountPendingVerificationError(AuthorizationError):
    """403 — User account registration is pending contact verification."""

    def __init__(
        self,
        message: str = "Account verification is pending. Please verify your email or phone",
        error_code: str = "ACCOUNT_PENDING_VERIFICATION",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class InsufficientPermissionsError(AuthorizationError):
    """403 — User role lacks required permission to access this resource or action."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        error_code: str = "INSUFFICIENT_PERMISSIONS",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class ProfileIncompleteError(AuthorizationError):
    """403 — Action requires the user to complete their profile first."""

    def __init__(
        self,
        message: str = "Please complete your profile before accessing this feature",
        error_code: str = "PROFILE_INCOMPLETE",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class EmailNotVerifiedError(AuthorizationError):
    """403 — Action requires a verified email address."""

    def __init__(
        self,
        message: str = "Please verify your email address to proceed",
        error_code: str = "EMAIL_NOT_VERIFIED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class PhoneNotVerifiedError(AuthorizationError):
    """403 — Action requires a verified phone number."""

    def __init__(
        self,
        message: str = "Please verify your phone number to proceed",
        error_code: str = "PHONE_NOT_VERIFIED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


# =============================================================================
# 400 Bad Request — Password Security & Policy Violations
# =============================================================================

class PasswordStrengthError(BadRequestException):
    """400 — Password does not meet OWASP complexity and length requirements."""

    def __init__(
        self,
        message: str = "Password does not meet security requirements",
        error_code: str = "PASSWORD_WEAK",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


# =============================================================================
# Account Lockout & OTP Security Exceptions (Phase 3.3)
# =============================================================================

class AccountLockedError(AuthorizationError):
    """403 — Account is temporarily locked due to excessive failed login attempts."""

    def __init__(
        self,
        message: str = "Account is temporarily locked due to too many failed login attempts",
        error_code: str = "ACCOUNT_LOCKED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class OTPExpiredError(BadRequestException):
    """400 — OTP code has expired."""

    def __init__(
        self,
        message: str = "OTP code has expired. Please request a new code",
        error_code: str = "OTP_EXPIRED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class OTPInvalidError(BadRequestException):
    """400 — OTP code is invalid."""

    def __init__(
        self,
        message: str = "Invalid OTP code",
        error_code: str = "OTP_INVALID",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class OTPRateLimitError(RateLimitException):
    """429 — Too many OTP send or resend requests."""

    def __init__(
        self,
        message: str = "Too many OTP requests. Please wait before requesting again",
        error_code: str = "OTP_RATE_LIMITED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class OTPMaxRetriesExceededError(BadRequestException):
    """400 — Maximum failed OTP verification attempts exceeded."""

    def __init__(
        self,
        message: str = "Maximum OTP verification attempts exceeded. Please request a new code",
        error_code: str = "OTP_MAX_RETRIES_EXCEEDED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)


class OTPMaxResendsExceededError(BadRequestException):
    """400 — Maximum OTP resend attempts exceeded."""

    def __init__(
        self,
        message: str = "Maximum OTP resend attempts exceeded for this request",
        error_code: str = "OTP_MAX_RESENDS_EXCEEDED",
        details: list | None = None,
    ) -> None:
        super().__init__(message=message, error_code=error_code, details=details)

