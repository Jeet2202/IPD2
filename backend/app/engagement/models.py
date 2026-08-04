"""
Beanie ODM document models for Customer Engagement module.
"""

from datetime import datetime, timezone
from typing import Any
import uuid

from beanie import Document, Indexed
from pydantic import Field

from app.engagement.schemas import FavoriteType, ItemType


class Favorite(Document):
    """Stores customer favorited workers and services."""
    favorite_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    target_type: FavoriteType
    target_id: Indexed(str)
    notes: str | None = None
    created_at: Indexed(datetime) = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "favorites"
        indexes = [
            [("user_id", 1), ("target_type", 1), ("target_id", 1)],
            [("user_id", 1), ("created_at", -1)],
        ]


class RecentlyViewed(Document):
    """Stores history of recently viewed workers and services."""
    view_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    item_type: ItemType
    item_id: Indexed(str)
    viewed_at: Indexed(datetime) = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "recently_viewed"
        indexes = [
            [("user_id", 1), ("item_type", 1), ("item_id", 1)],
            [("user_id", 1), ("viewed_at", -1)],
        ]


class SavedSearch(Document):
    """Stores saved search queries and filters for rapid execution."""
    search_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    name: str
    query: str | None = None
    category_id: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    created_at: Indexed(datetime) = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "saved_searches"
        indexes = [
            [("user_id", 1), ("created_at", -1)],
        ]


class RecommendationHistory(Document):
    """Stores historical personalization recommendation outputs."""
    recommendation_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Indexed(str)
    recommendation_type: str = Field(default="personalized_home")
    item_ids: list[str] = Field(default_factory=list)
    generated_at: Indexed(datetime) = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "recommendation_history"
        indexes = [
            [("user_id", 1), ("generated_at", -1)],
        ]
