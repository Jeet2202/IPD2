"""
Authentication FastAPI Router — endpoints for Auth, Sessions, Passwords, and OTP Verification.

Architecture:
    - Route handling layer — request validation, status codes, OpenAPI documentation, and response serialization.
    - Zero business logic and zero database queries inside routes.
    - Delegates execution to AuthService.
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Request, status

from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MeResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResendEmailOTPRequest,
    ResetPasswordRequest,
    SuccessResponse,
    TokenResponse,
    VerifyEmailRequest,
    VerifyPasswordResetOTPRequest,
    VerifyPhoneRequest,
)
from app.auth.service import AuthService
from app.core.dependencies import CurrentUserDep
from app.core.exceptions import AppException

router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Customer or Worker account",
    description="""
Create a new user account as a Customer or Worker.

**Flow:**
- Validates input payload and password strength.
- Checks for duplicate email or phone number.
- Hashes password using bcrypt.
- Creates User document (is_email_verified = False) and associated Profile document.
- Generates 6-digit Email OTP and sends verification email.
- Returns user details with instructions to verify email.
""",
)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
) -> SuccessResponse:
    """Register a new customer or worker account."""
    user, info = await AuthService.register(
        payload,
        background_tasks=background_tasks,
    )

    return SuccessResponse(
        success=True,
        message=info["message"],
        data={
            "user": user.model_dump(mode="json"),
            "email": info["email"],
            "registration_status": info["registration_status"],
            "email_delivery_status": info["email_delivery_status"],
        },
    )


@router.post(
    "/verify-email",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email address using OTP code",
    description="Validate 6-digit OTP code sent during registration, mark email as verified, and issue initial JWT authentication tokens.",
)
async def verify_email(payload: VerifyEmailRequest) -> SuccessResponse:
    """Verify email address using OTP and issue authentication tokens."""
    user, tokens = await AuthService.verify_email(payload)
    return SuccessResponse(
        success=True,
        message="Email address verified successfully. Welcome to KaamSetu!",
        data={
            "user": user.model_dump(mode="json"),
            "tokens": tokens.model_dump(mode="json"),
        },
    )


@router.post(
    "/resend-email-otp",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend email verification or reset OTP",
    description="Resend a new 6-digit OTP code to the specified email address, enforcing resend cooldown and attempt limits.",
)
async def resend_email_otp(
    payload: ResendEmailOTPRequest,
    background_tasks: BackgroundTasks,
) -> SuccessResponse:
    """Resend verification OTP code to email."""
    result = await AuthService.resend_email_otp(payload, background_tasks=background_tasks)
    return SuccessResponse(
        success=True,
        message=result["message"],
    )


@router.post(
    "/login",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate using Email or Phone number",
    description="""
Authenticate an existing user with Email or Phone and password.

**Security:**
- Enforces verified email requirement.
- Defends against account enumeration via constant-time password check.
- Validates account active status.
- Captures device info (device_id, browser, IP) for session tracking.
- Updates last_login timestamp and returns authenticated user and token pair.
""",
)
async def login(
    payload: LoginRequest,
    request: Request,
) -> SuccessResponse:
    """Login with email or phone number."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    user, tokens = await AuthService.login(
        payload=payload,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    return SuccessResponse(
        success=True,
        message="Login successful",
        data={
            "user": user.model_dump(mode="json"),
            "tokens": tokens.model_dump(mode="json"),
        },
    )


@router.post(
    "/refresh",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token using refresh token",
    description="""
Obtain a fresh Access Token and rotated Refresh Token.

**Security & Rotation:**
- Revokes previous refresh token on success (Token Rotation).
- Replay Protection: If a revoked refresh token is re-submitted, ALL active sessions for that user are immediately invalidated.
""",
)
async def refresh_tokens(payload: RefreshTokenRequest) -> SuccessResponse:
    """Refresh JWT access token using valid refresh token."""
    new_tokens = await AuthService.refresh_tokens(payload)
    return SuccessResponse(
        success=True,
        message="Token refreshed successfully",
        data=new_tokens.model_dump(mode="json"),
    )


@router.post(
    "/logout",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout current device session",
    description="Revoke the provided refresh token session for the current device.",
)
async def logout(payload: LogoutRequest) -> SuccessResponse:
    """Logout current device by revoking its refresh token."""
    await AuthService.logout(payload.refresh_token)
    return SuccessResponse(
        success=True,
        message="Logged out successfully",
    )


@router.post(
    "/logout-all",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout from all devices",
    description="Revoke all active sessions across all devices for the current user.",
)
async def logout_all(current_user: CurrentUserDep) -> SuccessResponse:
    """Revoke all active sessions across all devices for authenticated user."""
    revoked_count = await AuthService.logout_all(current_user.id)
    return SuccessResponse(
        success=True,
        message=f"Logged out from all devices ({revoked_count} active sessions revoked)",
    )


@router.get(
    "/me",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieve public identity details of the currently authenticated user.",
)
async def get_me(current_user: CurrentUserDep) -> SuccessResponse:
    """Get current user details."""
    user_response = await AuthService.get_current_user_profile(current_user.id)
    return SuccessResponse(
        success=True,
        message="User profile retrieved successfully",
        data={"user": user_response.model_dump(mode="json")},
    )


@router.get(
    "/sessions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="List active device sessions",
    description="Retrieve all active logged-in device sessions for the authenticated user.",
)
async def list_sessions(current_user: CurrentUserDep) -> SuccessResponse:
    """List active device sessions."""
    sessions = await AuthService.get_active_sessions(current_user.id)
    return SuccessResponse(
        success=True,
        message="Active sessions retrieved successfully",
        data={"sessions": [s.model_dump(mode="json") for s in sessions]},
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke a specific device session",
    description="Revoke an active device session by session ID or JTI.",
)
async def revoke_session(
    session_id: str,
    current_user: CurrentUserDep,
) -> SuccessResponse:
    """Revoke a specific device session."""
    await AuthService.revoke_session(current_user.id, session_id)
    return SuccessResponse(
        success=True,
        message="Session revoked successfully",
    )


@router.post(
    "/change-password",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description="Verify current password, apply new password, and invalidate all active sessions.",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUserDep,
) -> SuccessResponse:
    """Change current user password and revoke all sessions."""
    await AuthService.change_password(current_user.id, payload)
    return SuccessResponse(
        success=True,
        message="Password changed successfully. All active sessions have been revoked. Please log in again.",
    )


@router.post(
    "/forgot-password",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset OTP",
    description="Generate secure password reset OTP and deliver via email. Always returns success message to prevent email enumeration.",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
) -> SuccessResponse:
    """Initiate password reset process by requesting an OTP."""
    await AuthService.forgot_password(payload, background_tasks=background_tasks)
    return SuccessResponse(
        success=True,
        message="If an account exists with this email address, a password reset OTP code has been sent.",
    )


@router.post(
    "/verify-password-reset-otp",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify password reset OTP",
    description="Validate 6-digit password reset OTP and return a temporary authorization token for resetting password.",
)
async def verify_password_reset_otp(payload: VerifyPasswordResetOTPRequest) -> SuccessResponse:
    """Verify password reset OTP code."""
    result = await AuthService.verify_password_reset_otp(payload)
    return SuccessResponse(
        success=True,
        message=result["message"],
        data={"reset_token": result["reset_token"]},
    )


@router.post(
    "/reset-password",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password using reset token",
    description="Validate reset token, apply new password, and invalidate all existing active sessions.",
)
async def reset_password(payload: ResetPasswordRequest) -> SuccessResponse:
    """Reset password using reset authorization token."""
    await AuthService.reset_password(payload)
    return SuccessResponse(
        success=True,
        message="Password reset successfully. You can now log in with your new password.",
    )


@router.post(
    "/verify-phone",
    response_model=SuccessResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Verify phone number (Future Scope)",
    description="Phone verification is planned for a future release. Currently returns HTTP 501 Not Implemented.",
)
async def verify_phone(payload: VerifyPhoneRequest) -> SuccessResponse:
    """Verify phone number OTP (Future Scope)."""
    raise AppException(
        message="Phone verification is not available in the current version. This feature is planned for a future release.",
        error_code="FEATURE_NOT_IMPLEMENTED",
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
    )
