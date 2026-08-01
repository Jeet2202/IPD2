"""
Authentication Utilities — KaamSetu Service Marketplace.

Provides reusable helper functions for extracting HTTP Bearer tokens,
validating OWASP password complexity, generating cryptographic random
tokens, checking account lifecycle states, and safely loading JWT secrets.
"""

import re
import secrets
from datetime import datetime, timezone

from app.auth.constants import (
    AUTH_HEADER_PREFIX,
    DEV_FALLBACK_SECRET_KEY,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from app.auth.exceptions import InvalidTokenError
from app.auth.models import AccountStatus, UserRole
from app.core.config import settings


def extract_bearer_token(authorization_header: str | None) -> str:
    """
    Extract and validate a JWT string from an HTTP Authorization header.

    Args:
        authorization_header: Value of the Authorization header (e.g., 'Bearer <jwt>').

    Returns:
        The stripped token string.

    Raises:
        InvalidTokenError: If the header is missing or does not start with 'Bearer '.
    """
    if not authorization_header or not authorization_header.startswith(AUTH_HEADER_PREFIX):
        raise InvalidTokenError(
            message="Authorization header missing or invalid scheme. Expected 'Bearer <token>'",
            error_code="INVALID_AUTH_HEADER",
        )
    token = authorization_header[len(AUTH_HEADER_PREFIX):].strip()
    if not token:
        raise InvalidTokenError(
            message="Bearer token string is empty",
            error_code="EMPTY_BEARER_TOKEN",
        )
    return token


def validate_password_strength(password: str) -> list[str]:
    """
    Validate password against OWASP complexity rules.

    Rules enforced:
      1. Minimum length (8 characters).
      2. Maximum length (128 characters to prevent bcrypt DoS).
      3. At least one uppercase letter (A-Z).
      4. At least one lowercase letter (a-z).
      5. At least one numeric digit (0-9).
      6. At least one special character (!@#$%^&*(),.?":{}|<> etc.).

    Args:
        password: Plaintext password to evaluate.

    Returns:
        A list of failure description strings. Empty list if password is strong.
    """
    failures: list[str] = []

    if len(password) < MIN_PASSWORD_LENGTH:
        failures.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    if len(password) > MAX_PASSWORD_LENGTH:
        failures.append(f"Password must not exceed {MAX_PASSWORD_LENGTH} characters")

    if not re.search(r"[A-Z]", password):
        failures.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        failures.append("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        failures.append("Password must contain at least one digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        failures.append("Password must contain at least one special character")

    return failures


def generate_secure_random_token(length: int = 32) -> str:
    """
    Generate a URL-safe cryptographically secure random token.

    Useful for password reset tokens, email verification links, and OTP salts.

    Args:
        length: Number of random bytes before base64url encoding.

    Returns:
        URL-safe random token string.
    """
    return secrets.token_urlsafe(length)


def is_account_active(status: AccountStatus) -> bool:
    """
    Check if an account lifecycle status allows normal platform operations.

    Args:
        status: The user's current AccountStatus enum value.

    Returns:
        True if the account is ACTIVE, False otherwise.
    """
    return status == AccountStatus.ACTIVE


def can_access_admin_panel(role: UserRole) -> bool:
    """
    Check if a platform role is permitted to access administrative workflows.

    Args:
        role: The user's UserRole enum value.

    Returns:
        True if role is ADMIN, False otherwise.
    """
    return role == UserRole.ADMIN


def get_jwt_secret_key() -> str:
    """
    Retrieve the JWT signing secret from application settings.

    In development/staging, if JWT_SECRET_KEY is unconfigured in .env,
    this falls back to a deterministic development secret so local testing works.
    In production (ENVIRONMENT=production), it raises a RuntimeError to prevent
    insecure token signing.

    Returns:
        The secret key string used for HMAC signing.

    Raises:
        RuntimeError: If running in production without a configured JWT_SECRET_KEY.
    """
    if settings.JWT_SECRET_KEY is not None:
        return settings.JWT_SECRET_KEY.get_secret_value()

    if settings.is_production:
        raise RuntimeError(
            "CRITICAL SECURITY CONFIGURATION ERROR: "
            "settings.JWT_SECRET_KEY must be configured in a production environment."
        )

    return DEV_FALLBACK_SECRET_KEY


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-aware UTC.
    If naive (e.g. loaded from MongoDB), attach timezone.utc.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
