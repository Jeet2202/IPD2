"""
Pydantic v2 schemas and Enums for Customer Engagement module.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FavoriteType(str, Enum):
    """Types of favorited entities."""
    WORKER = "worker"
    SERVICE = "service"


class ItemType(str, Enum):
    """Types of browsed entities."""
    WORKER = "worker"
    SERVICE = "service"


# ---------------------------------------------------------------------------
# Favorites DTOs
# ---------------------------------------------------------------------------

class FavoriteCreate(BaseModel):
    """Payload to add an item to favorites."""
    target_type: FavoriteType
    target_id: str = Field(..., description="Worker User ID or Service Category ID")
    notes: str | None = Field(default=None, max_length=500, description="Optional user note")


class FavoriteRead(BaseModel):
    """Read DTO for a favorite entry."""
    id: PyObjectId
    favorite_id: str
    user_id: str
    target_type: FavoriteType
    target_id: str
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FavoriteListRead(BaseModel):
    """Paginated or categorized list of favorites."""
    favorites: list[FavoriteRead]
    total_count: int
    worker_count: int
    service_count: int


# ---------------------------------------------------------------------------
# Recently Viewed DTOs
# ---------------------------------------------------------------------------

class RecentlyViewedCreate(BaseModel):
    """Payload to log a recently viewed item."""
    item_type: ItemType
    item_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecentlyViewedRead(BaseModel):
    """Read DTO for recently viewed entry."""
    id: PyObjectId
    view_id: str
    user_id: str
    item_type: ItemType
    item_id: str
    viewed_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Saved Search DTOs
# ---------------------------------------------------------------------------

class SavedSearchCreate(BaseModel):
    """Payload to save a search query and filter criteria."""
    name: str = Field(..., max_length=100, description="User-friendly name for saved search")
    query: str | None = Field(default=None, max_length=200)
    category_id: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)


class SavedSearchRead(BaseModel):
    """Read DTO for a saved search."""
    id: PyObjectId
    search_id: str
    user_id: str
    name: str
    query: str | None = None
    category_id: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Personalization & Home Feed DTOs
# ---------------------------------------------------------------------------

class QuickRebookItemRead(BaseModel):
    """Quick rebooking suggestion based on past bookings."""
    booking_id: str
    service_id: str | None = None
    service_title: str
    worker_id: str | None = None
    worker_name: str | None = None
    last_booked_at: datetime


class RecommendationItem(BaseModel):
    """Individual item inside a recommendation response."""
    item_id: str
    item_type: ItemType
    title: str
    rating: float = 5.0
    reason: str


class RecommendationRead(BaseModel):
    """Recommendations response DTO."""
    recommendation_id: str
    user_id: str
    recommendation_type: str
    items: list[RecommendationItem] = Field(default_factory=list)
    generated_at: datetime


class PersonalizedHomeRead(BaseModel):
    """Personalized customer home feed response."""
    user_id: str
    continue_browsing: list[RecentlyViewedRead] = Field(default_factory=list)
    quick_rebook: list[QuickRebookItemRead] = Field(default_factory=list)
    favorite_workers_count: int = 0
    favorite_services_count: int = 0
    saved_searches_count: int = 0
    recommendations: list[RecommendationItem] = Field(default_factory=list)
