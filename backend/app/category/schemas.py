"""
Request/response schemas for the Category & Service module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Slug auto-generation from name using the generate_slug utility.
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Price validation ensures minimum_price ≤ base_market_price ≤ maximum_price.
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - CategoryCreateRequest auto-generates slug from name if not provided.
    - ServiceCreateRequest requires category_id and auto-generates slug.
    - required_skills are normalized to lowercase for consistent matching
      against WorkerProfile.skills[].skill_name.
    - Service response includes computed fields (price_range_display,
      duration_display) for frontend convenience.
    - Color code validated as #RRGGBB hex format.
"""

import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.category.models import generate_slug


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Hex color code: #RRGGBB format.
_COLOR_CODE_REGEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

# Slug format: lowercase alphanumeric with hyphens.
_SLUG_REGEX = re.compile(r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$")


# ---------------------------------------------------------------------------
# Shared Validators
# ---------------------------------------------------------------------------

def _validate_slug(value: str) -> str:
    """
    Validate and normalize a URL-friendly slug.

    Accepts lowercase alphanumeric characters and hyphens.
    Must start and end with an alphanumeric character.
    Examples: "electrical", "ac-repair", "salon-at-home".
    """
    stripped = value.strip().lower()
    if len(stripped) < 2:
        raise ValueError("Slug must be at least 2 characters")
    if not _SLUG_REGEX.match(stripped):
        raise ValueError(
            "Slug must contain only lowercase letters, numbers, and hyphens, "
            "and must start and end with a letter or number"
        )
    return stripped


def _validate_color_code(value: str) -> str:
    """Validate hex color code format (#RRGGBB)."""
    stripped = value.strip()
    if not _COLOR_CODE_REGEX.match(stripped):
        raise ValueError("Color code must be in #RRGGBB format (e.g., '#FF5722')")
    return stripped.upper()  # Normalize to uppercase hex


def _normalize_skill(value: str) -> str:
    """
    Normalize a skill name for consistent matching.

    Strips whitespace, converts to lowercase, replaces spaces with hyphens.
    Must match WorkerProfile skill normalization.
    """
    normalized = value.strip().lower().replace(" ", "-")
    if not normalized:
        raise ValueError("Skill name cannot be empty")
    if len(normalized) > 100:
        raise ValueError("Skill name must be at most 100 characters")
    return normalized


# ---------------------------------------------------------------------------
# Category Schemas
# ---------------------------------------------------------------------------

class CategoryCreateRequest(BaseModel):
    """
    Create a new service category.

    The service layer should:
        1. Auto-generate slug from name if slug is not provided.
        2. Check slug uniqueness before insert.
        3. Set display_order to max(existing) + 1 if not provided.

    Attributes:
        name: Category display name (required).
        slug: URL-friendly identifier (auto-generated if not provided).
        icon: Icon identifier or URL.
        description: Short category description.
        display_order: Sort position (0 = first).
        is_active: Visibility toggle (default True).
        color_code: Hex color for UI (#RRGGBB).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Category display name",
        examples=["Electrical"],
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
        description="URL-friendly identifier (auto-generated from name if empty)",
        examples=["electrical"],
    )
    icon: str | None = Field(
        default=None,
        max_length=512,
        description="Icon name or URL",
        examples=["electrical_services"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Short category description",
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Sort position (lower = first)",
    )
    is_active: bool = Field(
        default=True,
        description="Visibility toggle",
    )
    color_code: str | None = Field(
        default=None,
        description="Hex color code (#RRGGBB)",
        examples=["#FF5722"],
    )

    # --- Validators ---

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Normalize name: collapse spaces, strip edges."""
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Category name cannot be empty")
        return cleaned

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_slug(value)
        return value

    @field_validator("color_code")
    @classmethod
    def validate_color_code(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_color_code(value)
        return value

    @model_validator(mode="after")
    def auto_generate_slug(self) -> "CategoryCreateRequest":
        """Generate slug from name if not explicitly provided."""
        if self.slug is None:
            self.slug = generate_slug(self.name)
        return self


class CategoryUpdateRequest(BaseModel):
    """
    Partial update for an existing category.

    All fields optional. At least one must be provided.

    Attributes:
        name: Updated display name.
        slug: Updated slug (re-generates if name changes).
        icon: Updated icon.
        description: Updated description.
        display_order: Updated sort position.
        is_active: Updated visibility.
        color_code: Updated color.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated category name",
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
        description="Updated slug",
    )
    icon: str | None = Field(
        default=None,
        max_length=512,
        description="Updated icon",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Updated description",
    )
    display_order: int | None = Field(
        default=None,
        ge=0,
        description="Updated sort position",
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated visibility",
    )
    color_code: str | None = Field(
        default=None,
        description="Updated color code",
    )

    # --- Validators ---

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None:
            cleaned = " ".join(value.split())
            if not cleaned:
                raise ValueError("Category name cannot be empty")
            return cleaned
        return value

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_slug(value)
        return value

    @field_validator("color_code")
    @classmethod
    def validate_color_code(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_color_code(value)
        return value

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "CategoryUpdateRequest":
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
# Service Schemas
# ---------------------------------------------------------------------------

class ServiceCreateRequest(BaseModel):
    """
    Create a new service within a category.

    The service layer should:
        1. Validate category_id exists and is active.
        2. Auto-generate slug from name if not provided.
        3. Set category_slug from the resolved category.
        4. Validate minimum_price ≤ base_market_price ≤ maximum_price.

    Attributes:
        category_id: Reference to ServiceCategory ObjectId.
        name: Service display name (required).
        slug: URL-friendly identifier (auto-generated if not provided).
        description: Detailed service description.
        base_market_price: Standard price in INR.
        minimum_price: Floor price for dynamic pricing.
        maximum_price: Ceiling price for dynamic pricing.
        estimated_duration_minutes: Expected completion time.
        required_experience_years: Minimum worker experience.
        required_skills: Required skill names for matching.
        service_icon: Icon identifier or URL.
        service_image: Hero image URL.
        is_inspection_required: Needs on-site inspection.
        is_emergency_service: Priority dispatch service.
        is_active: Visibility toggle.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: str = Field(
        ...,
        description="ServiceCategory ObjectId",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Service display name",
        examples=["Fan Installation"],
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=220,
        description="URL-friendly identifier (auto-generated if empty)",
        examples=["fan-installation"],
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed service description",
    )

    # --- Pricing ---
    base_market_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Standard market price (INR)",
        examples=[499.0],
    )
    minimum_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Floor price — dynamic pricing minimum (INR)",
        examples=[299.0],
    )
    maximum_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Ceiling price — dynamic pricing maximum (INR)",
        examples=[999.0],
    )

    # --- Duration & Requirements ---
    estimated_duration_minutes: int = Field(
        ...,
        ge=5,
        le=2880,
        description="Expected completion time (minutes)",
        examples=[60],
    )
    required_experience_years: float = Field(
        default=0.0,
        ge=0.0,
        le=30.0,
        description="Minimum worker experience (years)",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Required skill names for worker matching",
        examples=[["fan-installation", "electrical-wiring"]],
    )

    # --- Media ---
    service_icon: str | None = Field(
        default=None,
        max_length=512,
        description="Icon name or URL",
    )
    service_image: str | None = Field(
        default=None,
        max_length=512,
        description="Hero image URL",
    )

    # --- Flags ---
    is_inspection_required: bool = Field(
        default=False,
        description="Requires on-site inspection",
    )
    is_emergency_service: bool = Field(
        default=False,
        description="Priority dispatch service",
    )
    is_active: bool = Field(
        default=True,
        description="Visibility toggle",
    )

    # --- Validators ---

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Normalize name: collapse spaces, strip edges."""
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Service name cannot be empty")
        return cleaned

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_slug(value)
        return value

    @field_validator("required_skills")
    @classmethod
    def normalize_skills(cls, value: list[str]) -> list[str]:
        """Normalize and deduplicate required skills."""
        normalized = [_normalize_skill(s) for s in value]
        return list(dict.fromkeys(normalized))  # Deduplicate, preserve order

    @model_validator(mode="after")
    def auto_generate_slug(self) -> "ServiceCreateRequest":
        """Generate slug from name if not explicitly provided."""
        if self.slug is None:
            self.slug = generate_slug(self.name)
        return self

    @model_validator(mode="after")
    def validate_price_hierarchy(self) -> "ServiceCreateRequest":
        """
        Ensure price ordering: minimum ≤ base ≤ maximum.

        This prevents configuration errors where the floor price
        exceeds the ceiling, or the base price is outside the range.
        """
        if self.minimum_price > self.base_market_price:
            raise ValueError(
                f"minimum_price ({self.minimum_price}) cannot exceed "
                f"base_market_price ({self.base_market_price})"
            )
        if self.base_market_price > self.maximum_price:
            raise ValueError(
                f"base_market_price ({self.base_market_price}) cannot exceed "
                f"maximum_price ({self.maximum_price})"
            )
        return self


class ServiceUpdateRequest(BaseModel):
    """
    Partial update for an existing service.

    All fields optional. At least one must be provided.
    The service layer should:
        - Validate category_id if changed (must exist, must be active).
        - Re-generate slug if name changes and slug is not provided.
        - Re-validate price hierarchy if any price field changes.

    Attributes:
        category_id: Updated category reference.
        name: Updated service name.
        slug: Updated slug.
        description: Updated description.
        base_market_price: Updated base price.
        minimum_price: Updated floor price.
        maximum_price: Updated ceiling price.
        estimated_duration_minutes: Updated duration.
        required_experience_years: Updated experience requirement.
        required_skills: Updated skill requirements.
        service_icon: Updated icon.
        service_image: Updated image.
        is_inspection_required: Updated inspection flag.
        is_emergency_service: Updated emergency flag.
        is_active: Updated visibility.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: str | None = Field(default=None, description="Updated category")
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
        description="Updated service name",
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=220,
        description="Updated slug",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Updated description",
    )

    # --- Pricing ---
    base_market_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Updated base price (INR)",
    )
    minimum_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Updated floor price (INR)",
    )
    maximum_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Updated ceiling price (INR)",
    )

    # --- Duration & Requirements ---
    estimated_duration_minutes: int | None = Field(
        default=None,
        ge=5,
        le=2880,
        description="Updated duration (minutes)",
    )
    required_experience_years: float | None = Field(
        default=None,
        ge=0.0,
        le=30.0,
        description="Updated experience requirement",
    )
    required_skills: list[str] | None = Field(
        default=None,
        max_length=10,
        description="Updated required skills",
    )

    # --- Media ---
    service_icon: str | None = Field(
        default=None,
        max_length=512,
        description="Updated icon",
    )
    service_image: str | None = Field(
        default=None,
        max_length=512,
        description="Updated image",
    )

    # --- Flags ---
    is_inspection_required: bool | None = Field(
        default=None,
        description="Updated inspection flag",
    )
    is_emergency_service: bool | None = Field(
        default=None,
        description="Updated emergency flag",
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated visibility",
    )

    # --- Validators ---

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None:
            cleaned = " ".join(value.split())
            if not cleaned:
                raise ValueError("Service name cannot be empty")
            return cleaned
        return value

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_slug(value)
        return value

    @field_validator("required_skills")
    @classmethod
    def normalize_skills(cls, value: list[str] | None) -> list[str] | None:
        if value is not None:
            normalized = [_normalize_skill(s) for s in value]
            return list(dict.fromkeys(normalized))
        return value

    @model_validator(mode="after")
    def validate_price_hierarchy(self) -> "ServiceUpdateRequest":
        """
        Validate price ordering for provided price fields.

        Only validates when all three prices are provided in the same
        update. Partial price updates are validated by the service layer
        against the existing document values.
        """
        prices = [self.minimum_price, self.base_market_price, self.maximum_price]
        provided_count = sum(1 for p in prices if p is not None)

        if provided_count == 3:
            assert self.minimum_price is not None
            assert self.base_market_price is not None
            assert self.maximum_price is not None
            if self.minimum_price > self.base_market_price:
                raise ValueError(
                    f"minimum_price ({self.minimum_price}) cannot exceed "
                    f"base_market_price ({self.base_market_price})"
                )
            if self.base_market_price > self.maximum_price:
                raise ValueError(
                    f"base_market_price ({self.base_market_price}) cannot exceed "
                    f"maximum_price ({self.maximum_price})"
                )
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ServiceUpdateRequest":
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

class CategoryResponse(BaseModel):
    """
    Category representation in API responses.

    Includes service_count (computed by the service layer via
    aggregation or denormalized counter) for display on category cards.

    Attributes:
        id: Category document ID.
        name: Display name.
        slug: URL-friendly identifier.
        icon: Icon name or URL.
        description: Short description.
        display_order: Sort position.
        is_active: Visibility status.
        color_code: Hex color for UI.
        service_count: Number of active services (computed).
        created_at: Creation time.
        updated_at: Last update time.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="Category ID (MongoDB ObjectId)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL slug")
    icon: str | None = Field(None, description="Icon name or URL")
    description: str | None = Field(None, description="Short description")
    display_order: int = Field(..., description="Sort position")
    is_active: bool = Field(..., description="Visibility status")
    color_code: str | None = Field(None, description="Hex color code")
    service_count: int = Field(default=0, description="Active services in category")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """Convert Beanie PydanticObjectId to plain string."""
        return str(value)


class ServiceResponse(BaseModel):
    """
    Service representation in API responses.

    Includes computed display fields (price_range_display, duration_display)
    and the denormalized category_slug for frontend routing.

    Attributes:
        id: Service document ID.
        category_id: Reference to category.
        category_slug: Denormalized category slug.
        name: Service name.
        slug: URL slug.
        description: Detailed description.
        base_market_price: Standard price (INR).
        minimum_price: Floor price (INR).
        maximum_price: Ceiling price (INR).
        estimated_duration_minutes: Duration (minutes).
        required_experience_years: Minimum experience.
        required_skills: Required skills.
        service_icon: Icon identifier or URL.
        service_image: Image URL.
        is_inspection_required: Inspection flag.
        is_emergency_service: Emergency flag.
        is_active: Visibility status.
        price_range_display: Formatted price range (computed).
        duration_display: Formatted duration (computed).
        created_at: Creation time.
        updated_at: Last update time.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="Service ID (MongoDB ObjectId)",
        examples=["60d5ec49f1a2c8b1f8e4e1a2"],
    )
    category_id: str = Field(..., description="Category reference")
    category_slug: str = Field(..., description="Denormalized category slug")

    # --- Identity ---
    name: str = Field(..., description="Service name")
    slug: str = Field(..., description="URL slug")
    description: str | None = Field(None, description="Detailed description")

    # --- Pricing ---
    base_market_price: float = Field(..., description="Base price (INR)")
    minimum_price: float = Field(..., description="Floor price (INR)")
    maximum_price: float = Field(..., description="Ceiling price (INR)")

    # --- Duration & Requirements ---
    estimated_duration_minutes: int = Field(..., description="Duration (min)")
    required_experience_years: float = Field(..., description="Min experience")
    required_skills: list[str] = Field(
        default_factory=list, description="Required skills",
    )

    # --- Media ---
    service_icon: str | None = Field(None, description="Icon")
    service_image: str | None = Field(None, description="Image URL")

    # --- Flags ---
    is_inspection_required: bool = Field(..., description="Inspection needed")
    is_emergency_service: bool = Field(..., description="Emergency service")
    is_active: bool = Field(..., description="Visibility")

    # --- Computed ---
    price_range_display: str = Field(
        default="", description="Formatted price range (e.g., '₹299 – ₹999')",
    )
    duration_display: str = Field(
        default="", description="Formatted duration (e.g., '1 hr 30 min')",
    )

    # --- Timestamps ---
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """Convert Beanie PydanticObjectId to plain string."""
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def compute_display_fields(cls, data: object) -> object:
        """
        Compute human-readable display fields from raw data.

        For dict inputs (raw MongoDB): compute from numeric values.
        For Beanie Documents: from_attributes reads @property directly.
        """
        if isinstance(data, dict):
            # Price range display
            min_p = data.get("minimum_price", 0)
            max_p = data.get("maximum_price", 0)
            data["price_range_display"] = f"₹{min_p:,.0f} – ₹{max_p:,.0f}"

            # Duration display
            duration = data.get("estimated_duration_minutes", 0)
            if duration < 60:
                data["duration_display"] = f"{duration} min"
            else:
                hours = duration // 60
                minutes = duration % 60
                if minutes == 0:
                    data["duration_display"] = f"{hours} hr"
                else:
                    data["duration_display"] = f"{hours} hr {minutes} min"

        # For Beanie Documents: from_attributes reads @property directly
        return data
