"""
Authentication Security Audit Logging — Ally Service Marketplace.

Records structured audit trail events into MongoDB Atlas via the Admin AuditLog
Beanie Document collection for all critical security actions:
  - User Login (success, failure, lockout)
  - User Logout (single device or global revocation)
  - Registration
  - Password Change & Password Reset
  - OTP Verification (success & failed attempts)
  - Failed Login Attempts
"""

import logging
from datetime import datetime, timezone

from app.admin.models import AuditLog

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Asynchronous audit logging service for authentication and security events.
    """

    @classmethod
    async def _safe_insert(cls, log_entry: AuditLog) -> None:
        """Insert an AuditLog entry without raising exceptions on transient DB errors."""
        try:
            await log_entry.insert()
        except Exception as exc:
            logger.error("Failed to insert security AuditLog entry: %s", exc, exc_info=True)

    @classmethod
    async def log_login(
        cls,
        user_id: str,
        identifier: str,
        ip_address: str | None = None,
        device: str | None = None,
        success: bool = True,
        reason: str | None = None,
    ) -> None:
        """Log a user login attempt."""
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        entry = AuditLog(
            performed_by=user_id or "system",
            action=action,
            module="Auth",
            entity_type="User",
            entity_id=user_id,
            new_data={
                "identifier": identifier,
                "success": success,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)

    @classmethod
    async def log_failed_login(
        cls,
        identifier: str,
        reason: str,
        ip_address: str | None = None,
        device: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Log a failed login attempt or brute force lockout."""
        entry = AuditLog(
            performed_by=user_id or "system",
            action="LOGIN_FAILED",
            module="Auth",
            entity_type="User",
            entity_id=user_id,
            new_data={
                "identifier": identifier,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)

    @classmethod
    async def log_logout(
        cls,
        user_id: str,
        scope: str = "CURRENT_DEVICE",
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a user logout action."""
        entry = AuditLog(
            performed_by=user_id,
            action="LOGOUT",
            module="Auth",
            entity_type="User",
            entity_id=user_id,
            new_data={
                "scope": scope,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)

    @classmethod
    async def log_registration(
        cls,
        user_id: str,
        email: str,
        role: str,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a new account registration."""
        entry = AuditLog(
            performed_by=user_id,
            action="REGISTRATION",
            module="Auth",
            entity_type="User",
            entity_id=user_id,
            new_data={
                "email": email,
                "role": role,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)

    @classmethod
    async def log_password_change(
        cls,
        user_id: str,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a user password change."""
        entry = AuditLog(
            performed_by=user_id,
            action="PASSWORD_CHANGE",
            module="Auth",
            entity_type="User",
            entity_id=user_id,
            new_data={
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)

    @classmethod
    async def log_password_reset(
        cls,
        user_id: str,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a user password reset via recovery token/OTP."""
        entry = AuditLog(
            performed_by=user_id,
            action="PASSWORD_RESET",
            module="Auth",
            entity_type="User",
            entity_id=user_id,
            new_data={
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)

    @classmethod
    async def log_otp_verification(
        cls,
        identifier: str,
        purpose: str,
        success: bool = True,
        user_id: str | None = None,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log an OTP verification attempt."""
        action = "OTP_VERIFICATION_SUCCESS" if success else "OTP_VERIFICATION_FAILED"
        entry = AuditLog(
            performed_by=user_id or "system",
            action=action,
            module="Auth",
            entity_type="OTPRecord",
            entity_id=user_id,
            new_data={
                "identifier": identifier,
                "purpose": purpose,
                "success": success,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ip_address=ip_address,
            device=device,
        )
        await cls._safe_insert(entry)
