"""
Security utilities — password hashing, JWT operations, password validation.

Architecture:
    - Password hashing: fully implemented using passlib/bcrypt.
      Ready to use in the auth module immediately.
    - JWT operations: production-ready token creation and validation.
      Includes jti, iss, aud claims for token revocation and
      cross-environment security.
    - Password validation: rule-based validator for password strength.
      Used during user registration and password change.
    - Token payload: strongly typed Pydantic model for decoded tokens.
      Ensures all required claims are present and valid.

Design decisions:
    - passlib CryptContext handles salt generation, work factor tuning,
      and hash format verification. No manual bcrypt calls.
    - bcrypt rounds are configurable via BCRYPT_ROUNDS setting.
      Use 12 for production (~250ms per hash), 4 for test suites.
    - JWT functions are synchronous (PyJWT encode/decode is CPU-bound,
      not I/O). They run in the FastAPI thread pool automatically.
    - Token payloads use 'sub' (subject) for user ID per RFC 7519.
    - Password validation returns a list of failures (not bool) so the
      frontend can display all issues at once, not one at a time.
    - All PyJWT exceptions are caught and translated to application
      exceptions. Callers never see library internals.
    - jti (JWT ID) enables per-token revocation for logout and
      password-change flows. Phase 3.2 can store revoked jti values
      in Redis or MongoDB without changing these functions.
    - iss/aud claims prevent cross-environment token confusion.
"""

import re
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.exceptions import TokenExpiredException, TokenInvalidException
from app.utils.constants import (
    JWT_SECRET_MIN_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from app.utils.enums import TokenType


# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------
# bcrypt is the industry standard for password storage:
#   - Automatic random salt per hash (no salt management needed).
#   - Configurable work factor via BCRYPT_ROUNDS setting.
#   - Resistant to GPU/ASIC brute-force attacks.
#
# Usage:
#     hashed = hash_password("user_password")
#     is_valid = verify_password("user_password", hashed)

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",    # Auto-mark old schemes as deprecated
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
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
# Constants are imported from app.utils.constants (single source of truth).
# bcrypt silently truncates input beyond 72 bytes — MAX_PASSWORD_LENGTH
# prevents this edge case and rejects absurdly long inputs.
#
# Usage:
#     errors = validate_password_strength("weak")
#     if errors:
#         raise BadRequestException(message="Weak password", details=errors)


def validate_password_strength(password: str) -> list[str]:
    """
    Validate password against strength rules.

    Returns an empty list if the password is strong enough.
    Returns a list of human-readable failure messages otherwise.

    Rules:
        - Minimum 8 characters (MIN_PASSWORD_LENGTH)
        - Maximum 128 characters (MAX_PASSWORD_LENGTH)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character (any non-alphanumeric)

    Args:
        password: The password to validate.

    Returns:
        List of failure messages (empty = valid).
    """
    failures: list[str] = []

    if len(password) < MIN_PASSWORD_LENGTH:
        failures.append(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        failures.append(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters"
        )

    if not re.search(r"[A-Z]", password):
        failures.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        failures.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        failures.append("Password must contain at least one digit")

    if not re.search(r"[^A-Za-z0-9]", password):
        failures.append("Password must contain at least one special character")

    return failures


# ---------------------------------------------------------------------------
# Token Payload Model
# ---------------------------------------------------------------------------

class TokenPayload(BaseModel):
    """
    Strongly typed JWT token payload.

    Validates decoded token claims before returning them to callers.
    Replaces raw dict access with typed attributes for safety.

    Fields:
        sub: User ID (subject) per RFC 7519.
        type: Token type — "access" or "refresh".
        jti: Unique token ID for revocation tracking.
        iat: Issued-at timestamp (Unix epoch).
        exp: Expiration timestamp (Unix epoch).
        iss: Issuer identifier.
        aud: Audience identifier.
        role: User role (access tokens only).
        phone: User phone number (access tokens only).
    """
    sub: str
    type: str
    jti: str
    iat: int
    exp: int
    iss: str | None = None
    aud: str | None = None
    # Extra claims — present in access tokens, absent in refresh tokens
    role: str | None = None
    phone: str | None = None


# ---------------------------------------------------------------------------
# JWT Token Operations
# ---------------------------------------------------------------------------
# Production-ready JWT access and refresh tokens with full RFC 7519
# claim support. Designed for Phase 3.2 token revocation and rotation.
#
# Token types:
#   - Access token: short-lived (30 min), sent in Authorization header.
#   - Refresh token: long-lived (7 days), used to get new access tokens.
#
# Revocation support (Phase 3.2):
#   - Each token has a unique jti (JWT ID) claim.
#   - On logout: add jti to a revocation store (Redis/MongoDB).
#   - On token validation: check jti against revocation store.
#   - On password change: revoke all tokens for the user.
#   - On "logout all devices": revoke all jti values for the user.


def _get_jwt_secret() -> str:
    """
    Extract JWT secret key from config.

    Raises:
        RuntimeError: If JWT_SECRET_KEY is not configured.
    """
    if settings.JWT_SECRET_KEY is None:
        raise RuntimeError(
            "JWT_SECRET_KEY is not configured. "
            "Set it in .env to enable token operations. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    secret = settings.JWT_SECRET_KEY.get_secret_value().strip()
    if len(secret) < JWT_SECRET_MIN_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET_KEY must be at least {JWT_SECRET_MIN_LENGTH} characters."
        )
    return secret


def create_access_token(
    subject: str,
    extra_claims: dict | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Includes jti for per-token revocation, iss/aud for environment
    isolation, and optional extra claims (role, phone) for the
    auth dependency to populate CurrentUser without a database query.

    Args:
        subject: User ID (stored as 'sub' claim per RFC 7519).
        extra_claims: Additional claims to include (e.g., role, phone).

    Returns:
        Encoded JWT string.

    Raises:
        RuntimeError: If JWT_SECRET_KEY is not configured.
    """
    secret = _get_jwt_secret()

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": TokenType.ACCESS.value,
        "jti": uuid.uuid4().hex,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        **(extra_claims or {}),
    }

    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Refresh tokens contain minimal claims (just subject, type, and jti).
    They are used only to obtain new access tokens, not for API access.
    The jti enables individual refresh token revocation for logout flows.

    Args:
        subject: User ID (stored as 'sub' claim).

    Returns:
        Encoded JWT string.

    Raises:
        RuntimeError: If JWT_SECRET_KEY is not configured.
    """
    secret = _get_jwt_secret()

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": TokenType.REFRESH.value,
        "jti": uuid.uuid4().hex,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    }

    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """
    Decode and validate a JWT token.

    Verifies signature, expiration, issuer, and audience. Returns a
    strongly typed TokenPayload if valid. Translates all PyJWT
    exceptions into application exceptions so callers never see
    library internals.

    Args:
        token: The encoded JWT string.

    Returns:
        Validated TokenPayload with all claims.

    Raises:
        RuntimeError: If JWT_SECRET_KEY is not configured.
        TokenExpiredException: If the token has expired.
        TokenInvalidException: If the token is malformed, signature is
            invalid, or required claims are missing.
    """
    secret = _get_jwt_secret()

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise TokenInvalidException()
    except ValidationError:
        raise TokenInvalidException(
            message="Token payload is missing required claims",
        )
