"""
Session Management & Brute Force Protection Service — KaamSetu Auth Module (Phase 3.3).

Implements:
  - Brute Force Account Lockout (5 failed attempts locks account for 15 minutes).
  - Active Session Management (UserSession document tracking).
  - Selective Device Logout (revoking specific session_id).
  - Global Device Logout (incrementing refresh_token_version and revoking all sessions).
  - Immutable Login History Ledger (LoginHistory document tracking).
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.auth.audit import AuditLogger
from app.auth.exceptions import AccountLockedError
from app.auth.models import LoginHistory, LoginStatus, User, UserSession
from app.auth.utils import ensure_utc

logger = logging.getLogger(__name__)

# Configurable security lockout settings
MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCK_MINUTES = 15


class SessionService:
    """
    Manages active user sessions, login audit ledger, and brute force account locking.
    """

    async def check_brute_force_lock(self, user: User) -> None:
        """
        Verify if the user account is temporarily locked due to excessive failed login attempts.
        Raises AccountLockedError if locked.
        Automatically resets lock if the lockout duration has expired.
        """
        now = datetime.now(timezone.utc)
        if user.locked_until:
            if now < ensure_utc(user.locked_until):
                raise AccountLockedError()
            # Lockout period expired; reset counter and lock timestamp
            user.failed_login_attempts = 0
            user.locked_until = None
            await user.save()

    async def record_failed_login_attempt(
        self,
        user: User | None,
        identifier: str,
        reason: str,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """
        Record a failed login attempt in LoginHistory and update user brute force counter.
        Locks the account if MAX_FAILED_LOGIN_ATTEMPTS is reached.
        """
        now = datetime.now(timezone.utc)
        status = LoginStatus.FAILED
        user_id_str = str(user.id) if user else None

        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=ACCOUNT_LOCK_MINUTES)
                status = LoginStatus.LOCKED
                reason = f"Account locked for {ACCOUNT_LOCK_MINUTES} minutes after {user.failed_login_attempts} failed attempts"
            await user.save()

        history_entry = LoginHistory(
            user_id=user_id_str,
            identifier=identifier,
            status=status,
            failure_reason=reason,
            ip_address=ip_address,
            device=device,
            timestamp=now,
        )
        await history_entry.insert()
        await AuditLogger.log_failed_login(
            identifier=identifier,
            reason=reason,
            ip_address=ip_address,
            device=device,
            user_id=user_id_str,
        )

    async def create_user_session(
        self,
        user: User,
        identifier: str,
        refresh_token_jti: str | None = None,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> UserSession:
        """
        Record a successful login, reset failed attempts, create an active UserSession,
        and log to LoginHistory and AuditLog.
        """
        now = datetime.now(timezone.utc)
        if user.failed_login_attempts > 0 or user.locked_until is not None:
            user.failed_login_attempts = 0
            user.locked_until = None
            await user.save()

        session_id = str(uuid.uuid4())
        session = UserSession(
            user_id=str(user.id),
            session_id=session_id,
            refresh_token_jti=refresh_token_jti,
            ip_address=ip_address,
            device=device,
            is_revoked=False,
            last_active=now,
            created_at=now,
        )
        await session.insert()

        history_entry = LoginHistory(
            user_id=str(user.id),
            identifier=identifier,
            status=LoginStatus.SUCCESS,
            failure_reason=None,
            ip_address=ip_address,
            device=device,
            timestamp=now,
        )
        await history_entry.insert()
        await AuditLogger.log_login(
            user_id=str(user.id),
            identifier=identifier,
            ip_address=ip_address,
            device=device,
            success=True,
        )

        return session

    async def revoke_session(
        self,
        user: User,
        session_id: str,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> bool:
        """
        Revoke a specific active session by its session_id (Logout from Current Device).
        Returns True if revoked, False if session not found or already revoked.
        """
        session = await UserSession.find_one(
            UserSession.user_id == str(user.id),
            UserSession.session_id == session_id,
            UserSession.is_revoked == False,
        )
        if not session:
            return False

        session.is_revoked = True
        await session.save()
        await AuditLogger.log_logout(
            user_id=str(user.id),
            scope="CURRENT_DEVICE",
            ip_address=ip_address,
            device=device,
        )
        return True

    async def revoke_all_user_sessions(
        self,
        user: User,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> int:
        """
        Revoke all active sessions for a user (Logout from All Devices).
        Increments user.refresh_token_version to invalidate all issued refresh tokens.
        Returns the number of session documents marked as revoked.
        """
        user.refresh_token_version += 1
        await user.save()

        active_sessions = await UserSession.find(
            UserSession.user_id == str(user.id),
            UserSession.is_revoked == False,
        ).to_list()

        count = 0
        for session in active_sessions:
            session.is_revoked = True
            await session.save()
            count += 1

        await AuditLogger.log_logout(
            user_id=str(user.id),
            scope="ALL_DEVICES",
            ip_address=ip_address,
            device=device,
        )
        return count

    async def get_active_sessions(self, user: User) -> list[UserSession]:
        """Return all non-revoked active sessions for the user."""
        return await UserSession.find(
            UserSession.user_id == str(user.id),
            UserSession.is_revoked == False,
        ).sort("-last_active").to_list()

    async def get_login_history(self, user: User, limit: int = 20) -> list[LoginHistory]:
        """Return the recent login history for the user."""
        return await LoginHistory.find(
            LoginHistory.user_id == str(user.id),
        ).sort("-timestamp").limit(limit).to_list()
