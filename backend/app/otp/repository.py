"""
Database repository for OTP operations — pure database layer.

Architecture:
    - Encapsulates queries, insertions, updates, and deletions on OTP documents using Beanie.
    - Zero business logic, zero raw OTP generation, zero email delivery logic.
"""

from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.otp.models import OTP


class OTPRepository:
    """
    Stateless async repository for database operations on OTP documents.
    """

    @staticmethod
    async def create_otp(
        otp_hash: str,
        purpose: str,
        expires_at: datetime,
        channel: str = "email",
        email: str | None = None,
        phone: str | None = None,
        user_id: PydanticObjectId | str | None = None,
    ) -> OTP:
        """Create and persist a new OTP document."""
        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        otp_doc = OTP(
            user_id=user_id,
            email=email.lower().strip() if email else None,
            phone=phone.strip() if phone else None,
            otp_hash=otp_hash,
            purpose=purpose,
            channel=channel,
            expires_at=expires_at,
        )
        await otp_doc.insert()
        return otp_doc

    @staticmethod
    async def find_active_otp(
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> OTP | None:
        """Find the latest active, unused, unexpired OTP matching purpose and recipient."""
        now = datetime.now(timezone.utc)
        query = [
            OTP.purpose == purpose,
            OTP.is_used == False,  # noqa: E712
            OTP.expires_at > now,
        ]

        if email:
            query.append(OTP.email == email.lower().strip())
        elif phone:
            query.append(OTP.phone == phone.strip())

        return await OTP.find(*query).sort("-created_at").first_or_none()

    @staticmethod
    async def find_by_email(email: str, purpose: str) -> list[OTP]:
        """Retrieve all OTP documents for a given email and purpose."""
        return await OTP.find(
            OTP.email == email.lower().strip(),
            OTP.purpose == purpose,
        ).to_list()

    @staticmethod
    async def find_by_phone(phone: str, purpose: str) -> list[OTP]:
        """Retrieve all OTP documents for a given phone and purpose."""
        return await OTP.find(
            OTP.phone == phone.strip(),
            OTP.purpose == purpose,
        ).to_list()

    @staticmethod
    async def increment_attempt(otp_doc: OTP) -> int:
        """Increment failed verification attempt count."""
        otp_doc.attempt_count += 1
        await otp_doc.save()
        return otp_doc.attempt_count

    @staticmethod
    async def increment_resend(otp_doc: OTP) -> int:
        """Increment resend count."""
        otp_doc.resend_count += 1
        await otp_doc.save()
        return otp_doc.resend_count

    @staticmethod
    async def mark_verified(otp_doc: OTP) -> None:
        """Mark OTP as verified."""
        now = datetime.now(timezone.utc)
        otp_doc.verified_at = now
        await otp_doc.save()

    @staticmethod
    async def mark_used(otp_doc: OTP) -> None:
        """Mark OTP as used so it cannot be re-verified (single use enforcement)."""
        now = datetime.now(timezone.utc)
        otp_doc.is_used = True
        if not otp_doc.verified_at:
            otp_doc.verified_at = now
        await otp_doc.save()

    @staticmethod
    async def delete_expired() -> int:
        """Delete all expired OTP documents (supplementing MongoDB TTL index)."""
        now = datetime.now(timezone.utc)
        result = await OTP.find(OTP.expires_at < now).delete()
        return result.deleted_count if result else 0

    @staticmethod
    async def cleanup(
        purpose: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> int:
        """Deactivate or mark previous active OTPs as used to prevent multiple active codes."""
        now = datetime.now(timezone.utc)
        query = [
            OTP.purpose == purpose,
            OTP.is_used == False,  # noqa: E712
        ]
        if email:
            query.append(OTP.email == email.lower().strip())
        elif phone:
            query.append(OTP.phone == phone.strip())

        result = await OTP.find(*query).update(
            {"$set": {"is_used": True, "updated_at": now}}
        )
        return result.modified_count if result else 0
