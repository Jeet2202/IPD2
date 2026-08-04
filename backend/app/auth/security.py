"""
Authentication Security Module — Ally Service Marketplace.

Implements bcrypt password hashing, JWT access and refresh token lifecycle
management, cryptographic signature verification, and typed Pydantic v2
payload models.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.auth.constants import (
    ACCESS_TOKEN_TYPE,
    BCRYPT_WORK_FACTOR,
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_JWT_ALGORITHM,
    DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_BEARER,
)
from app.auth.exceptions import InvalidTokenError, TokenExpiredError
from app.auth.models import UserRole
from app.auth.utils import get_jwt_secret_key


# =============================================================================
# Pydantic v2 Token Payload & Response Models
# =============================================================================

class TokenPayload(BaseModel):
    """
    Decoded and validated JWT token payload schema.

    Attributes:
        sub: Subject — User's MongoDB Document ID string.
        role: Platform role enum (customer/worker/admin).
        type: Token type string ('access' or 'refresh').
        iat: Issued at timestamp (UTC epoch seconds).
        exp: Expiration timestamp (UTC epoch seconds).
        jti: Unique JWT identifier string.
        ver: Refresh token version counter (present only on refresh tokens).
    """

    model_config = ConfigDict(extra="allow")

    sub: str = Field(..., description="Subject — User document ID")
    role: UserRole = Field(..., description="Platform user role")
    type: str = Field(..., description="Token type ('access' or 'refresh')")
    iat: int = Field(..., description="Issued at timestamp (epoch seconds)")
    exp: int = Field(..., description="Expiration timestamp (epoch seconds)")
    jti: str | None = Field(default=None, description="Unique JWT ID")
    ver: int | None = Field(default=None, description="Refresh token revocation version")


class TokenPair(BaseModel):
    """
    Standard OAuth2 token response pair returned upon authentication.

    Attributes:
        access_token: Short-lived JWT access token string.
        refresh_token: Long-lived JWT refresh token string.
        token_type: HTTP authentication scheme (defaults to 'Bearer').
        expires_in: Seconds remaining until the access token expires.
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default=TOKEN_TYPE_BEARER, description="Authentication scheme")
    expires_in: int = Field(..., description="Access token TTL in seconds")


# =============================================================================
# Password Hashing Infrastructure (Bcrypt)
# =============================================================================

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=BCRYPT_WORK_FACTOR,
)


def hash_password(password: str) -> str:
    """
    Securely hash a plaintext password using bcrypt with automatic salt generation.

    Args:
        password: Plaintext password string.

    Returns:
        Bcrypt hash string ($2b$12$...).
    """
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain_password: User-provided plaintext password.
        hashed_password: Stored bcrypt hash from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# JWT Lifecycle Management
# =============================================================================

def create_access_token(
    subject: str,
    role: UserRole,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a short-lived JWT access token for API authorization.

    Args:
        subject: User document ID string.
        role: Platform user role.
        extra_claims: Optional dictionary of additional claims.
        expires_delta: Optional timedelta override for expiration.

    Returns:
        Encoded JWT access token string.
    """
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(minutes=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + delta

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role.value if isinstance(role, UserRole) else str(role),
        "type": ACCESS_TOKEN_TYPE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, get_jwt_secret_key(), algorithm=DEFAULT_JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    role: UserRole,
    version: int = 0,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a long-lived JWT refresh token with server-side revocation support.

    Args:
        subject: User document ID string.
        role: Platform user role.
        version: User's current refresh_token_version counter.
        extra_claims: Optional dictionary of additional claims.
        expires_delta: Optional timedelta override for expiration.

    Returns:
        Encoded JWT refresh token string.
    """
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(days=DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS)
    expire = now + delta

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role.value if isinstance(role, UserRole) else str(role),
        "type": REFRESH_TOKEN_TYPE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
        "ver": version,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, get_jwt_secret_key(), algorithm=DEFAULT_JWT_ALGORITHM)


def decode_token(
    token: str,
    expected_type: str | None = None,
) -> TokenPayload:
    """
    Decode and cryptographically verify a JWT string into a TokenPayload model.

    Args:
        token: Raw JWT string to verify.
        expected_type: Optional token type string ('access' or 'refresh') to enforce.

    Returns:
        Validated TokenPayload Pydantic instance.

    Raises:
        TokenExpiredError: If the token expiration timestamp is in the past.
        InvalidTokenError: If the token signature is invalid, malformed, or wrong type.
    """
    try:
        raw_payload = jwt.decode(
            token,
            get_jwt_secret_key(),
            algorithms=[DEFAULT_JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        payload = TokenPayload.model_validate(raw_payload)

        if expected_type and payload.type != expected_type:
            raise InvalidTokenError(
                message=f"Invalid token type. Expected '{expected_type}', got '{payload.type}'",
                error_code="TOKEN_TYPE_MISMATCH",
            )

        return payload

    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except (jwt.InvalidTokenError, ValidationError, KeyError, ValueError, TypeError) as exc:
        raise InvalidTokenError(
            message="Malformed or cryptographic signature validation failed",
            error_code="INVALID_TOKEN",
        ) from exc
