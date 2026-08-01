"""
User document model — single identity source for all platform actors.

Architecture:
    - ONE User collection serves Customers, Workers, and Admins.
    - Role-based differentiation via UserRole enum (no separate collections).
    - Beanie Document with MongoDB-optimized indexes for auth queries.
    - Timestamps (created_at, updated_at) auto-managed via before_save hook.
    - Future-proof metadata dict for AI matching, voice, social login, etc.

Design decisions:
    - Single collection avoids cross-collection joins (MongoDB anti-pattern)
      and simplifies JWT token validation to a single lookup.
    - Unique compound index on email+phone ensures no duplicate accounts
      while still allowing efficient auth lookups on either field.
    - refresh_token_version enables server-side token invalidation without
      a blocklist table — increment to revoke all refresh tokens instantly.
    - profile_image stores a URL (Cloudinary/S3), not binary data.
    - metadata dict supports arbitrary future fields (preferred_language,
      fcm_token, social_provider) without schema migrations.

Index strategy:
    - email (unique): Login by email, duplicate prevention.
    - phone_number (unique): Login by phone, OTP verification.
    - role + account_status (compound): Admin dashboards filter users by
      role and status — compound index covers both queries efficiently.
    - created_at (descending): Recent-first pagination for admin panels.
    - last_login (descending, sparse): Analytics queries; sparse skips
      users who have never logged in, keeping the index small.

Collection name: "users" (explicit, lowercase, plural — MongoDB convention).
"""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import EmailStr, Field
from pymongo import DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    """
    Platform roles. Stored as lowercase strings in MongoDB for readability.

    - CUSTOMER: Books services, leaves reviews, manages addresses.
    - WORKER: Accepts jobs, manages availability, receives payments.
    - ADMIN: Full platform access — user management, analytics, moderation.
    """

    CUSTOMER = "customer"
    WORKER = "worker"
    ADMIN = "admin"


class AccountStatus(str, Enum):
    """
    Account lifecycle states. Controls access and visibility.

    - ACTIVE: Full platform access.
    - INACTIVE: Voluntarily deactivated (e.g., worker on vacation).
    - BLOCKED: Admin-enforced suspension (fraud, policy violation).
    - PENDING_VERIFICATION: Registered but email/phone not yet verified.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"


# ---------------------------------------------------------------------------
# User Document
# ---------------------------------------------------------------------------

class User(Document):
    """
    Core identity document for every platform actor.

    Single collection design — role field differentiates customers,
    workers, and admins. All auth operations (login, token refresh,
    password reset) query this one collection.

    Attributes:
        first_name: User's given name. Stripped of whitespace on input.
                    Used in greetings, notifications, and display.
        last_name: User's family name. Stripped of whitespace on input.
                   Used in formal communications and invoices.
        email: Primary login identifier. Unique across the platform.
               Validated as RFC 5322 compliant via Pydantic EmailStr.
               Stored lowercase to prevent duplicate accounts.
        phone_number: Secondary login identifier (OTP-based auth).
                      Unique across the platform. Stored in E.164 format
                      (e.g., +919876543210) for SMS gateway compatibility.
        password_hash: Bcrypt hash string ($2b$12$...). Never exposed
                       via API responses. Set via core.security.hash_password().
        role: Platform role (customer/worker/admin). Determines permissions,
              visible UI features, and API access scope.
        account_status: Lifecycle state. Defaults to PENDING_VERIFICATION
                        for new registrations. Changed by admin actions or
                        verification workflows.
        email_verified: True after the user clicks the email verification
                        link. Required before account becomes ACTIVE.
        phone_verified: True after OTP verification. Required for workers
                        (customers can skip for faster onboarding).
        profile_completed: True when the user has filled all required
                           profile fields (name, photo, address for customers;
                           skills, documents for workers). Used to gate
                           access to booking/job features.
        profile_image: URL to the user's profile photo (Cloudinary/S3).
                       None until uploaded. Used in chat, reviews, and
                       worker cards.
        refresh_token_version: Integer counter for server-side token
                               revocation. Embedded in refresh token payload.
                               Increment to invalidate ALL refresh tokens
                               for this user (e.g., password change, logout
                               from all devices). Avoids a token blocklist.
        last_login: Timestamp of the most recent successful login.
                    Used for analytics, dormant account detection, and
                    security audits. None until first login.
        metadata: Flexible key-value store for future features without
                  schema migration. Planned uses:
                  - preferred_language: str (multi-language support)
                  - fcm_token: str (push notifications via Firebase)
                  - social_provider: str (Google/Facebook social login)
                  - ai_profile_vector: list[float] (AI matching embeddings)
                  - voice_assistant_enabled: bool (voice assistant opt-in)
        created_at: Immutable registration timestamp. Set once on insert
                    via before_save hook. Used for analytics, sorting,
                    and audit trails.
        updated_at: Last modification timestamp. Auto-updated on every
                    save via before_save hook. Used for cache invalidation
                    and sync.
    """

    # --- Identity ---
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's given name",
        examples=["Rajesh"],
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's family name",
        examples=["Kumar"],
    )

    # --- Authentication ---
    email: Indexed(EmailStr, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Primary login identifier (unique, lowercase)",
        examples=["rajesh.kumar@example.com"],
    )
    phone_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        min_length=10,
        max_length=15,
        description="Phone in E.164 format (e.g., +919876543210)",
        examples=["+919876543210"],
    )
    password_hash: str = Field(
        ...,
        description="Bcrypt hash — never exposed in API responses",
        exclude=True,
    )

    # --- Authorization ---
    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        description="Platform role determining access scope",
    )
    account_status: AccountStatus = Field(
        default=AccountStatus.PENDING_VERIFICATION,
        description="Account lifecycle state",
    )

    # --- Verification Flags ---
    email_verified: bool = Field(
        default=False,
        description="True after email verification link is clicked",
    )
    phone_verified: bool = Field(
        default=False,
        description="True after OTP verification completes",
    )
    profile_completed: bool = Field(
        default=False,
        description="True when all required profile fields are filled",
    )

    # --- Profile ---
    profile_image: str | None = Field(
        default=None,
        description="URL to profile photo (Cloudinary/S3)",
        examples=["https://res.cloudinary.com/kaamsetu/image/upload/v1/users/abc123.jpg"],
    )

    # --- Token Management ---
    refresh_token_version: int = Field(
        default=0,
        ge=0,
        description="Increment to revoke all refresh tokens for this user",
    )

    # --- Activity ---
    last_login: datetime | None = Field(
        default=None,
        description="Timestamp of the most recent successful login",
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Immutable registration timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp (UTC, auto-updated)",
    )

    # ------------------------------------------------------------------
    # Beanie hooks
    # ------------------------------------------------------------------

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        """Auto-update `updated_at` on every write operation."""
        self.updated_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Beanie Settings
    # ------------------------------------------------------------------

    class Settings:
        """
        Beanie collection configuration.

        - name: Explicit collection name (lowercase, plural).
        - indexes: Compound and single-field indexes for query optimization.
        - use_state_management: Enables Beanie's change tracking for
          partial updates (only changed fields are sent to MongoDB).
        """

        name = "users"
        use_state_management = True

        indexes = [
            # Compound index: admin dashboard queries filtering by role + status.
            # Covers queries like "all active workers" or "blocked customers".
            IndexModel(
                [("role", 1), ("account_status", 1)],
                name="idx_role_status",
            ),
            # Descending sort on created_at for recent-first pagination.
            IndexModel(
                [("created_at", DESCENDING)],
                name="idx_created_at_desc",
            ),
            # Sparse descending index on last_login for analytics.
            # Sparse: excludes documents where last_login is null,
            # keeping the index compact for users who never logged in.
            IndexModel(
                [("last_login", DESCENDING)],
                name="idx_last_login_desc",
                sparse=True,
            ),
        ]

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        """Concatenated display name for UI and notifications."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """Quick check for active account status."""
        return self.account_status == AccountStatus.ACTIVE

    @property
    def is_verified(self) -> bool:
        """True when both email and phone are verified."""
        return self.email_verified and self.phone_verified

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} email={self.email} "
            f"role={self.role.value} status={self.account_status.value}>"
        )
