"""
OTP Service — domain logic for OTP generation, hashing, constant-time verification, and rate limiting.

Architecture:
    - Generates cryptographically secure numeric OTP codes using Python's secrets module.
    - Hashes OTP codes prior to database storage (SHA-256) — raw codes are never logged or stored.
    - Uses hmac.compare_digest for constant-time comparison to prevent timing attacks.
    - Enforces attempt limits, resend limits, expiration, and single-use invalidation.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import secrets

from beanie import PydanticObjectId

from app.core.config import settings
from app.core.exceptions import BadRequestException
from app.otp.models import OTP
from app.otp.repository import OTPRepository

logger = logging.getLogger(__name__)


class OTPService:
    """
    Business logic service for managing OTP lifecycle.
    """

    @staticmethod
    def _hash_otp(otp_code: str) -> str:
        """Compute SHA-256 hash of plain OTP string."""
        return hashlib.sha256(otp_code.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def generate_numeric_code(length: int | None = None) -> str:
        """
        Generate a cryptographically secure random numeric OTP string.
        """
        code_length = length or settings.OTP_LENGTH
        # Generate numeric string padded with leading zeros
        max_val = 10**code_length
        random_num = secrets.randbelow(max_val)
        return f"{random_num:0{code_length}d}"

    @staticmethod
    async def generate_otp(
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
        channel: str = "email",
        user_id: PydanticObjectId | str | None = None,
    ) -> tuple[str, OTP]:
        """
        Generate a new hashed OTP document and return the raw code alongside the document.

        Flow:
            1. Invalidate any existing active OTPs for the same purpose & recipient.
            2. Generate secure numeric OTP code.
            3. Compute SHA-256 hash.
            4. Persist OTP document with expiration timestamp.
        """
        if not email and not phone:
            raise BadRequestException(
                message="Recipient email or phone number is required to generate an OTP",
                error_code="IDENTIFIER_REQUIRED",
            )

        # Deactivate previous active OTPs for clean state
        await OTPRepository.cleanup(purpose=purpose, email=email, phone=phone)

        # Generate code & hash
        plain_code = OTPService.generate_numeric_code(settings.OTP_LENGTH)
        otp_hash = OTPService._hash_otp(plain_code)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

        otp_doc = await OTPRepository.create_otp(
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=expires_at,
            channel=channel,
            email=email,
            phone=phone,
            user_id=user_id,
        )

        logger.info(
            "OTP generated successfully | purpose=%s | channel=%s | recipient=%s",
            purpose,
            channel,
            email or phone,
        )

        return plain_code, otp_doc

    @staticmethod
    async def validate_otp(
        otp_code: str,
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> OTP:
        """
        Validate a user-provided OTP code without consuming it.

        OWASP Defenses:
            - Constant-time hash comparison via hmac.compare_digest.
            - Failed attempt counter & lockout.
            - Expiration verification.
        """
        if not email and not phone:
            raise BadRequestException(
                message="Recipient email or phone number is required for verification",
                error_code="IDENTIFIER_REQUIRED",
            )

        otp_doc = await OTPRepository.find_active_otp(purpose=purpose, email=email, phone=phone)

        if otp_doc is None:
            raise BadRequestException(
                message="No active OTP found or code has expired. Please request a new OTP.",
                error_code="OTP_EXPIRED_OR_NOT_FOUND",
            )

        # Check maximum verification attempts limit
        if otp_doc.attempt_count >= settings.OTP_MAX_ATTEMPTS:
            await OTPRepository.mark_used(otp_doc)
            raise BadRequestException(
                message="Maximum verification attempts exceeded. Please request a new OTP.",
                error_code="OTP_MAX_ATTEMPTS_EXCEEDED",
            )

        # Check expiration
        now = datetime.now(timezone.utc)
        exp_at = otp_doc.expires_at if otp_doc.expires_at.tzinfo else otp_doc.expires_at.replace(tzinfo=timezone.utc)
        if exp_at <= now:
            await OTPRepository.mark_used(otp_doc)
            raise BadRequestException(
                message="OTP code has expired. Please request a new OTP.",
                error_code="OTP_EXPIRED",
            )

        # Constant-time comparison
        input_hash = OTPService._hash_otp(otp_code)
        if not hmac.compare_digest(input_hash, otp_doc.otp_hash):
            attempts = await OTPRepository.increment_attempt(otp_doc)
            remaining = settings.OTP_MAX_ATTEMPTS - attempts
            raise BadRequestException(
                message=f"Invalid verification code. {remaining} attempt(s) remaining.",
                error_code="INVALID_OTP",
            )

        # Valid OTP — mark as used immediately for replay protection
        logger.info(
            "OTP validated successfully | purpose=%s | recipient=%s",
            purpose,
            email or phone,
        )
        return otp_doc

    @staticmethod
    async def consume_otp(otp_doc: OTP) -> None:
        """Mark a validated OTP as used so it cannot be replayed."""
        await OTPRepository.mark_used(otp_doc)

    @staticmethod
    async def verify_otp(
        otp_code: str,
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> bool:
        """
        Verify and consume a user-provided OTP code.
        """
        otp_doc = await OTPService.validate_otp(
            otp_code=otp_code,
            purpose=purpose,
            email=email,
            phone=phone,
        )
        await OTPService.consume_otp(otp_doc)
        logger.info(
            "OTP verified successfully | purpose=%s | recipient=%s",
            purpose,
            email or phone,
        )
        return True

    @staticmethod
    async def resend_otp(
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
        channel: str = "email",
        user_id: PydanticObjectId | str | None = None,
    ) -> tuple[str, OTP]:
        """
        Resend an OTP while enforcing resend count limits.
        """
        active_otp = await OTPRepository.find_active_otp(purpose=purpose, email=email, phone=phone)

        if active_otp is not None:
            now = datetime.now(timezone.utc)
            updated_at_tz = active_otp.updated_at if active_otp.updated_at.tzinfo else active_otp.updated_at.replace(tzinfo=timezone.utc)
            elapsed_seconds = (now - updated_at_tz).total_seconds()
            cooldown_seconds = settings.OTP_RESEND_COOLDOWN_SECONDS

            if elapsed_seconds < cooldown_seconds:
                remaining_seconds = int(cooldown_seconds - elapsed_seconds) + 1
                raise BadRequestException(
                    message=f"Please wait {remaining_seconds} seconds before requesting another verification code.",
                    error_code="OTP_RESEND_COOLDOWN",
                )

            if active_otp.resend_count >= settings.OTP_MAX_RESEND:
                raise BadRequestException(
                    message="Maximum OTP resend requests reached. Please try again later.",
                    error_code="OTP_MAX_RESEND_EXCEEDED",
                )

        prev_resend_count = active_otp.resend_count if active_otp else 0

        plain_code, new_otp_doc = await OTPService.generate_otp(
            purpose=purpose,
            email=email,
            phone=phone,
            channel=channel,
            user_id=user_id,
        )

        if prev_resend_count > 0 or active_otp is not None:
            new_otp_doc.resend_count = prev_resend_count + 1
            await new_otp_doc.save()

        return plain_code, new_otp_doc

    @staticmethod
    async def expire_otp(otp_doc: OTP) -> None:
        """Manually expire an OTP document."""
        await OTPRepository.mark_used(otp_doc)

    @staticmethod
    async def cleanup_expired_otps() -> int:
        """Purge expired OTP documents from database."""
        return await OTPRepository.delete_expired()
