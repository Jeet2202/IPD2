"""
Authentication service layer — business logic for Registration and Login.

Architecture:
    - Encapsulates domain logic, password verification, duplicate checks,
      profile instantiation, token generation, and rollback handling.
    - Pure async operations using AuthRepository for database access.
    - Constant-time password verification to defend against timing & enumeration attacks.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import logging
from time import perf_counter

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from starlette.background import BackgroundTasks

from app.auth.models import RefreshToken, User
from app.auth.repository import AuthRepository
from app.auth.schemas import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResendEmailOTPRequest,
    ResetPasswordRequest,
    SessionResponse,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
    VerifyPasswordResetOTPRequest,
)
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    TokenExpiredException,
    TokenInvalidException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.email.service import email_service
from app.otp.models import OTP
from app.otp.service import OTPService
from app.utils.enums import TokenType, UserRole

# Dummy bcrypt hash to ensure constant-time verification when user is not found
_DUMMY_BCRYPT_HASH = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQ68YkwS"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _TokenBundle:
    response: TokenResponse
    refresh_jti: str
    refresh_token_hash: str
    refresh_expires_at: datetime


def _elapsed_ms(started_at: float) -> float:
    return (perf_counter() - started_at) * 1000


class AuthService:
    """
    Business logic service for User Registration and Authentication.
    """

    @staticmethod
    async def create_customer_profile(user_id: PydanticObjectId | str) -> None:
        """Helper method to instantiate customer profile."""
        await AuthRepository.create_customer_profile(user_id)

    @staticmethod
    async def create_worker_profile(user_id: PydanticObjectId | str) -> None:
        """Helper method to instantiate worker profile."""
        await AuthRepository.create_worker_profile(user_id)

    @staticmethod
    def _create_token_bundle(user: User) -> _TokenBundle:
        """
        Create JWT access/refresh tokens without mutating database state.
        """
        user_id_str = str(user.id)

        access_token = create_access_token(
            subject=user_id_str,
            extra_claims={
                "role": user.role.value if isinstance(user.role, UserRole) else str(user.role),
                "phone": user.phone,
            },
        )
        refresh_token = create_refresh_token(subject=user_id_str)
        payload = decode_token(refresh_token)
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        exp_datetime = datetime.fromtimestamp(payload.exp, tz=timezone.utc)

        return _TokenBundle(
            response=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            ),
            refresh_jti=payload.jti,
            refresh_token_hash=token_hash,
            refresh_expires_at=exp_datetime,
        )

    @staticmethod
    async def _store_refresh_token_bundle(
        user: User,
        token_bundle: _TokenBundle,
        device_info: dict | None = None,
    ) -> RefreshToken:
        """
        Persist the refresh-token session for an already-created token bundle.
        """
        device_data = device_info or {}

        return await AuthRepository.store_refresh_token(
            user_id=user.id,
            jti=token_bundle.refresh_jti,
            token_hash=token_bundle.refresh_token_hash,
            expires_at=token_bundle.refresh_expires_at,
            device_id=device_data.get("device_id"),
            device_name=device_data.get("device_name"),
            device_type=device_data.get("device_type"),
            operating_system=device_data.get("operating_system"),
            browser=device_data.get("browser"),
            ip_address=device_data.get("ip_address"),
            user_agent=device_data.get("user_agent"),
        )

    @staticmethod
    async def generate_auth_response(
        user: User,
        device_info: dict | None = None,
    ) -> TokenResponse:
        """
        Generate JWT Access & Refresh token pair and persist RefreshToken session.
        """
        token_bundle = AuthService._create_token_bundle(user)
        await AuthService._store_refresh_token_bundle(user, token_bundle, device_info)
        return token_bundle.response

    @staticmethod
    async def _rollback_registration(
        user: User | None,
        role: UserRole,
        otp_doc: OTP | None = None,
        profile_created: bool = False,
    ) -> None:
        """
        Compensate partially-created registration documents.
        """
        rollback_errors: list[str] = []

        if otp_doc is not None:
            try:
                await otp_doc.delete()
            except Exception as exc:
                rollback_errors.append(f"otp:{exc}")

        if user is not None and profile_created:
            try:
                await AuthRepository.delete_profile_for_user(user.id, role)
            except Exception as exc:
                rollback_errors.append(f"profile:{exc}")

        if user is not None:
            try:
                await AuthRepository.delete_user(user)
            except Exception as exc:
                rollback_errors.append(f"user:{exc}")

        if rollback_errors:
            logger.error(
                "Registration rollback had errors | user_id=%s | errors=%s",
                str(user.id) if user and user.id else None,
                rollback_errors,
            )

    @staticmethod
    async def _send_registration_otp_background(
        to_email: str,
        otp_code: str,
        user_name: str | None,
    ) -> None:
        started_at = perf_counter()
        try:
            await email_service.send_registration_otp(
                to_email=to_email,
                otp_code=otp_code,
                user_name=user_name,
            )
            logger.info(
                "Registration OTP email completed | duration_ms=%.2f",
                _elapsed_ms(started_at),
            )
        except Exception:
            logger.exception(
                "Registration OTP email failed | duration_ms=%.2f",
                _elapsed_ms(started_at),
            )

    @staticmethod
    def _queue_registration_otp_email(
        background_tasks: BackgroundTasks | None,
        to_email: str,
        otp_code: str,
        user_name: str | None,
    ) -> str:
        try:
            if background_tasks is not None:
                background_tasks.add_task(
                    AuthService._send_registration_otp_background,
                    to_email=to_email,
                    otp_code=otp_code,
                    user_name=user_name,
                )
            else:
                asyncio.create_task(
                    AuthService._send_registration_otp_background(
                        to_email=to_email,
                        otp_code=otp_code,
                        user_name=user_name,
                    )
                )
            return "queued"
        except Exception:
            logger.exception("Failed to queue registration OTP email")
            return "failed_to_queue"

    @staticmethod
    async def register(
        payload: RegisterRequest,
        background_tasks: BackgroundTasks | None = None,
    ) -> tuple[UserResponse, dict]:
        """
        Register a new User (Customer or Worker) with safe profile and OTP creation.

        Flow:
            1. Validate duplicate email.
            2. Validate duplicate phone.
            3. Hash password.
            4. Insert User document.
            5. Insert 1:1 Profile document (CustomerProfile or WorkerProfile).
            6. Insert OTP document.
            7. Queue registration email after DB state is complete.
        """
        total_started_at = perf_counter()

        duplicate_started_at = perf_counter()
        if await AuthRepository.email_exists(payload.email):
            raise ConflictException(
                message="An account with this email address already exists",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        if await AuthRepository.phone_exists(payload.phone):
            raise ConflictException(
                message="An account with this phone number already exists",
                error_code="PHONE_ALREADY_EXISTS",
            )
        logger.info(
            "Registration duplicate checks completed | duration_ms=%.2f",
            _elapsed_ms(duplicate_started_at),
        )

        hash_started_at = perf_counter()
        hashed_password = hash_password(payload.password)
        full_name = f"{payload.first_name.strip()} {payload.last_name.strip()}".strip()
        logger.info(
            "Registration password hashing completed | duration_ms=%.2f",
            _elapsed_ms(hash_started_at),
        )

        user: User | None = None
        profile_created = False
        otp_doc: OTP | None = None
        plain_otp: str | None = None

        try:
            user_started_at = perf_counter()
            user = await AuthRepository.create_user(
                email=payload.email,
                phone=payload.phone,
                password_hash=hashed_password,
                full_name=full_name,
                role=payload.role,
            )
            logger.info(
                "Registration user insert completed | user_id=%s | duration_ms=%.2f",
                str(user.id),
                _elapsed_ms(user_started_at),
            )

            profile_started_at = perf_counter()
            if payload.role == UserRole.CUSTOMER:
                await AuthService.create_customer_profile(user.id)
            elif payload.role == UserRole.WORKER:
                await AuthService.create_worker_profile(user.id)
            profile_created = True
            logger.info(
                "Registration profile insert completed | user_id=%s | role=%s | duration_ms=%.2f",
                str(user.id),
                payload.role.value,
                _elapsed_ms(profile_started_at),
            )

            otp_started_at = perf_counter()
            plain_otp, otp_doc = await OTPService.generate_otp(
                purpose="registration",
                email=payload.email,
                user_id=user.id,
            )
            logger.info(
                "Registration OTP insert completed | user_id=%s | duration_ms=%.2f",
                str(user.id),
                _elapsed_ms(otp_started_at),
            )
        except DuplicateKeyError as exc:
            await AuthService._rollback_registration(
                user=user,
                role=payload.role,
                otp_doc=otp_doc,
                profile_created=profile_created,
            )
            err_str = str(exc)
            if "phone" in err_str:
                raise ConflictException(
                    message="An account with this phone number already exists",
                    error_code="PHONE_ALREADY_EXISTS",
                )
            raise ConflictException(
                message="An account with this email address already exists",
                error_code="EMAIL_ALREADY_EXISTS",
            )
        except Exception as exc:
            await AuthService._rollback_registration(
                user=user,
                role=payload.role,
                otp_doc=otp_doc,
                profile_created=profile_created,
            )
            raise AppException(
                message="Failed to complete registration safely",
                error_code="REGISTRATION_FAILED",
                status_code=500,
                details=[str(exc)],
            )

        email_started_at = perf_counter()
        email_delivery_status = AuthService._queue_registration_otp_email(
            background_tasks=background_tasks,
            to_email=payload.email,
            otp_code=plain_otp,
            user_name=user.full_name,
        )
        logger.info(
            "Registration email scheduling completed | user_id=%s | status=%s | duration_ms=%.2f",
            str(user.id),
            email_delivery_status,
            _elapsed_ms(email_started_at),
        )

        user_response = AuthService._to_user_response(user)
        info = {
            "message": "Account registered successfully. An OTP verification code has been queued for email delivery.",
            "email": user.email,
            "registration_status": "pending_email_verification",
            "email_delivery_status": email_delivery_status,
        }
        logger.info(
            "Registration request completed | user_id=%s | status=%s | duration_ms=%.2f",
            str(user.id),
            info["registration_status"],
            _elapsed_ms(total_started_at),
        )

        return user_response, info

    @staticmethod
    async def verify_email(payload: VerifyEmailRequest) -> tuple[UserResponse, TokenResponse]:
        """
        Verify user email address using OTP and issue initial authentication tokens.
        """
        total_started_at = perf_counter()

        user_started_at = perf_counter()
        user = await AuthRepository.find_user_by_email(payload.email)
        if user is None:
            raise UnauthorizedException(message="User account associated with this email address was not found")
        logger.info(
            "Email verification user lookup completed | user_id=%s | duration_ms=%.2f",
            str(user.id),
            _elapsed_ms(user_started_at),
        )

        otp_started_at = perf_counter()
        otp_doc = await OTPService.validate_otp(
            otp_code=payload.code,
            purpose="registration",
            email=payload.email,
        )
        logger.info(
            "Email verification OTP validation completed | user_id=%s | duration_ms=%.2f",
            str(user.id),
            _elapsed_ms(otp_started_at),
        )

        token_started_at = perf_counter()
        try:
            token_bundle = AuthService._create_token_bundle(user)
        except Exception as exc:
            raise AppException(
                message="Failed to create authentication tokens",
                error_code="TOKEN_CREATION_FAILED",
                status_code=500,
                details=[str(exc)],
            )
        logger.info(
            "Email verification token creation completed | user_id=%s | duration_ms=%.2f",
            str(user.id),
            _elapsed_ms(token_started_at),
        )

        was_email_verified = user.is_email_verified
        refresh_token_doc: RefreshToken | None = None

        try:
            verify_started_at = perf_counter()
            await AuthRepository.update_email_verification(user, True)
            logger.info(
                "Email verification user update completed | user_id=%s | duration_ms=%.2f",
                str(user.id),
                _elapsed_ms(verify_started_at),
            )

            refresh_started_at = perf_counter()
            refresh_token_doc = await AuthService._store_refresh_token_bundle(
                user,
                token_bundle,
            )
            logger.info(
                "Email verification refresh token storage completed | user_id=%s | jti=%s | duration_ms=%.2f",
                str(user.id),
                token_bundle.refresh_jti,
                _elapsed_ms(refresh_started_at),
            )

            consume_started_at = perf_counter()
            await OTPService.consume_otp(otp_doc)
            logger.info(
                "Email verification OTP consumption completed | user_id=%s | duration_ms=%.2f",
                str(user.id),
                _elapsed_ms(consume_started_at),
            )
        except Exception as exc:
            compensation_errors: list[str] = []

            if refresh_token_doc is not None:
                try:
                    await AuthRepository.revoke_refresh_token(refresh_token_doc)
                except Exception as rollback_exc:
                    compensation_errors.append(f"refresh_token:{rollback_exc}")

            if not was_email_verified:
                try:
                    await AuthRepository.update_email_verification(user, False)
                except Exception as rollback_exc:
                    compensation_errors.append(f"user_verification:{rollback_exc}")

            if compensation_errors:
                logger.error(
                    "Email verification compensation had errors | user_id=%s | errors=%s",
                    str(user.id),
                    compensation_errors,
                )

            raise AppException(
                message="Email verification could not be completed safely",
                error_code="EMAIL_VERIFICATION_FAILED",
                status_code=500,
                details=[str(exc)],
            )

        user_response = AuthService._to_user_response(user)
        logger.info(
            "Email verification completed | user_id=%s | duration_ms=%.2f",
            str(user.id),
            _elapsed_ms(total_started_at),
        )

        return user_response, token_bundle.response

    @staticmethod
    async def _send_otp_email_background(
        purpose: str,
        to_email: str,
        otp_code: str,
        user_name: str | None,
    ) -> None:
        started_at = perf_counter()
        try:
            if purpose == "registration":
                await email_service.send_registration_otp(to_email, otp_code, user_name)
            elif purpose == "login":
                await email_service.send_login_otp(to_email, otp_code, user_name)
            elif purpose == "password_reset":
                await email_service.send_password_reset_otp(to_email, otp_code, user_name)
            else:
                await email_service.send_email_verification_otp(to_email, otp_code, user_name)
            logger.info(
                "OTP email completed | purpose=%s | duration_ms=%.2f",
                purpose,
                _elapsed_ms(started_at),
            )
        except Exception:
            logger.exception(
                "OTP email failed | purpose=%s | duration_ms=%.2f",
                purpose,
                _elapsed_ms(started_at),
            )

    @staticmethod
    def _queue_otp_email(
        background_tasks: BackgroundTasks | None,
        purpose: str,
        to_email: str,
        otp_code: str,
        user_name: str | None,
    ) -> str:
        try:
            if background_tasks is not None:
                background_tasks.add_task(
                    AuthService._send_otp_email_background,
                    purpose=purpose,
                    to_email=to_email,
                    otp_code=otp_code,
                    user_name=user_name,
                )
            else:
                asyncio.create_task(
                    AuthService._send_otp_email_background(
                        purpose=purpose,
                        to_email=to_email,
                        otp_code=otp_code,
                        user_name=user_name,
                    )
                )
            return "queued"
        except Exception:
            logger.exception("Failed to queue OTP email")
            return "failed_to_queue"

    @staticmethod
    async def resend_email_otp(
        payload: ResendEmailOTPRequest,
        background_tasks: BackgroundTasks | None = None,
    ) -> dict:
        """
        Resend active OTP to user's email address while enforcing resend limit policies.
        """
        user = await AuthRepository.find_user_by_email(payload.email)

        if user and payload.purpose == "registration" and user.is_email_verified:
            return {"message": "Email address is already verified. You may log in directly."}

        plain_otp, _ = await OTPService.resend_otp(
            purpose=payload.purpose,
            email=payload.email,
            user_id=user.id if user else None,
        )

        user_name = user.full_name if user else None
        AuthService._queue_otp_email(
            background_tasks=background_tasks,
            purpose=payload.purpose,
            to_email=payload.email,
            otp_code=plain_otp,
            user_name=user_name,
        )

        return {"message": f"A new verification OTP code has been sent to {payload.email}."}

    @staticmethod
    async def login(
        payload: LoginRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[UserResponse, TokenResponse]:
        """
        Authenticate user using Email OR Phone with password verification and token issuance.

        OWASP Defenses:
            - Account lockout on 5 failed password attempts.
            - Constant-time verification against timing attacks.
            - Generic error message to prevent account enumeration.
            - Deactivated account restriction.
            - Unverified email restriction.
        """
        # 1. Determine identifier & query user
        user: User | None = None
        if payload.email:
            user = await AuthRepository.find_user_by_email(payload.email)
        elif payload.phone:
            user = await AuthRepository.find_user_by_phone(payload.phone)
        else:
            raise BadRequestException(
                message="Either email or phone must be provided for login",
                error_code="MISSING_LOGIN_IDENTIFIER",
            )

        # 2. Check temporary account lock status
        now = datetime.now(timezone.utc)
        if user and user.locked_until:
            locked_until_tz = user.locked_until if user.locked_until.tzinfo else user.locked_until.replace(tzinfo=timezone.utc)
            if locked_until_tz > now:
                remaining_minutes = int((locked_until_tz - now).total_seconds() // 60) + 1
                await AuthRepository.log_audit_event(
                    action="LOGIN_FAILED",
                    status="FAILURE",
                    user_id=user.id,
                    email=user.email,
                    phone=user.phone,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "ACCOUNT_LOCKED", "remaining_minutes": remaining_minutes},
                )
                raise ForbiddenException(
                    message=f"Account is temporarily locked due to multiple failed login attempts. Please try again in {remaining_minutes} minute(s).",
                    error_code="ACCOUNT_LOCKED",
                )
            else:
                # Lock period expired — unlock account
                await AuthRepository.reset_failed_login(user)

        # 3. Password verification
        if user is None:
            verify_password(payload.password, _DUMMY_BCRYPT_HASH)
            await AuthRepository.log_audit_event(
                action="LOGIN_FAILED",
                status="FAILURE",
                email=payload.email,
                phone=payload.phone,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "USER_NOT_FOUND"},
            )
            raise UnauthorizedException(
                message="Invalid credentials",
                error_code="INVALID_CREDENTIALS",
            )

        if not verify_password(payload.password, user.password_hash):
            failed_count, locked_until = await AuthRepository.record_failed_login(user)
            await AuthRepository.log_audit_event(
                action="ACCOUNT_LOCKED" if locked_until else "LOGIN_FAILED",
                status="FAILURE",
                user_id=user.id,
                email=user.email,
                phone=user.phone,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"failed_count": failed_count, "locked": locked_until is not None},
            )
            if locked_until:
                raise ForbiddenException(
                    message=f"Account locked due to {settings.LOGIN_MAX_ATTEMPTS} consecutive failed login attempts. Please try again in {settings.ACCOUNT_LOCK_DURATION_MINUTES} minutes.",
                    error_code="ACCOUNT_LOCKED",
                )
            raise UnauthorizedException(
                message="Invalid credentials",
                error_code="INVALID_CREDENTIALS",
            )

        # 4. Check active status
        if not user.is_active:
            await AuthRepository.log_audit_event(
                action="LOGIN_FAILED",
                status="FAILURE",
                user_id=user.id,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "ACCOUNT_DEACTIVATED"},
            )
            raise ForbiddenException(
                message="Your account has been deactivated. Please contact support.",
                error_code="ACCOUNT_DEACTIVATED",
            )

        # 5. Check email verification status
        if not user.is_email_verified:
            await AuthRepository.log_audit_event(
                action="LOGIN_FAILED",
                status="FAILURE",
                user_id=user.id,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "EMAIL_NOT_VERIFIED"},
            )
            raise ForbiddenException(
                message="Email address is not verified. Please verify your email before logging in.",
                error_code="EMAIL_NOT_VERIFIED",
            )

        # 6. Strict Role Validation (Cross-Role Login Defense)
        if payload.role and user.role != payload.role:
            role_display = user.role.value.capitalize()
            await AuthRepository.log_audit_event(
                action="LOGIN_FAILED",
                status="FAILURE",
                user_id=user.id,
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "INVALID_ROLE_LOGIN", "requested_role": payload.role.value, "actual_role": user.role.value},
            )
            raise ForbiddenException(
                message=f"This account is registered as a {role_display}. Please use the {role_display} Login.",
                error_code="INVALID_ROLE_LOGIN",
            )

        # 6. Update last_login timestamp & reset failed login count
        await AuthRepository.update_last_login(user)

        # 7. Audit log & issue tokens
        await AuthRepository.log_audit_event(
            action="LOGIN_SUCCESS",
            status="SUCCESS",
            user_id=user.id,
            email=user.email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        device_info = {
            "device_id": payload.device_id,
            "device_name": payload.device_name,
            "device_type": payload.device_type,
            "operating_system": payload.operating_system,
            "browser": payload.browser,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        tokens = await AuthService.generate_auth_response(user, device_info=device_info)
        user_response = AuthService._to_user_response(user)

        return user_response, tokens

    @staticmethod
    def _to_user_response(user: User) -> UserResponse:
        """Map User document to public UserResponse DTO."""
        return UserResponse(
            id=str(user.id),
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            account_status="active" if user.is_active else "deactivated",
            verification_status={
                "email": user.is_email_verified,
                "phone": user.is_phone_verified,
            },
            profile_status="complete",
            last_login=user.last_login,
            created_at=user.created_at,
        )

    @staticmethod
    async def refresh_tokens(payload: RefreshTokenRequest) -> TokenResponse:
        """
        Validate and rotate refresh token session.

        Flow:
            1. Decode JWT.
            2. Validate token type is refresh.
            3. Find session in DB by JTI.
            4. Detect Token Reuse (Replay Attack Defense): if token is already revoked,
               revoke ALL sessions for the user to mitigate compromise.
            5. Verify expiration.
            6. Rotate session (revoke old token, create & return new token pair).
        """
        raw_token = payload.refresh_token.strip()

        # 1. Decode token
        decoded = decode_token(raw_token)

        # 2. Verify type
        if decoded.type != TokenType.REFRESH.value:
            raise TokenInvalidException(message="Provided token is not a refresh token")

        # 3. Query token document
        token_doc = await AuthRepository.find_refresh_token_by_jti(decoded.jti)

        # 4. Token Reuse / Replay Attack Security Defense
        if token_doc is not None and token_doc.is_revoked:
            await AuthRepository.revoke_all_refresh_tokens(token_doc.user_id)
            raise TokenInvalidException(
                message="Security alert: Token reuse detected. All active sessions have been revoked."
            )

        if token_doc is None:
            raise TokenInvalidException(message="Refresh token session not found")

        # Verify raw refresh token SHA-256 hash against stored token_hash
        input_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(input_hash, token_doc.token_hash):
            raise TokenInvalidException(message="Invalid or modified refresh token")

        # 5. Check expiration
        now = datetime.now(timezone.utc)
        exp_at = token_doc.expires_at if token_doc.expires_at.tzinfo else token_doc.expires_at.replace(tzinfo=timezone.utc)
        if exp_at <= now:
            raise TokenExpiredException(message="Refresh token has expired. Please log in again.")

        # 6. Verify user active status
        user = await AuthRepository.find_user_by_id(token_doc.user_id)
        if user is None or not user.is_active:
            raise ForbiddenException(
                message="User account associated with this session is inactive or no longer exists"
            )

        # 7. Rotate token session (revoke previous, issue new pair)
        await AuthRepository.revoke_refresh_token(token_doc)

        device_info = {
            "device_id": payload.device_id or token_doc.device_id,
            "device_name": payload.device_name or token_doc.device_name,
            "device_type": payload.device_type or token_doc.device_type,
            "operating_system": payload.operating_system or token_doc.operating_system,
            "browser": payload.browser or token_doc.browser,
        }

        return await AuthService.generate_auth_response(user, device_info=device_info)

    @staticmethod
    async def logout(refresh_token_str: str) -> None:
        """
        Invalidate a single refresh token session for the current device.
        """
        try:
            decoded = decode_token(refresh_token_str.strip())
            token_doc = await AuthRepository.find_refresh_token_by_jti(decoded.jti)
            if token_doc and not token_doc.is_revoked:
                await AuthRepository.revoke_refresh_token(token_doc)
        except Exception:
            # Silent fallback — logout should succeed cleanly even if token is already expired
            pass

    @staticmethod
    async def logout_all(user_id: PydanticObjectId | str) -> int:
        """
        Revoke all active refresh token sessions for a user across all devices.
        """
        return await AuthRepository.revoke_all_refresh_tokens(user_id)

    @staticmethod
    async def change_password(
        user_id: PydanticObjectId | str,
        payload: ChangePasswordRequest,
    ) -> None:
        """
        Change user password and invalidate all active sessions across all devices.
        """
        user = await AuthRepository.find_user_by_id(user_id)
        if user is None:
            raise UnauthorizedException(message="User account not found")

        # Verify current password
        if not verify_password(payload.current_password, user.password_hash):
            raise UnauthorizedException(
                message="Current password is incorrect",
                error_code="INVALID_CURRENT_PASSWORD",
            )

        # Hash new password & update
        new_hash = hash_password(payload.new_password)
        await AuthRepository.update_password_hash(user, new_hash)

        # Invalidate all active sessions to enforce fresh login
        await AuthRepository.revoke_all_refresh_tokens(user.id)

    @staticmethod
    async def forgot_password(
        payload: ForgotPasswordRequest,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        """
        Generate password reset OTP and email it to the user.

        OWASP Defense:
            Always returns generic success message to prevent email enumeration.
        """
        user = await AuthRepository.find_user_by_email(payload.email)
        if user is not None and user.is_active:
            plain_otp, _ = await OTPService.generate_otp(
                purpose="password_reset",
                email=payload.email,
                user_id=user.id,
            )
            AuthService._queue_otp_email(
                background_tasks=background_tasks,
                purpose="password_reset",
                to_email=payload.email,
                otp_code=plain_otp,
                user_name=user.full_name,
            )

    @staticmethod
    async def verify_password_reset_otp(payload: VerifyPasswordResetOTPRequest) -> dict:
        """
        Verify password reset OTP and generate temporary reset token for authorization.
        """
        await OTPService.verify_otp(
            otp_code=payload.otp_code,
            purpose="password_reset",
            email=payload.email,
        )

        user = await AuthRepository.find_user_by_email(payload.email)
        if user is None:
            raise UnauthorizedException(message="User account associated with this email address was not found")

        import secrets
        from datetime import timedelta

        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        await AuthRepository.store_password_reset_token(user, reset_token, expires_at)

        return {
            "reset_token": reset_token,
            "message": "OTP verified successfully. Use the provided reset token to set your new password.",
        }

    @staticmethod
    async def reset_password(payload: ResetPasswordRequest) -> None:
        """
        Apply new password via reset token and invalidate all active user sessions.
        """
        token = payload.token.strip()
        user = await AuthRepository.find_user_by_reset_token(token)
        now = datetime.now(timezone.utc)

        exp_at = None
        if user and user.password_reset_expires_at:
            exp_at = user.password_reset_expires_at if user.password_reset_expires_at.tzinfo else user.password_reset_expires_at.replace(tzinfo=timezone.utc)

        if user is None or exp_at is None or exp_at <= now:
            raise BadRequestException(
                message="Invalid or expired password reset token",
                error_code="INVALID_RESET_TOKEN",
            )

        new_hash = hash_password(payload.new_password)
        await AuthRepository.update_password_hash(user, new_hash)
        await AuthRepository.revoke_all_refresh_tokens(user.id)

    @staticmethod
    async def get_current_user_profile(user_id: PydanticObjectId | str) -> UserResponse:
        """
        Retrieve UserResponse DTO for current user.
        """
        user = await AuthRepository.find_user_by_id(user_id)
        if user is None:
            raise UnauthorizedException(message="User account not found")

        return AuthService._to_user_response(user)

    @staticmethod
    async def get_active_sessions(
        user_id: PydanticObjectId | str,
        current_jti: str | None = None,
    ) -> list[SessionResponse]:
        """
        Retrieve active device sessions for authenticated user.
        """
        sessions = await AuthRepository.get_active_user_sessions(user_id)
        result: list[SessionResponse] = []

        for s in sessions:
            result.append(
                SessionResponse(
                    id=str(s.id),
                    jti=s.jti,
                    device_id=s.device_id,
                    device_name=s.device_name,
                    device_type=s.device_type,
                    operating_system=s.operating_system,
                    browser=s.browser,
                    ip_address=s.ip_address,
                    last_used=s.last_used,
                    created_at=s.created_at,
                    is_current=(s.jti == current_jti) if current_jti else False,
                )
            )
        return result

    @staticmethod
    async def revoke_session(
        user_id: PydanticObjectId | str,
        session_id_or_jti: str,
    ) -> bool:
        """
        Revoke a specific active device session by session ID or JTI.
        """
        success = await AuthRepository.revoke_session_by_id(user_id, session_id_or_jti)
        if not success:
            raise BadRequestException(
                message="Session not found or already revoked",
                error_code="SESSION_NOT_FOUND",
            )
        await AuthRepository.log_audit_event(
            action="SESSION_REVOKED",
            status="SUCCESS",
            user_id=user_id,
            details={"revoked_session": session_id_or_jti},
        )
        return True

    @staticmethod
    async def delete_account(
        user_id: PydanticObjectId | str,
        payload: DeleteAccountRequest,
    ) -> None:
        """
        Delete user account and all associated profile, session, and Cloudinary image assets.
        Requires valid current password confirmation.
        """
        user = await AuthRepository.find_user_by_id(user_id)
        if user is None:
            raise UnauthorizedException(message="User account not found")

        if not verify_password(payload.password, user.password_hash):
            raise BadRequestException(
                message="Invalid password. Account deletion requires valid password confirmation.",
                error_code="INVALID_PASSWORD",
            )

        # 1. Clean up Cloudinary Profile Photo & Delete Profile Document
        if user.role == UserRole.CUSTOMER:
            from app.customer.models import CustomerProfile
            profile = await CustomerProfile.find_one(CustomerProfile.user_id == user.id)
            if profile:
                if profile.profile_photo_public_id:
                    from app.uploads.service import CloudinaryService
                    CloudinaryService.delete_image(profile.profile_photo_public_id)
                await profile.delete()
        elif user.role == UserRole.WORKER:
            from app.worker.models import WorkerProfile
            profile = await WorkerProfile.find_one(WorkerProfile.user_id == user.id)
            if profile:
                if profile.profile_photo_public_id:
                    from app.uploads.service import CloudinaryService
                    CloudinaryService.delete_image(profile.profile_photo_public_id)
                await profile.delete()

        # 2. Revoke & delete all refresh tokens
        await AuthRepository.revoke_all_refresh_tokens(user.id)

        # 3. Log audit event & delete user document
        await AuthRepository.log_audit_event(
            action="ACCOUNT_DELETED",
            status="SUCCESS",
            user_id=user.id,
            details={"email": user.email, "role": user.role.value},
        )
        await user.delete()
