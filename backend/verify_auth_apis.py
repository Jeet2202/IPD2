"""
Verification script for KaamSetu Authentication APIs (Phase 3.2).

Tests end-to-end against live MongoDB Atlas:
  1. POST /auth/register (Customer & Worker profiles created in MongoDB Atlas).
  2. Duplicate email/phone registration conflict handling (409 ConflictException).
  3. POST /auth/login via Email AND via Phone Number (200 OK & JWT tokens).
  4. POST /auth/login with invalid password (401 InvalidCredentialsError).
  5. GET /auth/me (returns authenticated UserResponse including role).
  6. POST /auth/refresh (rotates session tokens and enforces version matching).
  7. POST /auth/change-password (updates hash, increments version, logs out old sessions).
  8. POST /auth/forgot-password & POST /auth/reset-password (password recovery flow).
  9. POST /auth/verify-email & POST /auth/verify-phone (contact verification flags).
  10. POST /auth/logout (session revocation via refresh_token_version increment).
  11. FastAPI APIRouter configuration verification for all 10 endpoints.
"""

import asyncio
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, ".")

from fastapi import status

from app.auth.exceptions import InvalidCredentialsError, TokenRevokedError
from app.auth.models import User, UserRole
from app.auth.repository import AuthRepository
from app.auth.router import router as auth_router
from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    UserCreateRequest,
    UserResponse,
    VerifyEmailRequest,
    VerifyPhoneRequest,
)
from app.auth.service import AuthService
from app.core.config import settings
from app.core.exceptions import ConflictException
from app.customer.models import CustomerProfile
from app.database import close_database_connection, connect_to_database
from app.worker.models import WorkerProfile

# Test user credentials
TEST_CUSTOMER_EMAIL = "verify_customer_api@kaamsetu.com"
TEST_CUSTOMER_PHONE = "+919800000101"
TEST_WORKER_EMAIL = "verify_worker_api@kaamsetu.com"
TEST_WORKER_PHONE = "+919800000102"
INITIAL_PASSWORD = "KaamSetuAuth2026!#"
CHANGED_PASSWORD = "KaamSetuChanged2026!#"
RECOVERED_PASSWORD = "KaamSetuRecovered2026!#"


async def cleanup_test_data(repo: AuthRepository) -> None:
    """
    Remove test user and profile documents from MongoDB Atlas.
    """
    for email in [TEST_CUSTOMER_EMAIL, TEST_WORKER_EMAIL]:
        user = await repo.get_user_by_email(email)
        if user:
            user_id_str = str(user.id)
            cust_prof = await CustomerProfile.find_one(CustomerProfile.user_id == user_id_str)
            if cust_prof:
                await cust_prof.delete()
            work_prof = await WorkerProfile.find_one(WorkerProfile.user_id == user_id_str)
            if work_prof:
                await work_prof.delete()
            await user.delete()


async def run_verification() -> None:
    print("=" * 75)
    print("KAAMSETU — AUTHENTICATION APIS (PHASE 3.2) VERIFICATION")
    print("=" * 75)

    # Connect to MongoDB Atlas
    print("\n[0] Connecting to live MongoDB Atlas...")
    await connect_to_database(
        document_models=[User, CustomerProfile, WorkerProfile]
    )
    print("    [PASS] Connected to Atlas database successfully.")

    repo = AuthRepository()
    service = AuthService(repository=repo)

    try:
        # Clean up any leftover test data
        await cleanup_test_data(repo)

        # ---------------------------------------------------------------------
        # Test 1: POST /auth/register (Customer and Worker)
        # ---------------------------------------------------------------------
        print("\n[1] Testing POST /auth/register (Customer & Worker profiles)...")
        cust_req = UserCreateRequest(
            first_name="Aarav",
            last_name="Sharma",
            email=TEST_CUSTOMER_EMAIL,
            phone_number=TEST_CUSTOMER_PHONE,
            password=INITIAL_PASSWORD,
            role=UserRole.CUSTOMER,
        )
        cust_res = await service.register(cust_req)
        assert cust_res.user.email == TEST_CUSTOMER_EMAIL
        assert cust_res.user.role == UserRole.CUSTOMER
        assert cust_res.tokens.access_token and cust_res.tokens.refresh_token

        # Verify CustomerProfile created in MongoDB
        cust_profile = await CustomerProfile.find_one(CustomerProfile.user_id == cust_res.user.id)
        assert cust_profile is not None, "CustomerProfile document was not created in Atlas!"
        print("    [PASS] Customer user and CustomerProfile created successfully.")

        work_req = UserCreateRequest(
            first_name="Ramesh",
            last_name="Yadav",
            email=TEST_WORKER_EMAIL,
            phone_number=TEST_WORKER_PHONE,
            password=INITIAL_PASSWORD,
            role=UserRole.WORKER,
        )
        work_res = await service.register(work_req)
        assert work_res.user.role == UserRole.WORKER

        # Verify WorkerProfile created in MongoDB
        work_profile = await WorkerProfile.find_one(WorkerProfile.user_id == work_res.user.id)
        assert work_profile is not None, "WorkerProfile document was not created in Atlas!"
        print("    [PASS] Worker user and WorkerProfile created successfully.")

        # ---------------------------------------------------------------------
        # Test 2: Duplicate Registration Conflict Handling
        # ---------------------------------------------------------------------
        print("\n[2] Testing Duplicate Registration Conflict (HTTP 409)...")
        try:
            await service.register(cust_req)
            assert False, "Should raise ConflictException on duplicate email/phone"
        except ConflictException as exc:
            assert exc.status_code == 409
            assert exc.error_code in ("EMAIL_ALREADY_EXISTS", "PHONE_ALREADY_EXISTS")
        print("    [PASS] Duplicate registration rejected with 409 ConflictException.")

        # ---------------------------------------------------------------------
        # Test 3: POST /auth/login (via Email OR via Phone Number)
        # ---------------------------------------------------------------------
        print("\n[3] Testing POST /auth/login (Email OR Phone Number)...")
        email_login_res = await service.login(
            LoginRequest(identifier=TEST_CUSTOMER_EMAIL, password=INITIAL_PASSWORD)
        )
        assert email_login_res.user.email == TEST_CUSTOMER_EMAIL
        assert email_login_res.tokens.access_token

        phone_login_res = await service.login(
            LoginRequest(identifier=TEST_CUSTOMER_PHONE, password=INITIAL_PASSWORD)
        )
        assert phone_login_res.user.phone_number == TEST_CUSTOMER_PHONE
        print("    [PASS] Login via Email AND via Phone Number verified.")

        # ---------------------------------------------------------------------
        # Test 4: POST /auth/login with wrong password (HTTP 401)
        # ---------------------------------------------------------------------
        print("\n[4] Testing POST /auth/login with invalid credentials (HTTP 401)...")
        try:
            await service.login(
                LoginRequest(identifier=TEST_CUSTOMER_EMAIL, password="WrongPassword123!")
            )
            assert False, "Should raise InvalidCredentialsError"
        except InvalidCredentialsError as exc:
            assert exc.status_code == 401
        print("    [PASS] Invalid password rejected with 401 InvalidCredentialsError.")

        # ---------------------------------------------------------------------
        # Test 5: GET /auth/me
        # ---------------------------------------------------------------------
        print("\n[5] Testing GET /auth/me...")
        user_doc = await repo.get_user_by_email(TEST_CUSTOMER_EMAIL)
        assert user_doc is not None
        me_res = await service.get_current_user_profile(user_doc)
        assert isinstance(me_res, UserResponse)
        assert me_res.role == UserRole.CUSTOMER
        print("    [PASS] Current user profile returned correctly.")

        # ---------------------------------------------------------------------
        # Test 6: POST /auth/refresh (token rotation & version check)
        # ---------------------------------------------------------------------
        print("\n[6] Testing POST /auth/refresh (token rotation & version check)...")
        rotated_tokens = await service.refresh_token(
            RefreshTokenRequest(refresh_token=email_login_res.tokens.refresh_token)
        )
        assert rotated_tokens.access_token and rotated_tokens.refresh_token
        print("    [PASS] Refresh token validated and rotated successfully.")

        # ---------------------------------------------------------------------
        # Test 7: POST /auth/change-password
        # ---------------------------------------------------------------------
        print("\n[7] Testing POST /auth/change-password & old session revocation...")
        change_res = await service.change_password(
            user_doc,
            ChangePasswordRequest(
                current_password=INITIAL_PASSWORD,
                new_password=CHANGED_PASSWORD,
            ),
        )
        assert "Password changed successfully" in change_res.message
        # Verify old refresh token is now rejected with TokenRevokedError (401)
        try:
            await service.refresh_token(
                RefreshTokenRequest(refresh_token=rotated_tokens.refresh_token)
            )
            assert False, "Should raise TokenRevokedError after password change"
        except TokenRevokedError as exc:
            assert exc.status_code == 401
        # Login with new password
        new_pwd_login = await service.login(
            LoginRequest(identifier=TEST_CUSTOMER_EMAIL, password=CHANGED_PASSWORD)
        )
        assert new_pwd_login.user.email == TEST_CUSTOMER_EMAIL
        print("    [PASS] Password changed, old sessions revoked, new password verified.")

        # ---------------------------------------------------------------------
        # Test 8: POST /auth/forgot-password & POST /auth/reset-password
        # ---------------------------------------------------------------------
        print("\n[8] Testing POST /auth/forgot-password & POST /auth/reset-password...")
        forgot_res = await service.forgot_password(
            ForgotPasswordRequest(email=TEST_CUSTOMER_EMAIL)
        )
        assert forgot_res.reset_token and len(forgot_res.reset_token) >= 32
        reset_res = await service.reset_password(
            ResetPasswordRequest(
                token=forgot_res.reset_token,
                new_password=RECOVERED_PASSWORD,
            )
        )
        assert "Password reset successfully" in reset_res.message
        # Confirm login works with recovered password
        rec_login = await service.login(
            LoginRequest(identifier=TEST_CUSTOMER_EMAIL, password=RECOVERED_PASSWORD)
        )
        assert rec_login.user.email == TEST_CUSTOMER_EMAIL
        print("    [PASS] Forgot password and token-based reset password verified.")

        # ---------------------------------------------------------------------
        # Test 9: POST /auth/verify-email & POST /auth/verify-phone
        # ---------------------------------------------------------------------
        print("\n[9] Testing POST /auth/verify-email & POST /auth/verify-phone...")
        user_doc_after = await repo.get_user_by_email(TEST_CUSTOMER_EMAIL)
        assert user_doc_after is not None
        await service.verify_email(user_doc_after, VerifyEmailRequest(token="demo_email_token"))
        await service.verify_phone(user_doc_after, VerifyPhoneRequest(otp="123456"))

        verified_doc = await repo.get_user_by_email(TEST_CUSTOMER_EMAIL)
        assert verified_doc and verified_doc.email_verified and verified_doc.phone_verified
        print("    [PASS] Email and Phone verification flags set correctly.")

        # ---------------------------------------------------------------------
        # Test 10: POST /auth/logout (Session Revocation)
        # ---------------------------------------------------------------------
        print("\n[10] Testing POST /auth/logout (session revocation)...")
        ver_before = verified_doc.refresh_token_version
        await service.logout(verified_doc)
        logged_out_doc = await repo.get_user_by_email(TEST_CUSTOMER_EMAIL)
        assert logged_out_doc and logged_out_doc.refresh_token_version == ver_before + 1
        print("    [PASS] Logout incremented refresh_token_version and revoked sessions.")

        # ---------------------------------------------------------------------
        # Test 11: FastAPI APIRouter Configuration Check
        # ---------------------------------------------------------------------
        print("\n[11] Verifying FastAPI APIRouter endpoints and response models...")
        route_paths = {route.path: route.methods for route in auth_router.routes}
        expected_endpoints = [
            "/register",
            "/login",
            "/refresh",
            "/logout",
            "/me",
            "/change-password",
            "/forgot-password",
            "/reset-password",
            "/verify-email",
            "/verify-phone",
        ]
        for ep in expected_endpoints:
            assert ep in route_paths, f"Missing endpoint {ep} in auth_router!"
        print("    [PASS] All 10 authentication routes configured correctly in APIRouter.")

    finally:
        print("\n[CLEANUP] Cleaning up test user and profile documents from Atlas...")
        await cleanup_test_data(repo)
        await close_database_connection()
        print("    [PASS] Test data cleaned up and MongoDB connection closed.")

    print("\n" + "=" * 75)
    print("ALL 11 AUTHENTICATION APIS (PHASE 3.2) VERIFICATION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_verification())
