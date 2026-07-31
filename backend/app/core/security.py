"""
Security utilities — password hashing, JWT operations, password validation.

Architecture:
    - Password hashing: fully implemented using passlib/bcrypt.
      Ready to use in the auth module immediately.
    - JWT operations: interface defined with full signatures and types.
      Raises NotImplementedError until auth module activates JWT_SECRET_KEY.
    - Password validation: rule-based validator for password strength.
      Used during user registration and password change.

Design decisions:
    - passlib CryptContext handles salt generation, work factor tuning,
      and hash format verification. No manual bcrypt calls.
    - JWT functions are synchronous (PyJWT encode/decode is CPU-bound,
      not I/O). They run in the FastAPI thread pool automatically.
    - Token payloads use 'sub' (subject) for user ID per RFC 7519.
    - Password validation returns a list of failures (not bool) so the
      frontend can display all issues at once, not one at a time.
"""

import re
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings


# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------
# bcrypt is the industry standard for password storage:
#   - Automatic random salt per hash (no salt management needed).
#   - Configurable work factor (rounds=12 = ~250ms per hash).
#   - Resistant to GPU/ASIC brute-force attacks.
#
# Usage:
#     hashed = hash_password("user_password")
#     is_valid = verify_password("user_password", hashed)

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",    # Auto-mark old schemes as deprecated
    bcrypt__rounds=12,    # Work factor: 2^12 iterations (~250ms per hash)
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Returns a string like '$2b$12$...' containing the algorithm,
    work factor, salt, and hash. Safe to store in the database.

    Args:
        plain_password: The user's plain-text password.

    Returns:
        Bcrypt hash string.
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: The password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches the hash.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# Password Validation
# ---------------------------------------------------------------------------
# Rules for password strength. Returns all failures at once so the
# frontend can display them together, not one error at a time.
#
# Usage:
#     errors = validate_password_strength("weak")
#     if errors:
#         raise BadRequestException(message="Weak password", details=errors)

# Minimum password length
_MIN_PASSWORD_LENGTH = 8


def validate_password_strength(password: str) -> list[str]:
    """
    Validate password against strength rules.

    Returns an empty list if the password is strong enough.
    Returns a list of human-readable failure messages otherwise.

    Rules:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

    Args:
        password: The password to validate.

    Returns:
        List of failure messages (empty = valid).
    """
    failures: list[str] = []

    if len(password) < _MIN_PASSWORD_LENGTH:
        failures.append(
            f"Password must be at least {_MIN_PASSWORD_LENGTH} characters"
        )

    if not re.search(r"[A-Z]", password):
        failures.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        failures.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        failures.append("Password must contain at least one digit")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        failures.append("Password must contain at least one special character")

    return failures


# ---------------------------------------------------------------------------
# JWT Token Operations
# ---------------------------------------------------------------------------
# Interface for JWT access and refresh tokens. These functions define
# the contract that the auth module will use. Currently raises
# NotImplementedError because JWT_SECRET_KEY is None in .env.
#
# When the auth module is built:
#   1. Set JWT_SECRET_KEY in .env
#   2. The functions below will work as-is (no code changes needed)
#
# Token types:
#   - Access token: short-lived (30 min), sent in Authorization header.
#   - Refresh token: long-lived (7 days), used to get new access tokens.

# Token type identifiers embedded in the payload
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _get_jwt_secret() -> str:
    """
    Extract JWT secret key from config.

    Raises:
        NotImplementedError: If JWT_SECRET_KEY is not configured.
    """
    if settings.JWT_SECRET_KEY is None:
        raise NotImplementedError(
            "JWT_SECRET_KEY is not configured. "
            "Set it in .env to enable token operations. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    return settings.JWT_SECRET_KEY.get_secret_value()


def create_access_token(
    subject: str,
    extra_claims: dict | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: User ID (stored as 'sub' claim per RFC 7519).
        extra_claims: Additional claims to include (e.g., role, phone).

    Returns:
        Encoded JWT string.

    Raises:
        NotImplementedError: If JWT_SECRET_KEY is not configured.
    """
    secret = _get_jwt_secret()

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        **(extra_claims or {}),
    }

    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Refresh tokens contain minimal claims (just subject and type).
    They are used only to obtain new access tokens, not for API access.

    Args:
        subject: User ID (stored as 'sub' claim).

    Returns:
        Encoded JWT string.

    Raises:
        NotImplementedError: If JWT_SECRET_KEY is not configured.
    """
    secret = _get_jwt_secret()

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": REFRESH_TOKEN_TYPE,
        "iat": now,
        "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    }

    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Verifies the signature and expiration. Returns the payload dict
    if valid. Raises specific exceptions for different failure modes
    so the auth module can return appropriate error messages.

    Args:
        token: The encoded JWT string.

    Returns:
        Decoded payload dictionary with claims.

    Raises:
        NotImplementedError: If JWT_SECRET_KEY is not configured.
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is malformed or signature is invalid.
    """
    secret = _get_jwt_secret()

    return jwt.decode(
        token,
        secret,
        algorithms=[settings.JWT_ALGORITHM],
    )
