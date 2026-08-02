"""
Verification script for KaamSetu Authentication Foundation.

Tests:
  1. Bcrypt password hashing and verification.
  2. OWASP password strength validation rules.
  3. JWT Access Token creation and decoding into TokenPayload.
  4. JWT Refresh Token creation, decoding, and version claims.
  5. Token expiration handling (TokenExpiredError).
  6. Token type mismatch enforcement (InvalidTokenError).
  7. Role-Based Access Control (RBAC) permission mapping and verification.
  8. Auth Exception hierarchy and HTTP status codes (400, 401, 403).
"""

import sys
from datetime import timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, ".")

from app.auth.constants import (
    ACCESS_TOKEN_TYPE,
    BCRYPT_WORK_FACTOR,
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_TYPE,
)
from app.auth.exceptions import (
    AccountBlockedError,
    AccountInactiveError,
    AuthenticationError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidTokenError,
    PasswordStrengthError,
    TokenExpiredError,
    TokenRevokedError,
)
from app.auth.models import UserRole
from app.auth.permissions import Permission, has_permission, require_permission
from app.auth.security import (
    TokenPayload,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.auth.utils import (
    extract_bearer_token,
    generate_secure_random_token,
    validate_password_strength,
)


def run_tests() -> None:
    print("=" * 70)
    print("KAAMSETU — AUTHENTICATION FOUNDATION VERIFICATION")
    print("=" * 70)

    # [Test 1] Bcrypt Password Hashing
    print("\n[1] Testing Bcrypt Password Hashing & Verification...")
    plain = "SuperSecretPassword123!"
    hashed = hash_password(plain)
    assert hashed.startswith("$2b$") or hashed.startswith("$2y$"), f"Unexpected format: {hashed}"
    assert verify_password(plain, hashed) is True, "Password verification failed!"
    assert verify_password("WrongPassword!", hashed) is False, "Wrong password verified incorrectly!"
    print("    [PASS] Bcrypt hashing & verification working correctly.")

    # [Test 2] OWASP Password Strength Validation
    print("\n[2] Testing OWASP Password Strength Validation...")
    weak_short = "short1!"
    weak_no_upper = "alllower123!"
    weak_no_digit = "NoDigitHere!"
    strong_pwd = "StrongKaamSetu2026!#"

    assert len(validate_password_strength(weak_short)) > 0, "Failed to catch short password"
    assert len(validate_password_strength(weak_no_upper)) > 0, "Failed to catch missing uppercase"
    assert len(validate_password_strength(weak_no_digit)) > 0, "Failed to catch missing digit"
    assert len(validate_password_strength(strong_pwd)) == 0, f"Strong password rejected: {validate_password_strength(strong_pwd)}"
    print("    [PASS] OWASP complexity rules enforced properly.")

    # [Test 3] Secure Random Token Generation & Bearer Extraction
    print("\n[3] Testing Secure Random Tokens & Bearer Header Extraction...")
    rng_token = generate_secure_random_token(32)
    assert len(rng_token) >= 32, "Random token shorter than expected"
    extracted = extract_bearer_token(f"Bearer {rng_token}")
    assert extracted == rng_token, "Bearer token extraction mismatch"
    try:
        extract_bearer_token("Basic abc123def456")
        assert False, "Should raise InvalidTokenError for non-Bearer scheme"
    except InvalidTokenError as exc:
        assert exc.status_code == 401
    print("    [PASS] Bearer extraction and secure RNG verified.")

    # [Test 4] JWT Access & Refresh Token Lifecycle
    print("\n[4] Testing JWT Access & Refresh Token Lifecycle...")
    subject_id = "user_mongo_id_abc123"
    access_tok = create_access_token(subject=subject_id, role=UserRole.CUSTOMER)
    refresh_tok = create_refresh_token(subject=subject_id, role=UserRole.CUSTOMER, version=3)

    decoded_access = decode_token(access_tok, expected_type=ACCESS_TOKEN_TYPE)
    assert isinstance(decoded_access, TokenPayload)
    assert decoded_access.sub == subject_id
    assert decoded_access.role == UserRole.CUSTOMER
    assert decoded_access.type == ACCESS_TOKEN_TYPE
    assert decoded_access.jti is not None

    decoded_refresh = decode_token(refresh_tok, expected_type=REFRESH_TOKEN_TYPE)
    assert decoded_refresh.ver == 3
    print("    [PASS] Token creation and TokenPayload decoding verified.")

    # [Test 5] Token Type Mismatch Enforcement
    print("\n[5] Testing Token Type Mismatch Enforcement...")
    try:
        decode_token(access_tok, expected_type=REFRESH_TOKEN_TYPE)
        assert False, "Should raise InvalidTokenError on token type mismatch"
    except InvalidTokenError as exc:
        assert exc.status_code == 401
        assert "TOKEN_TYPE_MISMATCH" in exc.error_code
    print("    [PASS] Token type mismatch caught with 401 InvalidTokenError.")

    # [Test 6] Token Expiration Enforcement
    print("\n[6] Testing Token Expiration Enforcement...")
    expired_tok = create_access_token(
        subject=subject_id,
        role=UserRole.WORKER,
        expires_delta=timedelta(seconds=-10),  # Expired 10 seconds ago
    )
    try:
        decode_token(expired_tok, expected_type=ACCESS_TOKEN_TYPE)
        assert False, "Should raise TokenExpiredError for expired token"
    except TokenExpiredError as exc:
        assert exc.status_code == 401
        assert exc.error_code == "TOKEN_EXPIRED"
    print("    [PASS] Expired tokens raise 401 TokenExpiredError.")

    # [Test 7] Role-Based Access Control (RBAC) Verification
    print("\n[7] Testing Granular RBAC Permissions & Admin Full Access...")
    assert has_permission(UserRole.CUSTOMER, Permission.SERVICE_REQUEST_CREATE) is True
    assert has_permission(UserRole.CUSTOMER, Permission.JOB_ACCEPT) is False
    assert has_permission(UserRole.WORKER, Permission.JOB_ACCEPT) is True
    assert has_permission(UserRole.WORKER, Permission.SERVICE_REQUEST_CREATE) is False

    # Admin has ADMIN_FULL_ACCESS and can perform any action
    assert has_permission(UserRole.ADMIN, Permission.JOB_ACCEPT) is True
    assert has_permission(UserRole.ADMIN, Permission.SYSTEM_CONFIG_MANAGE) is True

    try:
        require_permission(UserRole.CUSTOMER, Permission.SYSTEM_CONFIG_MANAGE)
        assert False, "Should raise InsufficientPermissionsError"
    except InsufficientPermissionsError as exc:
        assert exc.status_code == 403
        assert exc.error_code == "INSUFFICIENT_PERMISSIONS"
    print("    [PASS] RBAC mappings and permission verification working correctly.")

    # [Test 8] Exception Hierarchy Check
    print("\n[8] Testing Authentication Exception Hierarchy & HTTP Codes...")
    assert AuthenticationError().status_code == 401
    assert InvalidCredentialsError().status_code == 401
    assert TokenExpiredError().status_code == 401
    assert InvalidTokenError().status_code == 401
    assert TokenRevokedError().status_code == 401
    assert AccountInactiveError().status_code == 403
    assert AccountBlockedError().status_code == 403
    assert InsufficientPermissionsError().status_code == 403
    assert PasswordStrengthError().status_code == 400
    print("    [PASS] All auth exceptions map to correct HTTP status codes.")

    print("\n" + "=" * 70)
    print("ALL AUTHENTICATION FOUNDATION VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
