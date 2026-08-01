"""
Authentication Service Layer — KaamSetu Service Marketplace.

Orchestrates business rules, OWASP password validation, bcrypt hashing,
JWT token issuance and rotation, domain model persistence, profile creation,
and session revocation.
"""

from datetime import datetime, timedelta, timezone

from app.auth.constants import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_TYPE,
)
from app.auth.exceptions import (
    AccountBlockedError,
    AccountInactiveError,
    AuthenticationError,
    InvalidCredentialsError,
    InvalidTokenError,
    PasswordStrengthError,
    TokenRevokedError,
)
from app.auth.audit import AuditLogger
from app.auth.models import AccountStatus, OTPPurpose, User, UserRole
from app.auth.otp import OTPService
from app.auth.repository import AuthRepository
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
from app.auth.security import (
    TokenPair,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.auth.sessions import SessionService
from app.auth.utils import generate_secure_random_token, validate_password_strength
from app.core.exceptions import ConflictException


class AuthService:
    """
    Service layer containing all authentication, security, OTP, and session business logic.
    """

    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.repository = repository or AuthRepository()
        self.otp_service = OTPService()
        self.session_service = SessionService()

    def _generate_tokens(self, user: User) -> TokenPair:
        """
        Helper method to issue a fresh TokenPair for a user document.
        """
        access_tok = create_access_token(subject=str(user.id), role=user.role)
        refresh_tok = create_refresh_token(
            subject=str(user.id),
            role=user.role,
            version=user.refresh_token_version,
        )
        return TokenPair(
            access_token=access_tok,
            refresh_token=refresh_tok,
            expires_in=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def register(
        self,
        req: UserCreateRequest,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> AuthResponse:
        """
        Register a new user account and create their corresponding role profile.
        """
        existing_email = await self.repository.get_user_by_email(req.email)
        if existing_email:
            raise ConflictException(
                message="An account with this email address already exists",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        existing_phone = await self.repository.get_user_by_phone(req.phone_number)
        if existing_phone:
            raise ConflictException(
                message="An account with this phone number already exists",
                error_code="PHONE_ALREADY_EXISTS",
            )

        failures = validate_password_strength(req.password)
        if failures:
            raise PasswordStrengthError(
                message="Password does not meet security requirements",
                details=failures,
            )

        hashed = hash_password(req.password)

        user = User(
            first_name=req.first_name,
            last_name=req.last_name,
            email=req.email,
            phone_number=req.phone_number,
            password_hash=hashed,
            role=req.role,
            account_status=AccountStatus.ACTIVE,
        )
        created_user = await self.repository.create_user(user)

        if created_user.role == UserRole.WORKER:
            await self.repository.create_worker_profile(str(created_user.id))
        else:
            await self.repository.create_customer_profile(str(created_user.id))

        await AuditLogger.log_registration(
            user_id=str(created_user.id),
            email=created_user.email,
            role=created_user.role.value,
            ip_address=ip_address,
            device=device,
        )

        tokens = self._generate_tokens(created_user)
        return AuthResponse(
            user=UserResponse.model_validate(created_user),
            tokens=tokens,
        )

    async def login(
        self,
        req: LoginRequest,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> AuthResponse:
        """
        Authenticate a user via email address OR phone number, enforce brute force
        protection, record login history, and create an active session.
        """
        user = await self.repository.get_user_by_email_or_phone(req.identifier)

        if user:
            await self.session_service.check_brute_force_lock(user)

        if not user or not verify_password(req.password, user.password_hash):
            await self.session_service.record_failed_login_attempt(
                user=user,
                identifier=req.identifier,
                reason="Invalid credentials",
                ip_address=ip_address,
                device=device,
            )
            raise InvalidCredentialsError(
                message="Invalid email, phone number, or password",
                error_code="INVALID_CREDENTIALS",
            )

        if user.account_status == AccountStatus.INACTIVE:
            await self.session_service.record_failed_login_attempt(
                user=user,
                identifier=req.identifier,
                reason="Account inactive",
                ip_address=ip_address,
                device=device,
            )
            raise AccountInactiveError()
        if user.account_status == AccountStatus.BLOCKED:
            await self.session_service.record_failed_login_attempt(
                user=user,
                identifier=req.identifier,
                reason="Account blocked",
                ip_address=ip_address,
                device=device,
            )
            raise AccountBlockedError()

        user.last_login = datetime.now(timezone.utc)
        await self.repository.update_user(user)

        tokens = self._generate_tokens(user)
        await self.session_service.create_user_session(
            user=user,
            identifier=req.identifier,
            refresh_token_jti=None,
            ip_address=ip_address,
            device=device,
        )

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh_token(self, req: RefreshTokenRequest) -> TokenPair:
        """
        Rotate session tokens by validating the presented refresh token.
        """
        payload = decode_token(req.refresh_token, expected_type=REFRESH_TOKEN_TYPE)

        user = await self.repository.get_user_by_id(payload.sub)
        if not user:
            raise AuthenticationError(
                message="User account no longer exists",
                error_code="USER_NOT_FOUND",
            )

        if payload.ver is None or payload.ver != user.refresh_token_version:
            raise TokenRevokedError(
                message="Refresh token has been revoked or version mismatch",
                error_code="TOKEN_REVOKED",
            )

        if user.account_status != AccountStatus.ACTIVE:
            raise AccountInactiveError()

        return self._generate_tokens(user)

    async def logout(
        self,
        user: User,
        session_id: str | None = None,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> MessageResponse:
        """
        Log out from a specific device session if session_id is provided,
        otherwise invalidate all sessions across all devices.
        """
        if session_id:
            await self.session_service.revoke_session(
                user=user,
                session_id=session_id,
                ip_address=ip_address,
                device=device,
            )
            return MessageResponse(message="Successfully logged out from device")

        await self.session_service.revoke_all_user_sessions(
            user=user,
            ip_address=ip_address,
            device=device,
        )
        return MessageResponse(message="Successfully logged out from all devices")

    async def get_current_user_profile(self, user: User) -> UserResponse:
        """
        Return public user profile for an authenticated request.
        """
        return UserResponse.model_validate(user)

    async def change_password(
        self,
        user: User,
        req: ChangePasswordRequest,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> MessageResponse:
        """
        Verify current password, update password hash, and invalidate all old sessions.
        """
        if not verify_password(req.current_password, user.password_hash):
            raise InvalidCredentialsError(
                message="Current password is incorrect",
                error_code="INVALID_CURRENT_PASSWORD",
            )

        failures = validate_password_strength(req.new_password)
        if failures:
            raise PasswordStrengthError(
                message="New password does not meet security requirements",
                details=failures,
            )

        user.password_hash = hash_password(req.new_password)
        await self.session_service.revoke_all_user_sessions(
            user=user,
            ip_address=ip_address,
            device=device,
        )
        await AuditLogger.log_password_change(
            user_id=str(user.id),
            ip_address=ip_address,
            device=device,
        )

        return MessageResponse(
            message="Password changed successfully. Please log in again with your new password."
        )

    async def forgot_password(self, req: ForgotPasswordRequest) -> ForgotPasswordResponse:
        """
        Initiate password recovery by generating a secure random reset token.
        """
        user = await self.repository.get_user_by_email(req.email)
        if user:
            reset_token = generate_secure_random_token(32)
            expires = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            if not user.metadata:
                user.metadata = {}
            user.metadata["reset_token"] = reset_token
            user.metadata["reset_token_expires"] = expires
            await self.repository.update_user(user)
        else:
            reset_token = "preview_token_for_nonexistent_user"

        return ForgotPasswordResponse(
            message="If an account exists with this email, a password reset link has been sent.",
            reset_token=reset_token,
        )

    async def reset_password(
        self,
        req: ResetPasswordRequest,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> MessageResponse:
        """
        Validate password recovery token, update password, and revoke previous sessions.
        """
        user = await self.repository.get_user_by_reset_token(req.token)
        if not user or not user.metadata or "reset_token" not in user.metadata:
            raise InvalidTokenError(
                message="Password reset token is invalid or has expired",
                error_code="INVALID_RESET_TOKEN",
            )

        expires_str = user.metadata.get("reset_token_expires")
        if expires_str and datetime.fromisoformat(expires_str) < datetime.now(timezone.utc):
            raise InvalidTokenError(
                message="Password reset token has expired",
                error_code="RESET_TOKEN_EXPIRED",
            )

        failures = validate_password_strength(req.new_password)
        if failures:
            raise PasswordStrengthError(
                message="New password does not meet security requirements",
                details=failures,
            )

        user.password_hash = hash_password(req.new_password)
        user.metadata.pop("reset_token", None)
        user.metadata.pop("reset_token_expires", None)
        await self.session_service.revoke_all_user_sessions(
            user=user,
            ip_address=ip_address,
            device=device,
        )
        await AuditLogger.log_password_reset(
            user_id=str(user.id),
            ip_address=ip_address,
            device=device,
        )

        return MessageResponse(
            message="Password reset successfully. You can now log in."
        )

    async def verify_email(self, user: User, req: VerifyEmailRequest) -> MessageResponse:
        """
        Verify user email address.
        """
        user.email_verified = True
        await self.repository.update_user(user)
        return MessageResponse(message="Email address verified successfully")

    async def verify_phone(self, user: User, req: VerifyPhoneRequest) -> MessageResponse:
        """
        Verify user phone number.
        """
        user.phone_verified = True
        await self.repository.update_user(user)
        return MessageResponse(message="Phone number verified successfully")

    # =========================================================================
    # Phase 3.3 — OTP System Service Methods
    # =========================================================================

    async def send_otp(self, req: SendOTPRequest) -> OTPResponse:
        """Send an OTP verification code via EmailProvider."""
        return await self.otp_service.send_otp(req)

    async def verify_otp(self, req: VerifyOTPRequest) -> MessageResponse:
        """
        Verify a 6-digit OTP and update user verification flag if applicable.
        """
        await self.otp_service.verify_otp(req, mark_used=True)

        if req.purpose == OTPPurpose.EMAIL_VERIFY:
            user = await self.repository.get_user_by_email(req.identifier)
            if user:
                user.email_verified = True
                await self.repository.update_user(user)
        elif req.purpose == OTPPurpose.PHONE_VERIFY:
            user = await self.repository.get_user_by_phone(req.identifier)
            if user:
                user.phone_verified = True
                await self.repository.update_user(user)

        return MessageResponse(
            message=f"OTP verified successfully for {req.purpose.value}"
        )

    async def resend_otp(self, req: ResendOTPRequest) -> OTPResponse:
        """Resend an OTP verification code."""
        return await self.otp_service.resend_otp(req)

    async def login_with_otp(
        self,
        req: OTPLoginRequest,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> AuthResponse:
        """
        Authenticate a user using identifier and verified LOGIN OTP code.
        """
        await self.otp_service.verify_otp(
            VerifyOTPRequest(
                identifier=req.identifier,
                otp=req.otp,
                purpose=OTPPurpose.LOGIN,
            ),
            mark_used=True,
        )

        user = await self.repository.get_user_by_email_or_phone(req.identifier)
        if not user:
            raise InvalidCredentialsError(
                message="No account found for this identifier",
                error_code="USER_NOT_FOUND",
            )

        if user.account_status == AccountStatus.INACTIVE:
            raise AccountInactiveError()
        if user.account_status == AccountStatus.BLOCKED:
            raise AccountBlockedError()

        user.last_login = datetime.now(timezone.utc)
        await self.repository.update_user(user)

        tokens = self._generate_tokens(user)
        await self.session_service.create_user_session(
            user=user,
            identifier=req.identifier,
            refresh_token_jti=None,
            ip_address=ip_address,
            device=device,
        )

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    # =========================================================================
    # Phase 3.3 — Session & Login History Service Methods
    # =========================================================================

    async def get_active_sessions(self, user: User) -> list[SessionResponse]:
        """List all active (non-revoked) sessions for the user."""
        sessions = await self.session_service.get_active_sessions(user)
        return [SessionResponse.model_validate(s) for s in sessions]

    async def get_login_history(
        self,
        user: User,
        limit: int = 20,
    ) -> list[LoginHistoryResponse]:
        """Retrieve recent login attempt history for the user."""
        history = await self.session_service.get_login_history(user, limit)
        return [LoginHistoryResponse.model_validate(h) for h in history]
