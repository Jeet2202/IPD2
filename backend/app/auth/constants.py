"""
Authentication and Authorization Constants — KaamSetu Service Marketplace.

Single source of truth for token type identifiers, HTTP header formatting,
JWT claim names, expiration fallbacks, and OWASP password security bounds.
"""

from typing import Final

# ---------------------------------------------------------------------------
# Token Type Identifiers
# ---------------------------------------------------------------------------
ACCESS_TOKEN_TYPE: Final[str] = "access"
REFRESH_TOKEN_TYPE: Final[str] = "refresh"
TOKEN_TYPE_BEARER: Final[str] = "Bearer"

# ---------------------------------------------------------------------------
# HTTP Headers & Authentication Schemes
# ---------------------------------------------------------------------------
AUTH_HEADER_NAME: Final[str] = "Authorization"
AUTH_HEADER_PREFIX: Final[str] = "Bearer "

# ---------------------------------------------------------------------------
# JWT Standard & Custom Claim Keys
# ---------------------------------------------------------------------------
CLAIM_SUBJECT: Final[str] = "sub"         # User ID per RFC 7519
CLAIM_ROLE: Final[str] = "role"           # Platform UserRole (customer/worker/admin)
CLAIM_TOKEN_TYPE: Final[str] = "type"       # Token type ("access" or "refresh")
CLAIM_ISSUED_AT: Final[str] = "iat"         # Issued at timestamp (UTC epoch seconds)
CLAIM_EXPIRES_AT: Final[str] = "exp"        # Expiration timestamp (UTC epoch seconds)
CLAIM_JWT_ID: Final[str] = "jti"            # Unique JWT identifier per RFC 7519
CLAIM_TOKEN_VERSION: Final[str] = "ver"     # Refresh token version for revocation checking

# ---------------------------------------------------------------------------
# JWT Expiry & Security Default Fallbacks
# ---------------------------------------------------------------------------
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = 7
DEFAULT_JWT_ALGORITHM: Final[str] = "HS256"

# Deterministic development fallback secret — raises RuntimeError in production
DEV_FALLBACK_SECRET_KEY: Final[str] = (
    "kaamsetu-dev-insecure-jwt-secret-key-do-not-use-in-production-2026"
)

# ---------------------------------------------------------------------------
# OWASP Password Security Constraints
# ---------------------------------------------------------------------------
MIN_PASSWORD_LENGTH: Final[int] = 8
MAX_PASSWORD_LENGTH: Final[int] = 128
BCRYPT_WORK_FACTOR: Final[int] = 12

# ---------------------------------------------------------------------------
# Security & Account Lockout Constants
# ---------------------------------------------------------------------------
MAX_FAILED_LOGIN_ATTEMPTS: Final[int] = 5
LOCKOUT_DURATION_MINUTES: Final[int] = 15
