"""
Database repository for authentication entities — User and RefreshToken.

Architecture:
    - Pure database access layer utilizing Beanie ODM async operations.
    - Encapsulates queries, updates, indexing helpers, and atomic operations.
    - Zero business logic, zero password hashing, zero JWT generation, zero request validation.
"""

from datetime import datetime, timedelta, timezone

from beanie import PydanticObjectId
from beanie.operators import In, Set

from app.auth.models import AuthAuditLog, RefreshToken, User
from app.core.config import settings
from app.utils.enums import UserRole


class AuthRepository:
    """
    Stateless async repository for database operations on User and RefreshToken documents.
    """

    # ---------------------------------------------------------------------------
    # User Queries & Operations
    # ---------------------------------------------------------------------------

    @staticmethod
    async def create_user(
        email: str,
        phone: str,
        password_hash: str,
        full_name: str,
        role: UserRole = UserRole.CUSTOMER,
    ) -> User:
        """Create and persist a new User document."""
        user = User(
            email=email.lower().strip(),
            phone=phone.strip(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role=role,
        )
        await user.insert()
        return user

    @staticmethod
    async def delete_user(user: User) -> None:
        """Delete a User document (used for registration rollback)."""
        await user.delete()

    @staticmethod
    async def create_customer_profile(user_id: PydanticObjectId | str) -> None:
        """Create a 1:1 CustomerProfile document linked to a user."""
        from app.customer.models import CustomerProfile

        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        profile = CustomerProfile(user_id=user_id)
        await profile.insert()

    @staticmethod
    async def create_worker_profile(user_id: PydanticObjectId | str) -> None:
        """Create a 1:1 WorkerProfile document linked to a user."""
        from app.worker.models import WorkerProfile

        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        profile = WorkerProfile(user_id=user_id)
        await profile.insert()

    @staticmethod
    async def delete_profile_for_user(
        user_id: PydanticObjectId | str,
        role: UserRole,
    ) -> bool:
        """Delete a user's role profile during registration compensation."""
        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        profile = None
        if role == UserRole.CUSTOMER:
            from app.customer.models import CustomerProfile

            profile = await CustomerProfile.find_one(CustomerProfile.user_id == user_id)
        elif role == UserRole.WORKER:
            from app.worker.models import WorkerProfile

            profile = await WorkerProfile.find_one(WorkerProfile.user_id == user_id)

        if profile is None:
            return False

        await profile.delete()
        return True

    @staticmethod
    async def find_user_by_email(email: str) -> User | None:
        """Find a User document by exact email address (case-insensitive)."""
        return await User.find_one(User.email == email.lower().strip())

    @staticmethod
    async def find_user_by_phone(phone: str) -> User | None:
        """Find a User document by phone number."""
        return await User.find_one(User.phone == phone.strip())

    @staticmethod
    async def find_user_by_id(user_id: str | PydanticObjectId) -> User | None:
        """Find a User document by MongoDB ObjectId."""
        if isinstance(user_id, str):
            try:
                user_id = PydanticObjectId(user_id)
            except Exception:
                return None
        return await User.get(user_id)

    @staticmethod
    async def email_exists(email: str) -> bool:
        """Check if an email address already exists in the users collection."""
        user = await AuthRepository.find_user_by_email(email)
        return user is not None

    @staticmethod
    async def phone_exists(phone: str) -> bool:
        """Check if a phone number already exists in the users collection."""
        user = await AuthRepository.find_user_by_phone(phone)
        return user is not None

    @staticmethod
    async def update_last_login(user: User) -> None:
        """Update the last_login timestamp and reset failed login attempts."""
        user.last_login = datetime.now(timezone.utc)
        user.failed_login_count = 0
        user.locked_until = None
        await user.save()

    @staticmethod
    async def record_failed_login(user: User) -> tuple[int, datetime | None]:
        """
        Record a failed login attempt and lock the account if max attempts are reached.
        """
        now = datetime.now(timezone.utc)
        user.failed_login_count += 1
        user.last_failed_login = now

        if user.failed_login_count >= settings.LOGIN_MAX_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.ACCOUNT_LOCK_DURATION_MINUTES)

        await user.save()
        return user.failed_login_count, user.locked_until

    @staticmethod
    async def reset_failed_login(user: User) -> None:
        """Reset failed login count and clear locked_until timestamp."""
        user.failed_login_count = 0
        user.locked_until = None
        await user.save()

    @staticmethod
    async def log_audit_event(
        action: str,
        status: str = "SUCCESS",
        user_id: PydanticObjectId | str | None = None,
        email: str | None = None,
        phone: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> AuthAuditLog:
        """Record an authentication security event in auth_audit_logs collection."""
        if isinstance(user_id, str):
            try:
                user_id = PydanticObjectId(user_id)
            except Exception:
                user_id = None

        log_entry = AuthAuditLog(
            user_id=user_id,
            email=email,
            phone=phone,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        await log_entry.insert()
        return log_entry

    @staticmethod
    async def store_password_reset_token(user: User, token: str, expires_at: datetime) -> None:
        """Store password reset token and expiration on User document."""
        user.password_reset_token = token
        user.password_reset_expires_at = expires_at
        await user.save()

    @staticmethod
    async def find_user_by_reset_token(token: str) -> User | None:
        """Find User by active password reset token."""
        return await User.find_one(User.password_reset_token == token)

    @staticmethod
    async def update_password_hash(user: User, new_password_hash: str) -> None:
        """Update a user's password hash and record the change timestamp."""
        now = datetime.now(timezone.utc)
        user.password_hash = new_password_hash
        user.password_changed_at = now
        user.password_reset_token = None
        user.password_reset_expires_at = None
        await user.save()

    @staticmethod
    async def update_email_verification(user: User, is_verified: bool = True) -> None:
        """Update email verification status for a user."""
        user.is_email_verified = is_verified
        if is_verified:
            user.email_verification_token = None
            user.email_verification_expires_at = None
        await user.save()

    @staticmethod
    async def update_phone_verification(user: User, is_verified: bool = True) -> None:
        """Update phone verification status for a user."""
        user.is_phone_verified = is_verified
        if is_verified:
            user.phone_verification_code = None
            user.phone_verification_expires_at = None
        await user.save()

    # ---------------------------------------------------------------------------
    # RefreshToken Queries & Operations
    # ---------------------------------------------------------------------------

    @staticmethod
    async def store_refresh_token(
        user_id: PydanticObjectId | str,
        jti: str,
        token_hash: str,
        expires_at: datetime,
        device_id: str | None = None,
        device_name: str | None = None,
        device_type: str | None = None,
        operating_system: str | None = None,
        browser: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> RefreshToken:
        """Store a new refresh token session document in MongoDB."""
        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        # Enforce maximum concurrent active sessions limit per user
        await AuthRepository.enforce_max_sessions(user_id)

        token_doc = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at,
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            operating_system=operating_system,
            browser=browser,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await token_doc.insert()
        return token_doc

    @staticmethod
    async def get_active_user_sessions(user_id: PydanticObjectId | str) -> list[RefreshToken]:
        """Retrieve all active (unexpired, unrevoked) refresh token session documents for a user."""
        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        now = datetime.now(timezone.utc)
        return await RefreshToken.find(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,  # noqa: E712
            RefreshToken.expires_at > now,
        ).sort("-created_at").to_list()

    @staticmethod
    async def enforce_max_sessions(
        user_id: PydanticObjectId | str,
        max_sessions: int = settings.MAX_ACTIVE_SESSIONS,
    ) -> int:
        """
        Enforce max concurrent active sessions per user by revoking oldest sessions.
        """
        active_sessions = await AuthRepository.get_active_user_sessions(user_id)
        if len(active_sessions) < max_sessions:
            return 0

        # Sort by creation time ascending (oldest first)
        active_sessions.sort(key=lambda s: s.created_at)
        excess_count = len(active_sessions) - max_sessions + 1  # make room for new session

        revoked_count = 0
        for old_session in active_sessions[:excess_count]:
            await AuthRepository.revoke_refresh_token(old_session)
            revoked_count += 1

        return revoked_count

    @staticmethod
    async def revoke_session_by_id(
        user_id: PydanticObjectId | str,
        session_id_or_jti: str,
    ) -> bool:
        """Revoke a specific user session document by ID or JTI."""
        session = await AuthRepository.find_refresh_token(session_id_or_jti)
        if session is None or str(session.user_id) != str(user_id):
            return False

        if not session.is_revoked:
            await AuthRepository.revoke_refresh_token(session)
            return True
        return False

    @staticmethod
    async def find_refresh_token_by_jti(jti: str) -> RefreshToken | None:
        """Find a refresh token session document by unique JTI."""
        return await RefreshToken.find_one(RefreshToken.jti == jti)

    @staticmethod
    async def find_refresh_token(jti_or_id: str) -> RefreshToken | None:
        """Find a refresh token session by JTI or ObjectId string."""
        doc = await AuthRepository.find_refresh_token_by_jti(jti_or_id)
        if doc is not None:
            return doc
        try:
            obj_id = PydanticObjectId(jti_or_id)
            return await RefreshToken.get(obj_id)
        except Exception:
            return None

    @staticmethod
    async def revoke_refresh_token(token: RefreshToken) -> None:
        """Mark a specific refresh token session as revoked."""
        now = datetime.now(timezone.utc)
        token.is_revoked = True
        token.revoked_at = now
        await token.save()

    @staticmethod
    async def revoke_all_refresh_tokens(user_id: PydanticObjectId | str) -> int:
        """
        Revoke all active refresh tokens for a specific user across all devices.

        Returns:
            Number of tokens updated/revoked.
        """
        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)

        now = datetime.now(timezone.utc)
        result = await RefreshToken.find(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,  # noqa: E712
        ).update(
            Set(
                {
                    RefreshToken.is_revoked: True,
                    RefreshToken.revoked_at: now,
                    RefreshToken.updated_at: now,
                }
            )
        )
        return result.modified_count if result else 0

    @staticmethod
    async def delete_expired_refresh_tokens() -> int:
        """
        Manually clean up expired refresh tokens (supplementing MongoDB TTL index).

        Returns:
            Number of documents deleted.
        """
        now = datetime.now(timezone.utc)
        result = await RefreshToken.find(RefreshToken.expires_at < now).delete()
        return result.deleted_count if result else 0
