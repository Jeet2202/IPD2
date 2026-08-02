"""
OTP Beanie document model.

Architecture:
    - Dedicated collection storing hashed OTP values for single-use verification.
    - Native MongoDB TTL index on expires_at for auto-purging expired OTP documents.
    - Strict state tracking (attempt_count, resend_count, is_used, verified_at).
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field


class OTP(Document):
    """
    One-Time Password (OTP) tracking document for authentication, verification, and reset flows.

    Collection: otps
    """

    user_id: PydanticObjectId | None = None
    email: Annotated[str | None, Indexed()] = None
    phone: Annotated[str | None, Indexed()] = None

    otp_hash: str
    purpose: Annotated[str, Indexed()]  # registration, login, password_reset, email_verification, phone_verification
    channel: str = "email"  # email or sms

    attempt_count: int = 0
    resend_count: int = 0

    expires_at: Annotated[datetime, Indexed(expireAfterSeconds=0)]
    verified_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    is_used: Annotated[bool, Indexed()] = False

    class Settings:
        name = "otps"
        use_state_management = True

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
