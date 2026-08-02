"""
Authentication Beanie document models — User, RefreshToken, and AuthAuditLog.

Architecture:
    - User: Central identity document storing credentials, roles, status, and failed login lock state.
    - RefreshToken: Per-device token tracking document for session management, token rotation, and instant revocation.
    - AuthAuditLog: Immutable security audit log collection for auditing all auth actions.
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import Field

from app.utils.enums import UserRole


class User(Document):
    """
    Core identity document for all system users (Customers, Workers, Admins).

    Collection: users
    """

    email: Annotated[str, Indexed(unique=True)]
    phone: Annotated[str, Indexed(unique=True)]
    password_hash: str
    full_name: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    is_email_verified: bool = False
    is_phone_verified: bool = False

    last_login: datetime | None = None
    password_changed_at: datetime | None = None

    # Failed login tracking & account locking
    failed_login_count: int = 0
    locked_until: datetime | None = None
    last_failed_login: datetime | None = None

    password_reset_token: str | None = None
    password_reset_expires_at: datetime | None = None

    email_verification_token: str | None = None
    email_verification_expires_at: datetime | None = None

    phone_verification_code: str | None = None
    phone_verification_expires_at: datetime | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        use_state_management = True

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)


class RefreshToken(Document):
    """
    Refresh token tracking document for multi-device login, rotation, and revocation.

    Collection: refresh_tokens
    """

    user_id: Annotated[PydanticObjectId, Indexed()]
    jti: Annotated[str, Indexed(unique=True)]
    token_hash: str

    device_id: Annotated[str | None, Indexed()] = None
    device_name: str | None = None
    device_type: str | None = None
    operating_system: str | None = None
    browser: str | None = None

    ip_address: str | None = None
    user_agent: str | None = None

    expires_at: Annotated[datetime, Indexed(expireAfterSeconds=0)]
    last_used: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revoked_at: datetime | None = None
    is_revoked: Annotated[bool, Indexed()] = False

    class Settings:
        name = "refresh_tokens"
        use_state_management = True

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)


class AuthAuditLog(Document):
    """
    Audit log document for tracking all authentication events for security compliance.

    Collection: auth_audit_logs
    """

    user_id: Annotated[PydanticObjectId | None, Indexed()] = None
    email: Annotated[str | None, Indexed()] = None
    phone: Annotated[str | None, Indexed()] = None
    action: Annotated[str, Indexed()]  # REGISTER, LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, LOGOUT_ALL, PASSWORD_CHANGE, PASSWORD_RESET, OTP_VERIFIED, OTP_FAILED, ACCOUNT_LOCKED, SESSION_REVOKED, TOKEN_REFRESH, REPLAY_ATTACK_REVOCATION
    status: str = "SUCCESS"  # SUCCESS or FAILURE
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "auth_audit_logs"
        use_state_management = True
