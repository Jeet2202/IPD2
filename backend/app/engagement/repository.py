"""
Database access repositories for Customer Engagement module.
"""

from datetime import datetime, timezone
from typing import Any

from app.engagement.models import Favorite, RecentlyViewed, RecommendationHistory, SavedSearch
from app.engagement.schemas import FavoriteType, ItemType


class FavoriteRepository:
    """DB Repository for customer favorites."""

    @staticmethod
    async def add_favorite(data: dict[str, Any]) -> Favorite:
        """Create a new favorite entry."""
        fav = Favorite(**data)
        await fav.insert()
        return fav

    @staticmethod
    async def get_by_id(favorite_id: str) -> Favorite | None:
        """Get favorite by favorite_id."""
        return await Favorite.find_one(Favorite.favorite_id == favorite_id)

    @staticmethod
    async def get_by_user_and_target(user_id: str, target_type: FavoriteType, target_id: str) -> Favorite | None:
        """Find favorite entry for specific user, target type, and target ID."""
        return await Favorite.find_one(
            Favorite.user_id == str(user_id),
            Favorite.target_type == target_type,
            Favorite.target_id == str(target_id),
        )

    @staticmethod
    async def list_by_user(
        user_id: str,
        target_type: FavoriteType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Favorite]:
        """List favorite records for a user."""
        query = {"user_id": str(user_id)}
        if target_type:
            query["target_type"] = target_type

        return await Favorite.find(query).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_by_user(user_id: str, target_type: FavoriteType | None = None) -> int:
        """Count favorite records for a user."""
        query = {"user_id": str(user_id)}
        if target_type:
            query["target_type"] = target_type
        return await Favorite.find(query).count()

    @staticmethod
    async def delete_favorite(favorite_id: str, user_id: str) -> bool:
        """Delete a favorite record owned by user."""
        fav = await Favorite.find_one(
            Favorite.favorite_id == str(favorite_id),
            Favorite.user_id == str(user_id),
        )
        if fav:
            await fav.delete()
            return True
        return False


class RecentlyViewedRepository:
    """DB Repository for recently viewed items."""

    @staticmethod
    async def log_view(user_id: str, item_type: ItemType, item_id: str, metadata: dict[str, Any] | None = None) -> RecentlyViewed:
        """Upsert recently viewed item entry."""
        user_id_str = str(user_id)
        item_id_str = str(item_id)
        existing = await RecentlyViewed.find_one(
            RecentlyViewed.user_id == user_id_str,
            RecentlyViewed.item_type == item_type,
            RecentlyViewed.item_id == item_id_str,
        )

        now = datetime.now(timezone.utc)
        if existing:
            existing.viewed_at = now
            if metadata:
                existing.metadata = {**existing.metadata, **metadata}
            await existing.save()
            return existing

        item = RecentlyViewed(
            user_id=user_id_str,
            item_type=item_type,
            item_id=item_id_str,
            viewed_at=now,
            metadata=metadata or {},
        )
        await item.insert()
        return item

    @staticmethod
    async def list_by_user(
        user_id: str,
        item_type: ItemType | None = None,
        limit: int = 20,
    ) -> list[RecentlyViewed]:
        """List recently viewed items for a user."""
        query = {"user_id": str(user_id)}
        if item_type:
            query["item_type"] = item_type
        return await RecentlyViewed.find(query).sort("-viewed_at").limit(limit).to_list()

    @staticmethod
    async def clear_by_user(user_id: str) -> int:
        """Clear all recently viewed items for user."""
        res = await RecentlyViewed.find(RecentlyViewed.user_id == str(user_id)).delete()
        return res.deleted_count if res else 0


class SavedSearchRepository:
    """DB Repository for saved search presets."""

    @staticmethod
    async def save_search(data: dict[str, Any]) -> SavedSearch:
        """Create a new saved search entry."""
        search = SavedSearch(**data)
        await search.insert()
        return search

    @staticmethod
    async def get_by_id(search_id: str) -> SavedSearch | None:
        """Get saved search by search_id."""
        return await SavedSearch.find_one(SavedSearch.search_id == str(search_id))

    @staticmethod
    async def list_by_user(user_id: str, skip: int = 0, limit: int = 50) -> list[SavedSearch]:
        """List saved searches for a user."""
        return await SavedSearch.find(SavedSearch.user_id == str(user_id)).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """Count saved searches for a user."""
        return await SavedSearch.find(SavedSearch.user_id == str(user_id)).count()

    @staticmethod
    async def delete_search(search_id: str, user_id: str) -> bool:
        """Delete a saved search record owned by user."""
        search = await SavedSearch.find_one(
            SavedSearch.search_id == str(search_id),
            SavedSearch.user_id == str(user_id),
        )
        if search:
            await search.delete()
            return True
        return False


class RecommendationHistoryRepository:
    """DB Repository for recommendation history."""

    @staticmethod
    async def create_history(data: dict[str, Any]) -> RecommendationHistory:
        """Store recommendation output."""
        rec = RecommendationHistory(**data)
        await rec.insert()
        return rec

    @staticmethod
    async def get_latest_by_user(user_id: str) -> RecommendationHistory | None:
        """Fetch most recent recommendation history entry."""
        return await RecommendationHistory.find(RecommendationHistory.user_id == str(user_id)).sort("-generated_at").first_or_none()
