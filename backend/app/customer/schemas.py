"""
Request/response schemas for the customer profile module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict input validation (pincode, coordinates, language code).
    - All schemas use ConfigDict(str_strip_whitespace=True) for automatic
      whitespace stripping on all string fields.
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - Address schemas are separate (AddressCreateRequest, AddressUpdateRequest)
      because addresses are managed independently via dedicated endpoints
      (POST /addresses, PATCH /addresses/{id}, DELETE /addresses/{id}).
    - Latitude/longitude validation uses field constraints (ge/le) instead
      of regex — simpler, faster, and type-safe.
    - Pincode is validated as exactly 6 digits via regex pattern — matches
      Indian postal code format.
    - preferred_language is validated against ISO 639-1 (2-letter codes)
      but not against a hardcoded list — allows new languages without
      code changes. The frontend controls which languages are available.
    - NotificationPreferencesSchema mirrors the embedded model for both
      input and output — same shape, no transformation needed.
"""

import re
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.customer.models import (
    AddressLabel,
    Gender,
    PaymentMethod,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Indian pincode: exactly 6 digits, first digit is 1-9.
_PINCODE_REGEX = re.compile(r"^[1-9]\d{5}$")

# ISO 639-1 language codes: 2-3 lowercase letters.
# Not restricted to a hardcoded list — allows future language additions.
_LANGUAGE_REGEX = re.compile(r"^[a-z]{2,3}$")

# Maximum addresses per customer profile.
_MAX_ADDRESSES = 10


# ---------------------------------------------------------------------------
# Shared Validators
# ---------------------------------------------------------------------------

def _validate_pincode(value: str) -> str:
    """
    Validate Indian postal code format.

    Indian pincodes are exactly 6 digits, first digit is 1-9.
    Examples: 400001 (Mumbai), 110001 (Delhi), 560001 (Bangalore).
    """
    stripped = value.strip()
    if not _PINCODE_REGEX.match(stripped):
        raise ValueError(
            "Pincode must be exactly 6 digits (e.g., 400001)"
        )
    return stripped


def _validate_language(value: str) -> str:
    """
    Validate ISO 639-1 language code.

    Accepts 2-3 lowercase letter codes (e.g., 'hi', 'en', 'ta', 'mar').
    Not restricted to a hardcoded list to support future languages.
    """
    stripped = value.strip().lower()
    if not _LANGUAGE_REGEX.match(stripped):
        raise ValueError(
            "Language must be a valid ISO 639-1 code (e.g., 'hi', 'en', 'ta')"
        )
    return stripped


# ---------------------------------------------------------------------------
# Notification Preferences Schema
# ---------------------------------------------------------------------------

class NotificationPreferencesSchema(BaseModel):
    """
    Notification channel settings for create/update requests.

    Mirrors the embedded NotificationPreferences model. All fields
    optional for updates — only provided channels are changed.

    Attributes:
        push: Enable/disable push notifications.
        email: Enable/disable email notifications.
        sms: Enable/disable SMS notifications.
    """

    push: bool | None = Field(default=None, description="Push notifications via FCM")
    email: bool | None = Field(default=None, description="Email notifications")
    sms: bool | None = Field(default=None, description="SMS notifications")


# ---------------------------------------------------------------------------
# Address Schemas
# ---------------------------------------------------------------------------

class AddressCreateRequest(BaseModel):
    """
    Create a new address in the customer's saved_addresses array.

    All required fields must be provided. Location (lat/lng) is optional —
    populated when the user pins a location on the map.

    The service layer should:
        1. Validate the customer has < 10 addresses.
        2. Generate the address ID (UUID4) server-side.
        3. If is_default=True, unset is_default on all other addresses.
        4. Convert lat/lng to GeoJSON format for storage.

    Attributes:
        label: Address category (Home/Work/Other).
        full_address: Complete street address.
        landmark: Optional nearby landmark.
        city: City name.
        state: State or province.
        pincode: Indian postal code (6 digits).
        latitude: WGS84 latitude (-90 to +90). Optional.
        longitude: WGS84 longitude (-180 to +180). Optional.
        is_default: Set as the default address for new bookings.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    label: AddressLabel = Field(
        default=AddressLabel.HOME,
        description="Address category",
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
        description="Indian postal code (6 digits)",
        examples=["400001"],
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="WGS84 latitude",
        examples=[19.0760],
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="WGS84 longitude",
        examples=[72.8777],
    )
    is_default: bool = Field(
        default=False,
        description="Set as default address for bookings",
    )

    # --- Validators ---

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        return _validate_pincode(value)

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> "AddressCreateRequest":
        """
        Ensure latitude and longitude are provided together.

        A single coordinate without the other is useless for geo queries.
        Either provide both or neither.
        """
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None
        if has_lat != has_lng:
            raise ValueError(
                "Both latitude and longitude must be provided together, or neither"
            )
        return self


class AddressUpdateRequest(BaseModel):
    """
    Partial update for an existing address.

    All fields are optional. At least one field must be provided.
    The service layer should locate the address by ID within the
    embedded array and apply only the provided fields.

    Attributes:
        label: Updated address category.
        full_address: Updated street address.
        landmark: Updated landmark (set to null to clear).
        city: Updated city.
        state: Updated state.
        pincode: Updated postal code.
        latitude: Updated latitude.
        longitude: Updated longitude.
        is_default: Update default status.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    label: AddressLabel | None = Field(default=None, description="Address category")
    full_address: str | None = Field(
        default=None,
        min_length=5,
        max_length=500,
        description="Complete street address",
    )
    landmark: str | None = Field(
        default=None,
        max_length=200,
        description="Nearby landmark",
    )
    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="City name",
    )
    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="State or province",
    )
    pincode: str | None = Field(
        default=None,
        description="Indian postal code (6 digits)",
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="WGS84 latitude",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="WGS84 longitude",
    )
    is_default: bool | None = Field(default=None, description="Default address flag")

    # --- Validators ---

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_pincode(value)
        return value

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> "AddressUpdateRequest":
        """
        Ensure latitude and longitude are provided together.

        Same rule as AddressCreateRequest — a single coordinate
        without the other is useless for geo queries.
        """
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None
        if has_lat != has_lng:
            raise ValueError(
                "Both latitude and longitude must be provided together, or neither"
            )
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "AddressUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Customer Profile Schemas
# ---------------------------------------------------------------------------

class CustomerProfileCreateRequest(BaseModel):
    """
    Create a new customer profile.

    Called after user registration when role=CUSTOMER. The service layer
    should:
        1. Verify the User exists and has role=CUSTOMER.
        2. Verify no CustomerProfile exists for this user_id.
        3. Create the profile with defaults for unset fields.

    Most fields are optional — allows fast onboarding with minimal data.
    Profile can be completed gradually via update requests.

    Attributes:
        date_of_birth: Optional DOB for age verification.
        gender: Optional gender selection.
        profile_photo: Optional photo URL.
        preferred_language: App language (defaults to Hindi).
        preferred_payment_method: Default payment method (defaults to Cash).
        notification_preferences: Channel settings (all enabled by default).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    date_of_birth: date | None = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
        examples=["1995-06-15"],
    )
    gender: Gender | None = Field(
        default=None,
        description="Gender for preferences",
    )
    profile_photo: str | None = Field(
        default=None,
        max_length=512,
        description="Profile photo URL",
        examples=["https://res.cloudinary.com/kaamsetu/image/upload/v1/customers/abc123.jpg"],
    )
    preferred_language: str = Field(
        default="hi",
        min_length=2,
        max_length=10,
        description="ISO 639-1 language code",
        examples=["hi"],
    )
    preferred_payment_method: PaymentMethod = Field(
        default=PaymentMethod.CASH,
        description="Default payment method",
    )
    notification_preferences: NotificationPreferencesSchema | None = Field(
        default=None,
        description="Notification channel settings",
    )

    # --- Validators ---

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        return _validate_language(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, value: date | None) -> date | None:
        """Reject dates of birth in the future."""
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class CustomerProfileUpdateRequest(BaseModel):
    """
    Partial update for an existing customer profile.

    All fields are optional. At least one must be provided.
    The service layer should validate ownership (user can only
    update their own profile).

    Attributes:
        date_of_birth: Updated DOB.
        gender: Updated gender.
        profile_photo: Updated photo URL (set to null to remove).
        preferred_language: Updated language code.
        preferred_payment_method: Updated payment method.
        notification_preferences: Updated channel settings (partial merge).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    date_of_birth: date | None = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
    )
    gender: Gender | None = Field(
        default=None,
        description="Gender for preferences",
    )
    profile_photo: str | None = Field(
        default=None,
        max_length=512,
        description="Profile photo URL",
    )
    preferred_language: str | None = Field(
        default=None,
        min_length=2,
        max_length=10,
        description="ISO 639-1 language code",
    )
    preferred_payment_method: PaymentMethod | None = Field(
        default=None,
        description="Default payment method",
    )
    notification_preferences: NotificationPreferencesSchema | None = Field(
        default=None,
        description="Notification channel settings (partial merge)",
    )

    # --- Validators ---

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_language(value)
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, value: date | None) -> date | None:
        """Reject dates of birth in the future."""
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "CustomerProfileUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class AddressResponse(BaseModel):
    """
    Address representation in API responses.

    Converts GeoJSON [longitude, latitude] back to separate lat/lng
    fields for frontend convenience. Frontend developers expect
    separate latitude/longitude fields, not GeoJSON arrays.

    Attributes:
        id: Address UUID.
        label: Address category.
        full_address: Street address.
        landmark: Nearby landmark.
        city: City name.
        state: State or province.
        pincode: Postal code.
        latitude: Latitude (null if no coordinates).
        longitude: Longitude (null if no coordinates).
        is_default: Whether this is the default address.
        created_at: When the address was added.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Address UUID")
    label: AddressLabel = Field(..., description="Address category")
    full_address: str = Field(..., description="Street address")
    landmark: str | None = Field(None, description="Nearby landmark")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State or province")
    pincode: str = Field(..., description="Postal code")
    latitude: float | None = Field(None, description="WGS84 latitude")
    longitude: float | None = Field(None, description="WGS84 longitude")
    is_default: bool = Field(..., description="Default address flag")
    created_at: datetime = Field(..., description="When address was added")

    @model_validator(mode="before")
    @classmethod
    def extract_coordinates(cls, data: object) -> object:
        """
        Extract lat/lng from GeoJSON location field.

        The model stores coordinates as GeoJSON:
            {"type": "Point", "coordinates": [lng, lat]}

        This validator flattens them into separate latitude/longitude
        fields for the API response.
        """
        # Handle both dict (raw MongoDB) and object (Pydantic model) inputs
        if isinstance(data, dict):
            location = data.get("location")
            if location and isinstance(location, dict):
                coords = location.get("coordinates", [])
                if len(coords) == 2:
                    data["longitude"] = coords[0]
                    data["latitude"] = coords[1]
            return data

        # Pydantic model / object with attributes
        if hasattr(data, "location") and data.location is not None:
            location = data.location
            coords = (
                location.get("coordinates", [])
                if isinstance(location, dict)
                else getattr(location, "coordinates", [])
            )
            if len(coords) == 2:
                # Convert to dict so we can inject lat/lng fields
                if hasattr(data, "model_dump"):
                    result = data.model_dump()
                else:
                    result = dict(data)
                result["longitude"] = coords[0]
                result["latitude"] = coords[1]
                return result

        return data


class NotificationPreferencesResponse(BaseModel):
    """Notification channel settings in API responses."""

    model_config = ConfigDict(from_attributes=True)

    push: bool = Field(..., description="Push notifications enabled")
    email: bool = Field(..., description="Email notifications enabled")
    sms: bool = Field(..., description="SMS notifications enabled")


class CustomerProfileResponse(BaseModel):
    """
    Complete customer profile representation for API responses.

    Includes computed fields (address_count, completion_ratio) for
    frontend display without requiring client-side calculation.

    Security:
        - metadata: EXCLUDED (may contain internal data).
        - user_id: Included (needed for frontend linking).

    Attributes:
        id: Profile document ID.
        user_id: Reference to User document.
        date_of_birth: DOB (null if not provided).
        gender: Gender (null if not provided).
        profile_photo: Photo URL (null if not uploaded).
        saved_addresses: List of address responses.
        default_address_id: UUID of default address.
        preferred_language: ISO 639-1 language code.
        preferred_payment_method: Default payment method.
        notification_preferences: Channel settings.
        total_bookings: Total booking count.
        completed_bookings: Completed booking count.
        cancelled_bookings: Cancelled booking count.
        address_count: Number of saved addresses (computed).
        completion_ratio: Booking completion % (computed).
        created_at: Profile creation time.
        updated_at: Last update time.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="Profile ID (MongoDB ObjectId)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    user_id: str = Field(..., description="Reference to User document")
    date_of_birth: date | None = Field(None, description="Date of birth")
    gender: Gender | None = Field(None, description="Gender")
    profile_photo: str | None = Field(None, description="Profile photo URL")
    saved_addresses: list[AddressResponse] = Field(
        default_factory=list,
        description="Saved addresses",
    )
    default_address_id: str | None = Field(None, description="Default address UUID")
    preferred_language: str = Field(..., description="Language code")
    preferred_payment_method: PaymentMethod = Field(..., description="Payment method")
    notification_preferences: NotificationPreferencesResponse = Field(
        ...,
        description="Notification settings",
    )
    total_bookings: int = Field(..., description="Total bookings")
    completed_bookings: int = Field(..., description="Completed bookings")
    cancelled_bookings: int = Field(..., description="Cancelled bookings")
    address_count: int = Field(default=0, description="Number of saved addresses")
    completion_ratio: float = Field(default=0.0, description="Booking completion %")
    created_at: datetime = Field(..., description="Profile creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """Convert Beanie PydanticObjectId to plain string."""
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def compute_derived_fields(cls, data: object) -> object:
        """
        Compute address_count and completion_ratio from document fields.

        For dict inputs (raw MongoDB data), injects computed values.
        For Beanie Documents, from_attributes=True reads @property directly.
        """
        if isinstance(data, dict):
            addresses = data.get("saved_addresses", [])
            data["address_count"] = len(addresses)
            total = data.get("total_bookings", 0)
            completed = data.get("completed_bookings", 0)
            data["completion_ratio"] = (
                round((completed / total) * 100, 2) if total > 0 else 0.0
            )
        # For Beanie Documents: from_attributes=True reads @property directly
        return data
