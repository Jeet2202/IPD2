"""
Service Schemas — Pydantic DTOs for service creation, updates, and responses.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.category.models import generate_slug


def _clean_str_list(items: list[str] | None) -> list[str]:
    """Clean, lowercase, strip, and deduplicate list of strings."""
    if not items:
        return []
    cleaned = []
    for item in items:
        s = item.strip().lower()
        if s and s not in cleaned:
            cleaned.append(s)
    return cleaned


class CreateServiceRequest(BaseModel):
    """
    DTO for creating a new Service under a Category.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: str = Field(
        ...,
        description="ServiceCategory ObjectId string",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    title: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Service display title",
        examples=["Fan Installation"],
    )
    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=220,
        description="URL-friendly identifier (auto-generated if empty)",
    )
    short_description: str | None = Field(
        default=None,
        max_length=500,
        description="Short service summary",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed service description",
    )
    base_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Base market price in INR",
        examples=[499.0],
    )
    minimum_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Minimum dynamic price floor in INR",
    )
    maximum_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Maximum dynamic price ceiling in INR",
    )
    estimated_duration_minutes: int = Field(
        ...,
        gt=0,
        le=2880,
        description="Expected completion time in minutes",
        examples=[60],
    )
    service_image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary or CDN image URL",
    )
    service_image_public_id: str | None = Field(
        default=None,
        max_length=256,
        description="Cloudinary public ID",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Searchable tags",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Search keywords",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Required worker skills",
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Display sort order",
    )
    is_featured: bool = Field(
        default=False,
        description="Featured service status",
    )
    is_active: bool = Field(
        default=True,
        description="Active visibility status",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        cleaned = " ".join(v.split())
        if not cleaned:
            raise ValueError("Service title cannot be empty")
        return cleaned

    @field_validator("tags", "keywords", "required_skills")
    @classmethod
    def validate_str_lists(cls, v: list[str] | None) -> list[str]:
        return _clean_str_list(v)

    @model_validator(mode="after")
    def auto_slug_and_prices(self) -> "CreateServiceRequest":
        if not self.slug:
            self.slug = generate_slug(self.title)
        if self.minimum_price is None:
            self.minimum_price = self.base_price
        if self.maximum_price is None:
            self.maximum_price = self.base_price
        if self.minimum_price > self.base_price:
            raise ValueError(f"minimum_price ({self.minimum_price}) cannot exceed base_price ({self.base_price})")
        if self.base_price > self.maximum_price:
            raise ValueError(f"base_price ({self.base_price}) cannot exceed maximum_price ({self.maximum_price})")
        return self


class UpdateServiceRequest(BaseModel):
    """
    DTO for partial updates to an existing Service.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: str | None = Field(default=None, description="Updated category ObjectId")
    title: str | None = Field(default=None, min_length=2, max_length=200, description="Updated title")
    slug: str | None = Field(default=None, min_length=2, max_length=220, description="Updated slug")
    short_description: str | None = Field(default=None, max_length=500, description="Updated short description")
    description: str | None = Field(default=None, max_length=2000, description="Updated detailed description")
    base_price: float | None = Field(default=None, ge=0.0, le=500000.0, description="Updated base price")
    minimum_price: float | None = Field(default=None, ge=0.0, le=500000.0, description="Updated min price")
    maximum_price: float | None = Field(default=None, ge=0.0, le=500000.0, description="Updated max price")
    estimated_duration_minutes: int | None = Field(default=None, gt=0, le=2880, description="Updated duration")
    service_image_url: str | None = Field(default=None, max_length=1024, description="Updated image URL")
    service_image_public_id: str | None = Field(default=None, max_length=256, description="Updated public ID")
    tags: list[str] | None = Field(default=None, description="Updated tags")
    keywords: list[str] | None = Field(default=None, description="Updated keywords")
    required_skills: list[str] | None = Field(default=None, description="Updated skills")
    display_order: int | None = Field(default=None, ge=0, description="Updated display order")
    is_featured: bool | None = Field(default=None, description="Updated featured flag")
    is_active: bool | None = Field(default=None, description="Updated visibility flag")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = " ".join(v.split())
            if not cleaned:
                raise ValueError("Service title cannot be empty")
            return cleaned
        return v

    @field_validator("tags", "keywords", "required_skills")
    @classmethod
    def validate_str_lists(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            return _clean_str_list(v)
        return v

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UpdateServiceRequest":
        provided = {k for k, v in self.model_dump().items() if v is not None}
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


class ServiceResponse(BaseModel):
    """
    Response representation for a Service.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Service ObjectId string")
    category_id: str = Field(..., description="Parent category ObjectId string")
    category_slug: str = Field(..., description="Denormalized parent category slug")
    title: str = Field(..., description="Service title")
    slug: str = Field(..., description="Service URL slug")
    short_description: str | None = Field(None, description="Short summary")
    description: str | None = Field(None, description="Detailed description")
    base_price: float = Field(..., description="Base price in INR")
    minimum_price: float = Field(..., description="Floor price")
    maximum_price: float = Field(..., description="Ceiling price")
    estimated_duration_minutes: int = Field(..., description="Duration in minutes")
    service_image_url: str | None = Field(None, description="Cloudinary image URL")
    service_image_public_id: str | None = Field(None, description="Cloudinary public ID")
    whats_included: list[str] = Field(default_factory=list, description="Items included in service")
    whats_not_included: list[str] = Field(default_factory=list, description="Items excluded from service")
    tags: list[str] = Field(default_factory=list, description="Search tags")
    keywords: list[str] = Field(default_factory=list, description="Search keywords")
    required_skills: list[str] = Field(default_factory=list, description="Required worker skills")
    display_order: int = Field(..., description="Display sort order")
    is_featured: bool = Field(..., description="Featured service status")
    is_active: bool = Field(..., description="Active visibility status")
    price_range_display: str = Field(default="", description="Formatted price display string")
    duration_display: str = Field(default="", description="Formatted duration display string")
    created_at: datetime = Field(..., description="Creation UTC timestamp")
    updated_at: datetime = Field(..., description="Last modification UTC timestamp")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, v: object) -> str:
        return str(v)

    @model_validator(mode="before")
    @classmethod
    def map_aliases_and_computed_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            # Map title from name
            if "title" not in data and "name" in data:
                data["title"] = data["name"]
            # Map base_price from base_market_price
            if "base_price" not in data and "base_market_price" in data:
                data["base_price"] = data["base_market_price"]
            # Map image URL
            if "service_image_url" not in data and "service_image" in data:
                data["service_image_url"] = data["service_image"]

            # Whats included / not included fallbacks if empty
            if not data.get("whats_included"):
                data["whats_included"] = [
                    "Professional technician service & labor",
                    "Standard inspection & diagnostic check",
                    "Post-service operational testing",
                    "Workplace cleanup after service completion",
                ]
            if not data.get("whats_not_included"):
                data["whats_not_included"] = [
                    "Spare parts & replacement materials (charged at MRP)",
                    "Major structural modifications or masonry works",
                    "Statutory taxes & third-party fees if applicable",
                ]

            # Compute price range display
            min_p = data.get("minimum_price") or data.get("base_price", 0)
            max_p = data.get("maximum_price") or data.get("base_price", 0)
            data["price_range_display"] = f"₹{min_p:,.0f} – ₹{max_p:,.0f}"

            # Compute duration display
            duration = data.get("estimated_duration_minutes", 0)
            if duration < 60:
                data["duration_display"] = f"{duration} min"
            else:
                h = duration // 60
                m = duration % 60
                data["duration_display"] = f"{h} hr" if m == 0 else f"{h} hr {m} min"
        return data


class ServiceListResponse(BaseModel):
    """
    List response wrapper for Services with pagination metadata.
    """

    items: list[ServiceResponse] = Field(default_factory=list, description="List of services")
    total: int = Field(..., description="Total count")
    page: int = Field(default=1, description="Current page number")
    limit: int = Field(default=10, description="Items per page")
    pages: int = Field(default=1, description="Total number of pages")
