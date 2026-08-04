"""
Secure OTP Verification Service — Ally Auth Module (Phase 3.3).

Implements end-to-end OTP lifecycle management:
  - Cryptographically secure 6-digit numeric OTP generation.
  - Bcrypt hashing before storage in MongoDB Atlas (OTPRecord).
  - Configurable TTL expiration (default: 10 minutes = 600 seconds).
  - Rate limiting (60s minimum interval between requests).
  - Max retry attempts (5) and max resend attempts (3).
  - Reuse prevention (is_used flag).
  - Swappable email dispatch via EmailProvider and branded templates.
  - Security audit logging of verification outcomes.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone

from app.auth.audit import AuditLogger
from app.auth.email import get_email_provider, get_otp_email_template
from app.auth.exceptions import (
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxResendsExceededError,
    OTPMaxRetriesExceededError,
    OTPRateLimitError,
)
from app.auth.models import OTPPurpose, OTPRecord
from app.auth.schemas import OTPResponse, ResendOTPRequest, SendOTPRequest, VerifyOTPRequest
from app.auth.security import hash_password, verify_password
from app.auth.utils import ensure_utc

logger = logging.getLogger(__name__)

# Configurable OTP security limits
DEFAULT_OTP_EXPIRES_SECONDS = 600  # 10 minutes
DEFAULT_OTP_RATE_LIMIT_SECONDS = 60  # 1 minute between sends/resends
MAX_OTP_RETRY_ATTEMPTS = 5
MAX_OTP_RESEND_ATTEMPTS = 3


class OTPService:
    """
    Business logic and security invariants for Ally's OTP Verification System.
    """

    @staticmethod
    def _generate_numeric_otp(length: int = 6) -> str:
        """Generate a cryptographically secure numeric OTP string."""
        return "".join(secrets.choice("0123456789") for _ in range(length))

    async def send_otp(self, req: SendOTPRequest) -> OTPResponse:
        """
        Generate, hash, store, and email an OTP code for an email or phone identifier.
        """
        now = datetime.now(timezone.utc)

        # Check rate limiting against existing recent record
        existing = await OTPRecord.find_one(
            OTPRecord.identifier == req.identifier,
            OTPRecord.purpose == req.purpose,
            OTPRecord.is_used == False,
        )
        if existing and (now - ensure_utc(existing.created_at)).total_seconds() < DEFAULT_OTP_RATE_LIMIT_SECONDS:
            raise OTPRateLimitError()

        otp_code = self._generate_numeric_otp(6)
        otp_hash = hash_password(otp_code)
        expires_at = now + timedelta(seconds=DEFAULT_OTP_EXPIRES_SECONDS)

        record = OTPRecord(
            identifier=req.identifier,
            otp_hash=otp_hash,
            purpose=req.purpose,
            expires_at=expires_at,
            retry_count=0,
            resend_count=0,
            is_used=False,
            created_at=now,
        )
        await record.insert()

        # Dispatch transactional email via EmailProvider
        subject, html_body, text_body = get_otp_email_template(
            otp=otp_code,
            purpose=req.purpose,
            expires_in_seconds=DEFAULT_OTP_EXPIRES_SECONDS,
        )
        provider = get_email_provider()
        await provider.send_email(
            to_email=req.identifier,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
        )

        return OTPResponse(
            success=True,
            message=f"OTP sent successfully to {req.identifier}",
            expires_in_seconds=DEFAULT_OTP_EXPIRES_SECONDS,
        )

    async def resend_otp(self, req: ResendOTPRequest) -> OTPResponse:
        """
        Resend an unexpired or replace an OTP code, enforcing resend and rate limits.
        """
        now = datetime.now(timezone.utc)
        record = await OTPRecord.find_one(
            OTPRecord.identifier == req.identifier,
            OTPRecord.purpose == req.purpose,
            OTPRecord.is_used == False,
        )

        if not record:
            # Fall back to sending a new OTP if none exists
            return await self.send_otp(SendOTPRequest(identifier=req.identifier, purpose=req.purpose))

        if record.resend_count >= MAX_OTP_RESEND_ATTEMPTS:
            raise OTPMaxResendsExceededError()

        if (now - ensure_utc(record.created_at)).total_seconds() < DEFAULT_OTP_RATE_LIMIT_SECONDS:
            raise OTPRateLimitError()

        otp_code = self._generate_numeric_otp(6)
        record.otp_hash = hash_password(otp_code)
        record.expires_at = now + timedelta(seconds=DEFAULT_OTP_EXPIRES_SECONDS)
        record.resend_count += 1
        record.created_at = now
        await record.save()

        # Dispatch transactional email
        subject, html_body, text_body = get_otp_email_template(
            otp=otp_code,
            purpose=req.purpose,
            expires_in_seconds=DEFAULT_OTP_EXPIRES_SECONDS,
        )
        provider = get_email_provider()
        await provider.send_email(
            to_email=req.identifier,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
        )

        return OTPResponse(
            success=True,
            message=f"OTP resent successfully to {req.identifier}",
            expires_in_seconds=DEFAULT_OTP_EXPIRES_SECONDS,
        )

    async def verify_otp(self, req: VerifyOTPRequest, mark_used: bool = True) -> OTPRecord:
        """
        Verify a submitted 6-digit OTP code against the bcrypt hash in MongoDB Atlas.

        Enforces:
          - Expiration checks (TTL)
          - Max verification attempts (5)
          - Reuse prevention (is_used)

        Returns:
            The verified OTPRecord.
        """
        now = datetime.now(timezone.utc)
        record = await OTPRecord.find_one(
            OTPRecord.identifier == req.identifier,
            OTPRecord.purpose == req.purpose,
            OTPRecord.is_used == False,
        )

        if not record:
            await AuditLogger.log_otp_verification(req.identifier, req.purpose.value, success=False)
            raise OTPInvalidError(message="No active OTP found for this identifier and purpose")

        if now > ensure_utc(record.expires_at):
            await AuditLogger.log_otp_verification(req.identifier, req.purpose.value, success=False)
            raise OTPExpiredError()

        if record.retry_count >= MAX_OTP_RETRY_ATTEMPTS:
            await AuditLogger.log_otp_verification(req.identifier, req.purpose.value, success=False)
            raise OTPMaxRetriesExceededError()

        if not verify_password(req.otp, record.otp_hash):
            record.retry_count += 1
            await record.save()
            await AuditLogger.log_otp_verification(req.identifier, req.purpose.value, success=False)
            raise OTPInvalidError()

        if mark_used:
            record.is_used = True
            await record.save()

        await AuditLogger.log_otp_verification(req.identifier, req.purpose.value, success=True)
        return record
