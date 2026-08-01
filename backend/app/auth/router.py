"""
Authentication API Router — KaamSetu Service Marketplace.

Defines HTTP routes for user registration, dual-token authentication,
token rotation, session logout, profile introspection, password management,
and contact verification.

Strictly handles request parsing, dependency injection, and HTTP responses,
delegating all business rules and database persistence to AuthService.
"""

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import ActiveUserDep
from app.auth.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginHistoryResponse,
    LoginRequest,
    LogoutDeviceRequest,
    MessageResponse,
    OTPLoginRequest,
    OTPResponse,
    RefreshTokenRequest,
    ResendOTPRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    SessionResponse,
    UserCreateRequest,
    UserResponse,
    VerifyEmailRequest,
    VerifyOTPRequest,
    VerifyPhoneRequest,
)
from app.auth.security import TokenPair
from app.auth.service import AuthService

router = APIRouter()


def get_auth_service() -> AuthService:
    """
    Dependency injection provider for AuthService.
    """
    return AuthService()


def _get_ip_and_device(
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> tuple[str | None, str | None]:
    ip = request.client.host if request.client else None
    return ip, user_agent


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account (Customer or Worker)",
)
async def register(
    req: UserCreateRequest,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """
    Register a new user account, hash the password using bcrypt, create the
    corresponding CustomerProfile or WorkerProfile document, and return fresh
    JWT access and refresh tokens.
    """
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.register(req, ip_address=ip, device=device)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate via Email or Phone Number",
)
async def login(
    req: LoginRequest,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """
    Authenticate a user using their registered Email Address OR E.164 Phone Number
    and password. Verifies account status, updates last login time, and returns
    fresh JWT access and refresh tokens.
    """
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.login(req, ip_address=ip, device=device)


@router.post(
    "/refresh",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token using refresh token",
)
async def refresh_token(
    req: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """
    Rotate session tokens by validating the presented refresh token against the
    user's current revocation counter.
    """
    return await service.refresh_token(req)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out of the current session",
)
async def logout(
    user: ActiveUserDep,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Invalidate all outstanding refresh tokens by incrementing the user's
    refresh token revocation counter in the database.
    """
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.logout(user, ip_address=ip, device=device)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
async def get_current_user_info(
    user: ActiveUserDep,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Return the public representation of the authenticated user's profile,
    including their platform role and contact verification status.
    """
    return await service.get_current_user_profile(user)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change account password",
)
async def change_password(
    req: ChangePasswordRequest,
    user: ActiveUserDep,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Verify the user's current password, validate the new password against OWASP
    complexity criteria, update the bcrypt hash, and revoke all existing sessions.
    """
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.change_password(user, req, ip_address=ip, device=device)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Request a password recovery link",
)
async def forgot_password(
    req: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> ForgotPasswordResponse:
    """
    Initiate password recovery by generating a 32-byte secure random token
    stored in user metadata.
    """
    return await service.forgot_password(req)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password using recovery token",
)
async def reset_password(
    req: ResetPasswordRequest,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Validate the recovery token, check its expiration time, hash the new password,
    clear the recovery token, and revoke previous sessions.
    """
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.reset_password(req, ip_address=ip, device=device)


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify user email address (structure only)",
)
async def verify_email(
    req: VerifyEmailRequest,
    user: ActiveUserDep,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Verify user email address via token (structural implementation).
    """
    return await service.verify_email(user, req)


@router.post(
    "/verify-phone",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify user phone number via SMS OTP (structure only)",
)
async def verify_phone(
    req: VerifyPhoneRequest,
    user: ActiveUserDep,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Verify user phone number via SMS OTP code (structural implementation).
    """
    return await service.verify_phone(user, req)


# =============================================================================
# Phase 3.3 — OTP System Endpoints
# =============================================================================

@router.post(
    "/otp/send",
    response_model=OTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Send an OTP code for registration, login, or verification",
)
async def send_otp(
    req: SendOTPRequest,
    service: AuthService = Depends(get_auth_service),
) -> OTPResponse:
    """Generate, store, and email an OTP verification code."""
    return await service.send_otp(req)


@router.post(
    "/otp/verify",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify an OTP code",
)
async def verify_otp(
    req: VerifyOTPRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Verify a submitted 6-digit OTP code against MongoDB Atlas."""
    return await service.verify_otp(req)


@router.post(
    "/otp/resend",
    response_model=OTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend an OTP verification code",
)
async def resend_otp(
    req: ResendOTPRequest,
    service: AuthService = Depends(get_auth_service),
) -> OTPResponse:
    """Resend an unexpired OTP code or generate a replacement if permitted."""
    return await service.resend_otp(req)


@router.post(
    "/login/otp",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate using identifier and verified OTP code",
)
async def login_with_otp(
    req: OTPLoginRequest,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Authenticate via email/phone and verified LOGIN OTP code."""
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.login_with_otp(req, ip_address=ip, device=device)


# =============================================================================
# Phase 3.3 — Session Management & Audit Endpoints
# =============================================================================

@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List active user sessions",
)
async def list_sessions(
    user: ActiveUserDep,
    service: AuthService = Depends(get_auth_service),
) -> list[SessionResponse]:
    """Retrieve all active (non-revoked) sessions for the authenticated user."""
    return await service.get_active_sessions(user)


@router.post(
    "/sessions/logout-device",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out from a specific device session",
)
async def logout_device(
    req: LogoutDeviceRequest,
    user: ActiveUserDep,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Revoke a specific session by its session_id."""
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.logout(user, session_id=req.session_id, ip_address=ip, device=device)


@router.post(
    "/sessions/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out from all devices",
)
async def logout_all_devices(
    user: ActiveUserDep,
    request: Request,
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Revoke all active sessions and rotate refresh token version."""
    ip, device = _get_ip_and_device(request, user_agent)
    return await service.logout(user, session_id=None, ip_address=ip, device=device)


@router.get(
    "/login-history",
    response_model=list[LoginHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve recent user login history",
)
async def get_login_history(
    user: ActiveUserDep,
    limit: int = 20,
    service: AuthService = Depends(get_auth_service),
) -> list[LoginHistoryResponse]:
    """Return immutable login history for the authenticated user."""
    return await service.get_login_history(user, limit=limit)
