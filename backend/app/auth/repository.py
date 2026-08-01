"""
Authentication Repository Layer — KaamSetu Service Marketplace.

Handles all asynchronous MongoDB operations for the User collection,
CustomerProfile collection, and WorkerProfile collection via Beanie ODM.
Strictly decoupled from business logic, password validation, and HTTP serialization.
"""

from app.auth.models import LoginHistory, OTPRecord, User, UserSession
from app.customer.models import CustomerProfile
from app.worker.models import WorkerProfile


class AuthRepository:
    """
    Repository encapsulating database persistence and lookups for auth domain models.
    """

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Retrieve a User document by its MongoDB ID.

        Args:
            user_id: MongoDB ObjectId string.

        Returns:
            User document if found, None otherwise.
        """
        return await User.get(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a User document by normalized email address.

        Args:
            email: Registered email address (case-insensitive search).

        Returns:
            User document if found, None otherwise.
        """
        normalized_email = email.strip().lower()
        return await User.find_one(User.email == normalized_email)

    async def get_user_by_phone(self, phone_number: str) -> User | None:
        """
        Retrieve a User document by E.164 phone number.

        Args:
            phone_number: E.164 formatted phone number string.

        Returns:
            User document if found, None otherwise.
        """
        return await User.find_one(User.phone_number == phone_number.strip())

    async def get_user_by_email_or_phone(self, identifier: str) -> User | None:
        """
        Retrieve a User document by matching either email address or phone number.

        Args:
            identifier: Either an email address or an E.164 phone number.

        Returns:
            User document if found, None otherwise.
        """
        cleaned = identifier.strip()
        return await User.find_one(
            {
                "$or": [
                    {"email": cleaned.lower()},
                    {"phone_number": cleaned},
                ]
            }
        )

    async def get_user_by_reset_token(self, reset_token: str) -> User | None:
        """
        Retrieve a User document by active password reset token in metadata.

        Args:
            reset_token: Recovery token string stored in user.metadata.

        Returns:
            User document if found, None otherwise.
        """
        return await User.find_one({"metadata.reset_token": reset_token})

    async def create_user(self, user: User) -> User:
        """
        Persist a new User document in MongoDB.

        Args:
            user: Unsaved User document instance.

        Returns:
            Persisted User document with generated ID and timestamps.
        """
        return await user.insert()

    async def update_user(self, user: User) -> User:
        """
        Save changes to an existing User document in MongoDB.

        Args:
            user: Modified User document instance.

        Returns:
            Updated User document.
        """
        await user.save()
        return user

    async def create_customer_profile(self, user_id: str) -> CustomerProfile:
        """
        Create and persist a CustomerProfile document linked to a User.

        Args:
            user_id: String ID of the created User document.

        Returns:
            Persisted CustomerProfile document.
        """
        profile = CustomerProfile(user_id=user_id)
        return await profile.insert()

    async def create_worker_profile(self, user_id: str) -> WorkerProfile:
        """
        Create and persist a WorkerProfile document linked to a User.

        Args:
            user_id: String ID of the created User document.

        Returns:
            Persisted WorkerProfile document.
        """
        profile = WorkerProfile(user_id=user_id)
        return await profile.insert()

    # =========================================================================
    # Phase 3.3 — OTP, Session, and Login History Repository Methods
    # =========================================================================

    async def create_otp_record(self, record: OTPRecord) -> OTPRecord:
        """Persist a new OTP verification record in MongoDB."""
        return await record.insert()

    async def get_active_otp_record(
        self,
        identifier: str,
        purpose: str,
    ) -> OTPRecord | None:
        """Retrieve the latest un-used OTPRecord for an identifier and purpose."""
        return await OTPRecord.find_one(
            OTPRecord.identifier == identifier,
            OTPRecord.purpose == purpose,
            OTPRecord.is_used == False,
        )

    async def create_user_session(self, session: UserSession) -> UserSession:
        """Persist a new active user session document."""
        return await session.insert()

    async def get_user_session_by_id(
        self,
        user_id: str,
        session_id: str,
    ) -> UserSession | None:
        """Retrieve an active UserSession by its unique session UUID."""
        return await UserSession.find_one(
            UserSession.user_id == user_id,
            UserSession.session_id == session_id,
            UserSession.is_revoked == False,
        )

    async def list_active_user_sessions(self, user_id: str) -> list[UserSession]:
        """List all non-revoked UserSession documents for a user."""
        return await UserSession.find(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False,
        ).sort("-last_active").to_list()

    async def create_login_history(self, entry: LoginHistory) -> LoginHistory:
        """Append an immutable LoginHistory record."""
        return await entry.insert()

    async def list_user_login_history(
        self,
        user_id: str,
        limit: int = 20,
    ) -> list[LoginHistory]:
        """Retrieve recent login attempt records for a user."""
        return await LoginHistory.find(
            LoginHistory.user_id == user_id,
        ).sort("-timestamp").limit(limit).to_list()
