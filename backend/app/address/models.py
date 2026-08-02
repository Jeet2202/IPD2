"""
Address Beanie document model — dedicated collection for customer addresses.

Design rationale:
    - Separate collection (NOT embedded in CustomerProfile) so that:
        1. Bookings can hold a stable address_id foreign key.
        2. Each address can be independently soft-deleted or updated.
        3. GeoJSON location field enables 2dsphere index for geo queries.
    - Soft-delete pattern: is_deleted=True, never hard-delete.
    - At most one is_default=True per customer at any time (enforced in service).

Location Design (Phase 4.3.3):
    - location field uses GeoJSON Point format:
        {"type": "Point", "coordinates": [longitude, latitude]}
    - NOTE: GeoJSON ALWAYS stores [longitude, latitude], not [latitude, longitude].
    - MongoDB 2dsphere index on location enables:
        * $near queries for worker matching
        * $geoWithin for service radius
        * $geoNear aggregation for distance calculation
    - The REST API still accepts/returns flat latitude/longitude fields
      (converted in service layer) so Flutter clients are unaffected.

Collection: customer_addresses
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class AddressLabel(str, Enum):
    """Human-readable label for the address purpose."""

    HOME = "Home"
    OFFICE = "Office"
    OTHER = "Other"


class GeoJSONPoint(BaseModel):
    """
    GeoJSON Point geometry.

    MongoDB 2dsphere index requires coordinates in [longitude, latitude] order.

    IMPORTANT: GeoJSON coordinates are ALWAYS [longitude, latitude].
               This is the OPPOSITE of the common lat/lng mental model.
               - coordinates[0] = longitude
               - coordinates[1] = latitude

    Used for:
        - Worker matching (find workers near customer address)
        - Distance calculation between addresses
        - Service radius queries ($geoWithin)
        - Routing for inspections
    """

    type: str = Field(default="Point", description="GeoJSON geometry type — always 'Point'")
    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude] — GeoJSON order (longitude first!)",
    )

    @property
    def longitude(self) -> float:
        """Extract longitude (coordinates[0])."""
        return self.coordinates[0]

    @property
    def latitude(self) -> float:
        """Extract latitude (coordinates[1])."""
        return self.coordinates[1]

    @classmethod
    def from_lat_lng(cls, latitude: float, longitude: float) -> "GeoJSONPoint":
        """
        Construct a GeoJSONPoint from conventional (latitude, longitude) values.

        GeoJSON stores [longitude, latitude] — this helper ensures correct order.
        Always use this factory instead of constructing coordinates manually.
        """
        return cls(coordinates=[longitude, latitude])


class Address(Document):
    """
    Customer address document.

    Linked to a customer via customer_id (= User._id).
    Supports multiple addresses per customer with a single default.

    Location stored as GeoJSON Point for MongoDB geo-indexing.
    The REST API exposes flat latitude/longitude (converted in service layer).

    Future integrations:
        - Booking: booking.service_address_id → Address.id
        - Worker Matching: Address.location for $near queries
        - Inspection: Address.full_name/phone as contact details
        - Distance: $geoNear aggregation on Address.location
    """

    customer_id: Annotated[PydanticObjectId, Indexed()]
    """Foreign key to User._id (not CustomerProfile._id)."""

    label: AddressLabel = Field(
        default=AddressLabel.HOME,
        description="Address category: Home, Office, or Other",
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the person at this address",
    )
    phone: str = Field(
        ...,
        max_length=15,
        description="Contact phone for this address (+91XXXXXXXXXX)",
    )

    address_line_1: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Primary address line (flat/house no, building name, street)",
    )
    address_line_2: str | None = Field(
        default=None,
        max_length=200,
        description="Secondary address line (area, locality)",
    )
    landmark: str | None = Field(
        default=None,
        max_length=150,
        description="Nearby landmark to help workers locate the address",
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name",
    )
    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="State name",
    )
    country: str = Field(
        default="India",
        min_length=2,
        max_length=100,
        description="Country name",
    )
    postal_code: str = Field(
        ...,
        description="6-digit Indian postal code (PIN code)",
    )

    location: GeoJSONPoint | None = Field(
        default=None,
        description=(
            "GeoJSON Point for MongoDB 2dsphere indexing. "
            "Coordinates stored as [longitude, latitude] per GeoJSON spec. "
            "Use GeoJSONPoint.from_lat_lng(lat, lng) to construct. "
            "Enables $near, $geoWithin, and $geoNear queries for worker matching."
        ),
    )

    is_default: bool = Field(
        default=False,
        description="True if this is the customer's default address for bookings",
    )
    is_deleted: bool = Field(
        default=False,
        description="Soft-delete flag — deleted addresses are hidden but preserved",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    class Settings:
        name = "customer_addresses"
        use_state_management = True
        indexes = [
            # 2dsphere index on the GeoJSON location field.
            # Enables MongoDB geospatial queries:
            #   $near, $nearSphere, $geoWithin, $geoNear aggregation
            # Required for worker matching and distance calculation features.
            [("location", "2dsphere")],
        ]

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
