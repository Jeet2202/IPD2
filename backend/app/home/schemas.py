"""
Home Schemas — DTO for aggregated Customer Home API response.
"""

from pydantic import BaseModel, ConfigDict, Field
from app.category.schemas import CategoryResponse
from app.service.schemas import ServiceResponse


class HomeResponse(BaseModel):
    """
    Unified payload aggregating home screen components in a single API call.
    """

    model_config = ConfigDict(from_attributes=True)

    featured_categories: list[CategoryResponse] = Field(
        default_factory=list,
        description="Top active categories for home grid (max 8)",
    )
    featured_services: list[ServiceResponse] = Field(
        default_factory=list,
        description="Active featured services for hero carousel",
    )
    popular_services: list[ServiceResponse] = Field(
        default_factory=list,
        description="Popular active services",
    )
    recommended_services: list[ServiceResponse] = Field(
        default_factory=list,
        description="Recommended active services (AI recommendation placeholder)",
    )
    recent_services: list[ServiceResponse] = Field(
        default_factory=list,
        description="Newest active services (sorted by created_at desc)",
    )
