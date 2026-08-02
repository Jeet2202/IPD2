"""
Pydantic schemas for Address Management — request validation and response serialization.

Phase 4.3.3 Changes (GeoJSON Migration):
    - CreateAddressRequest / UpdateAddressRequest still accept flat latitude/longitude
      fields — the service layer converts them to GeoJSON Point internally.
    - AddressResponse still returns flat latitude/longitude fields — extracted from
      location.coordinates by the service layer.
    - Flutter clients require NO changes.

Schemas:
    CreateAddressRequest   — Validated payload for POST /customer/addresses
    UpdateAddressRequest   — Partial update payload for PUT /customer/addresses/{id}
    AddressResponse        — Full address DTO returned by all endpoints
    AddressListResponse    — Paginated list wrapper
"""

import re

from pydantic import BaseModel, Field, field_validator, model_validator

from app.address.models import AddressLabel

# ---------------------------------------------------------------------------
# Validation Patterns
# ---------------------------------------------------------------------------

_PHONE_RE = re.compile(r"^\+91[6-9]\d{9}$")
_PIN_RE = re.compile(r"^\d{6}$")


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------


class CreateAddressRequest(BaseModel):
    """
    Payload for creating a new customer address.

    All required fields must be provided. Latitude and longitude are
    optional — can be set later via device GPS on mobile.

    The backend converts latitude + longitude into a GeoJSON Point
    for MongoDB storage. The API surface remains lat/lng for compatibility.
    """

    label: AddressLabel = Field(
        default=AddressLabel.HOME,
        description="Address label: Home, Office, or Other",
        examples=["Home"],
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the contact person at this address",
        examples=["Rajesh Kumar"],
    )
    phone: str = Field(
        ...,
        description="Contact phone number in +91XXXXXXXXXX format",
        examples=["+919876543210"],
    )
    address_line_1: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Primary address (flat no., building, street)",
        examples=["Flat 4B, Sunrise Apartments, MG Road"],
    )
    address_line_2: str | None = Field(
        default=None,
        max_length=200,
        description="Secondary address (area, locality)",
        examples=["Andheri West"],
    )
    landmark: str | None = Field(
        default=None,
        max_length=150,
        description="Nearby landmark for easier navigation",
        examples=["Near Andheri Metro Station"],
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
        description="State name",
        examples=["Maharashtra"],
    )
    country: str = Field(
        default="India",
        min_length=2,
        max_length=100,
        description="Country name",
        examples=["India"],
    )
    postal_code: str = Field(
        ...,
        description="6-digit Indian PIN code",
        examples=["400058"],
    )

    # ── Location fields (flat API, converted to GeoJSON internally) ──────────
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description=(
            "GPS latitude (optional). Stored internally as GeoJSON coordinates[1]. "
            "Must be provided together with longitude."
        ),
        examples=[19.1136],
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description=(
            "GPS longitude (optional). Stored internally as GeoJSON coordinates[0]. "
            "Must be provided together with latitude."
        ),
        examples=[72.8697],
    )

    is_default: bool = Field(
        default=False,
        description="Set as default address. Auto-true if first address.",
        examples=[True],
    )

    # ── Validators ──────────────────────────────────────────────────────────

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not _PHONE_RE.match(v):
            raise ValueError(
                "Phone must be in +91XXXXXXXXXX format (10 digits starting with 6-9)."
            )
        return v

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        v = v.strip()
        if not _PIN_RE.match(v):
            raise ValueError("Postal code must be exactly 6 digits.")
        return v

    @field_validator("full_name", "address_line_1", "city", "state", "country")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @field_validator("address_line_2", "landmark")
    @classmethod
    def strip_optional_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v is not None and v.strip() else None

    @model_validator(mode="after")
    def validate_lat_lng_pair(self) -> "CreateAddressRequest":
        """Latitude and longitude must either both be set or both be None."""
        lat, lng = self.latitude, self.longitude
        if (lat is None) != (lng is None):
            raise ValueError(
                "latitude and longitude must both be provided or both be omitted."
            )
        return self


class UpdateAddressRequest(BaseModel):
    """
    Partial update payload for an existing customer address.
    Only provided fields are updated (PATCH semantics on all fields).

    Latitude and longitude, if provided, are converted to GeoJSON Point
    by the service layer. The API surface remains flat lat/lng.
    """

    label: AddressLabel | None = Field(default=None, description="Address label")
    full_name: str | None = Field(default=None, min_length=2, max_length=100, description="Contact full name")
    phone: str | None = Field(default=None, description="Contact phone (+91XXXXXXXXXX)")
    address_line_1: str | None = Field(default=None, min_length=5, max_length=200, description="Primary address line")
    address_line_2: str | None = Field(default=None, max_length=200, description="Secondary address line")
    landmark: str | None = Field(default=None, max_length=150, description="Nearby landmark")
    city: str | None = Field(default=None, min_length=2, max_length=100, description="City name")
    state: str | None = Field(default=None, min_length=2, max_length=100, description="State name")
    country: str | None = Field(default=None, min_length=2, max_length=100, description="Country name")
    postal_code: str | None = Field(default=None, description="6-digit PIN code")

    # ── Location fields (flat API, converted to GeoJSON internally) ──────────
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="GPS latitude. Updates GeoJSON location.coordinates[1].",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="GPS longitude. Updates GeoJSON location.coordinates[0].",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not _PHONE_RE.match(v):
                raise ValueError(
                    "Phone must be in +91XXXXXXXXXX format (10 digits starting with 6-9)."
                )
        return v

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not _PIN_RE.match(v):
                raise ValueError("Postal code must be exactly 6 digits.")
        return v

    @field_validator("full_name", "address_line_1", "city", "state", "country")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v is not None else None

    @field_validator("address_line_2", "landmark")
    @classmethod
    def strip_optional_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v is not None and v.strip() else None

    @model_validator(mode="after")
    def validate_lat_lng_pair(self) -> "UpdateAddressRequest":
        """
        Latitude and longitude must either both be set or both be None.
        Partial update: if only one is provided, the other must be explicitly set too.
        """
        lat, lng = self.latitude, self.longitude
        if (lat is None) != (lng is None):
            raise ValueError(
                "latitude and longitude must both be provided or both be omitted "
                "when updating location."
            )
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------


class AddressResponse(BaseModel):
    """
    Full address DTO returned by all address endpoints.

    Location is returned as flat latitude/longitude fields for Flutter
    compatibility, even though stored internally as GeoJSON Point.
    """

    id: str = Field(..., description="Address ObjectId string")
    customer_id: str = Field(..., description="Owner's User ObjectId string")

    label: str = Field(..., description="Address label: Home, Office, Other")
    full_name: str = Field(..., description="Contact full name")
    phone: str = Field(..., description="Contact phone number")

    address_line_1: str = Field(..., description="Primary address line")
    address_line_2: str | None = Field(default=None, description="Secondary address line")
    landmark: str | None = Field(default=None, description="Nearby landmark")

    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    country: str = Field(..., description="Country")
    postal_code: str = Field(..., description="6-digit PIN code")

    # ── Flat lat/lng (extracted from GeoJSON location by service) ─────────────
    latitude: float | None = Field(
        default=None,
        description="GPS latitude — extracted from GeoJSON location.coordinates[1]",
    )
    longitude: float | None = Field(
        default=None,
        description="GPS longitude — extracted from GeoJSON location.coordinates[0]",
    )

    is_default: bool = Field(..., description="True if this is the default address")
    is_deleted: bool = Field(..., description="True if soft-deleted")

    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last-update timestamp")

    model_config = {"from_attributes": True}


class AddressListResponse(BaseModel):
    """Response for listing all active customer addresses."""

    total: int = Field(..., description="Total number of active (non-deleted) addresses")
    addresses: list[AddressResponse] = Field(..., description="List of address DTOs")
