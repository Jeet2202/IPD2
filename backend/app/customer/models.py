"""
Customer Profile document model — domain-specific data for customers.

Architecture:
    - Separates customer-specific data from auth identity (User collection).
    - One User → One CustomerProfile (enforced by unique index on user_id).
    - Addresses are EMBEDDED (not a separate collection) for atomic reads.
    - Coordinates stored for future geo-spatial queries (2dsphere index ready).

Why embedded addresses (not a separate collection):
    - A customer typically has 2-5 addresses — small, bounded list.
    - Every profile read needs addresses — embedding avoids $lookup joins.
    - Atomic updates: adding/removing addresses is a single document write.
    - MongoDB documents have a 16 MB limit; even 100 addresses with full
      fields would use < 50 KB — no risk of exceeding the limit.
    - Geo-queries on embedded coordinates work with $elemMatch + 2dsphere.
    - If addresses ever need to be queried independently across users
      (e.g., "all users in pincode 400001"), a separate collection can be
      added later without changing the profile schema.

Why this schema is scalable:
    - user_id unique index ensures O(1) profile lookup from JWT subject.
    - Booking counters are denormalized (total/completed/cancelled) to avoid
      counting queries on the bookings collection for every profile view.
    - notification_preferences is a typed embedded model — new channels
      (WhatsApp, in-app) are added by extending NotificationPreferences,
      with backward-compatible defaults.
    - metadata dict handles unforeseen future fields without migration.

Index strategy:
    - user_id (unique): Profile lookup by authenticated user ID. One-to-one.
    - saved_addresses.location (2dsphere): Future nearby worker search
      and Google Maps integration. Declared upfront so existing documents
      are indexed as addresses with coordinates are added.
    - created_at (descending): Admin dashboard sorting, analytics.

Collection name: "customer_profiles" (explicit, lowercase, plural).
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import BaseModel, Field
from pymongo import DESCENDING, GEOSPHERE, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Gender(str, Enum):
    """
    Gender options for customer profile.

    - MALE / FEMALE / OTHER: Standard options.
    - PREFER_NOT_TO_SAY: Opt-out for privacy-conscious users.
    """

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class AddressLabel(str, Enum):
    """
    Predefined address labels for quick identification.

    - HOME / WORK: Most common — displayed with icons in the app.
    - OTHER: Catch-all for secondary locations (parents' house, gym, etc.).
    """

    HOME = "home"
    WORK = "work"
    OTHER = "other"


class PaymentMethod(str, Enum):
    """
    Preferred payment methods.

    Stored as preference only — actual payment processing is handled
    by the payments module. This field controls default selection in UI.

    - CASH: Cash on delivery (dominant in Indian home services).
    - UPI: UPI apps (GPay, PhonePe, Paytm).
    - CARD: Credit/debit card via payment gateway.
    - WALLET: In-app wallet (future feature).
    """

    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    WALLET = "wallet"


# ---------------------------------------------------------------------------
# Embedded Models
# ---------------------------------------------------------------------------

class GeoLocation(BaseModel):
    """
    GeoJSON Point for MongoDB 2dsphere queries.

    Stored in GeoJSON format per MongoDB specification:
        { "type": "Point", "coordinates": [longitude, latitude] }

    Note: MongoDB GeoJSON uses [longitude, latitude] order (not lat/lng).
    This matches the GeoJSON RFC 7946 standard.

    Attributes:
        type: Always "Point" for single-location addresses.
        coordinates: [longitude, latitude] pair. Longitude first per GeoJSON.
    """

    type: Literal["Point"] = Field(
        default="Point",
        description="GeoJSON geometry type (locked to 'Point')",
    )
    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude] in GeoJSON order",
        examples=[[72.8777, 19.0760]],
    )


class NotificationPreferences(BaseModel):
    """
    Channel-level notification opt-in/opt-out settings.

    All channels default to True (opt-in) for new customers.
    Users can disable individual channels from app settings.

    Future channels (WhatsApp, in-app) are added by extending
    this model with new fields and backward-compatible True defaults.

    Attributes:
        push: Mobile push notifications via Firebase Cloud Messaging.
        email: Email notifications for bookings, promotions, receipts.
        sms: SMS notifications for OTP, booking confirmations, alerts.
    """

    push: bool = Field(
        default=True,
        description="Push notifications via FCM",
    )
    email: bool = Field(
        default=True,
        description="Email notifications",
    )
    sms: bool = Field(
        default=True,
        description="SMS notifications",
    )


class Address(BaseModel):
    """
    Embedded address model — stored inside CustomerProfile.saved_addresses.

    Each address has a unique ID (UUID4) for identification within the
    embedded array. This enables targeted updates and deletion via
    array filters without loading the entire profile.

    Attributes:
        id: UUID4 string — unique identifier within the addresses array.
            Generated server-side, not by the client.
        label: Predefined category (Home/Work/Other) for UI display.
        full_address: Complete street address as entered by the user.
                      Displayed on booking confirmation and invoices.
        landmark: Nearby landmark for navigation help. Common in Indian
                  addresses where street numbers are unreliable.
        city: City name. Used for service area filtering and worker
              matching. Indexed for geo-based queries.
        state: State/province. Used for tax calculation and compliance.
        pincode: Indian postal code (6 digits). Used for service area
                 matching and delivery zone determination.
        location: GeoJSON Point for coordinates. Enables MongoDB 2dsphere
                  queries for "nearby workers" and Google Maps integration.
                  Optional — populated when user pins location on map.
        is_default: True for the primary address. Only one address should
                    have is_default=True — enforced by the service layer.
        created_at: When this address was added.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique address identifier (UUID4)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    label: AddressLabel = Field(
        default=AddressLabel.HOME,
        description="Address category for display",
    )
    full_address: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Complete street address",
        examples=["B-42, Sector 15, Noida"],
    )
    landmark: str | None = Field(
        default=None,
        max_length=200,
        description="Nearby landmark for navigation",
        examples=["Near City Mall"],
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name",
        examples=["Mumbai"],
    )
    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="State or province",
        examples=["Maharashtra"],
    )
    pincode: str = Field(
        ...,
        pattern=r"^[1-9]\d{5}$",
        description="Indian postal code (6 digits, no leading zero)",
        examples=["400001"],
    )
    location: GeoLocation | None = Field(
        default=None,
        description="GeoJSON Point for map coordinates",
    )
    is_default: bool = Field(
        default=False,
        description="True if this is the primary address",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this address was added (UTC)",
    )


# ---------------------------------------------------------------------------
# Customer Profile Document
# ---------------------------------------------------------------------------

class CustomerProfile(Document):
    """
    Domain-specific profile for platform customers.

    Stores personal preferences, saved addresses, booking statistics,
    and notification settings. Authentication data (email, password,
    phone) stays in the User collection — this profile references
    User via user_id.

    One User → One CustomerProfile (enforced by unique index on user_id).

    Attributes:
        user_id: Reference to the User document's ObjectId. Unique —
                 prevents duplicate profiles for the same user. Indexed
                 for O(1) lookup from JWT subject during auth flow.
        date_of_birth: Optional. Used for age verification (some services
                       require 18+), birthday promotions, and analytics.
        gender: Optional. Used for worker matching preferences and
                analytics. Defaults to None (not set until user chooses).
        profile_photo: URL to customer's profile photo (Cloudinary/S3).
                       Separate from User.profile_image — allows different
                       images for auth avatar vs. in-app profile.
        saved_addresses: Embedded array of Address objects. Bounded —
                         typical customers have 2-5 addresses. Service
                         layer should enforce a max (e.g., 10 addresses).
        default_address_id: UUID4 string pointing to the default address
                            within saved_addresses. Used to pre-fill the
                            address on new bookings. Null until an address
                            is saved.
        preferred_language: ISO 639-1 language code for the app UI.
                            Defaults to Hindi (India's most common).
                            Used by the frontend and notification templates.
        preferred_payment_method: Default payment method for new bookings.
                                  Defaults to CASH (dominant in Indian
                                  home services market).
        notification_preferences: Embedded notification channel settings.
                                  Controls which channels deliver notifications.
        total_bookings: Denormalized counter — total bookings ever created.
                        Avoids COUNT queries on the bookings collection.
                        Incremented by the booking service on creation.
        completed_bookings: Denormalized counter — successfully completed.
                            Used for loyalty tiers and AI recommendations.
        cancelled_bookings: Denormalized counter — cancelled by customer.
                            High ratio triggers fraud detection.
        metadata: Flexible key-value store for future features:
                  - ai_recommendations: list[str] (AI service suggestions)
                  - voice_assistant_enabled: bool
                  - referral_code: str
                  - loyalty_tier: str (bronze/silver/gold)
        created_at: Profile creation timestamp (UTC). Set once on insert.
        updated_at: Last modification timestamp (UTC). Auto-updated on
                    every save via @before_event hook.
    """

    # --- User Reference ---
    user_id: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Reference to User document ObjectId (unique, one-to-one)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )

    # --- Personal Information ---
    date_of_birth: date | None = Field(
        default=None,
        description="Date of birth for age verification and promotions",
        examples=["1995-06-15"],
    )
    gender: Gender | None = Field(
        default=None,
        description="Gender for preferences and analytics",
    )
    profile_photo: str | None = Field(
        default=None,
        max_length=512,
        description="URL to profile photo (Cloudinary/S3)",
        examples=["https://res.cloudinary.com/kaamsetu/image/upload/v1/customers/abc123.jpg"],
    )

    # --- Addresses ---
    saved_addresses: list[Address] = Field(
        default_factory=list,
        description="Embedded array of saved addresses (max ~10)",
    )
    default_address_id: str | None = Field(
        default=None,
        description="UUID4 of the default address in saved_addresses",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    # --- Preferences ---
    preferred_language: str = Field(
        default="hi",
        min_length=2,
        max_length=10,
        description="ISO 639-1 language code (e.g., 'hi', 'en', 'ta')",
        examples=["hi"],
    )
    preferred_payment_method: PaymentMethod = Field(
        default=PaymentMethod.CASH,
        description="Default payment method for new bookings",
    )

    # --- Notifications ---
    notification_preferences: NotificationPreferences = Field(
        default_factory=NotificationPreferences,
        description="Channel-level notification settings",
    )

    # --- Booking Statistics (Denormalized) ---
    total_bookings: int = Field(
        default=0,
        ge=0,
        description="Total bookings created (denormalized counter)",
    )
    completed_bookings: int = Field(
        default=0,
        ge=0,
        description="Successfully completed bookings",
    )
    cancelled_bookings: int = Field(
        default=0,
        ge=0,
        description="Bookings cancelled by customer",
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Profile creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp (UTC, auto-updated)",
    )

    # ------------------------------------------------------------------
    # Beanie Event Hooks
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
        - indexes: Optimized for profile lookup, geo queries, and sorting.
        - use_state_management: Enables Beanie's change tracking for
          efficient partial updates.
        """

        name = "customer_profiles"
        use_state_management = True

        indexes = [
            # 2dsphere index on embedded address coordinates.
            # Enables $near and $geoWithin queries for "nearby workers"
            # and service area matching via Google Maps integration.
            # Sparse: only indexes documents that have location data,
            # keeping the index compact for addresses without coordinates.
            IndexModel(
                [("saved_addresses.location", GEOSPHERE)],
                name="idx_address_geo_2dsphere",
                sparse=True,
            ),
            # Descending sort on created_at for admin dashboard pagination.
            IndexModel(
                [("created_at", DESCENDING)],
                name="idx_created_at_desc",
            ),
        ]

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @property
    def address_count(self) -> int:
        """Number of saved addresses."""
        return len(self.saved_addresses)

    @property
    def default_address(self) -> Address | None:
        """
        Return the default address if one is set.

        Scans the embedded array for the matching UUID. Returns None
        if default_address_id is not set or doesn't match any address.
        """
        if not self.default_address_id:
            return None
        for addr in self.saved_addresses:
            if addr.id == self.default_address_id:
                return addr
        return None

    @property
    def completion_ratio(self) -> float:
        """
        Booking completion rate as a percentage (0.0 - 100.0).

        Used for loyalty tier calculation and AI recommendations.
        Returns 0.0 if no bookings exist (avoids ZeroDivisionError).
        """
        if self.total_bookings == 0:
            return 0.0
        return round((self.completed_bookings / self.total_bookings) * 100, 2)

    def get_address_by_id(self, address_id: str) -> Address | None:
        """Look up an address by its UUID within the embedded array."""
        for addr in self.saved_addresses:
            if addr.id == address_id:
                return addr
        return None

    def __repr__(self) -> str:
        return (
            f"<CustomerProfile user_id={self.user_id} "
            f"addresses={self.address_count} "
            f"bookings={self.total_bookings}>"
        )
