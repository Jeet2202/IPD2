"""
Domain services for Customer Engagement module.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from app.booking.models import Booking
from app.core.exceptions import BadRequestException, NotFoundException
from app.engagement.models import Favorite, RecentlyViewed, SavedSearch
from app.engagement.repository import (
    FavoriteRepository,
    RecentlyViewedRepository,
    RecommendationHistoryRepository,
    SavedSearchRepository,
)
from app.engagement.schemas import (
    FavoriteCreate,
    FavoriteListRead,
    FavoriteRead,
    FavoriteType,
    ItemType,
    PersonalizedHomeRead,
    QuickRebookItemRead,
    RecentlyViewedCreate,
    RecentlyViewedRead,
    RecommendationItem,
    RecommendationRead,
    SavedSearchCreate,
    SavedSearchRead,
)
from app.trust.schemas import AuditEventType
from app.trust.service import AuditService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Favorites Service
# ---------------------------------------------------------------------------

class FavoritesService:
    """Manages customer favorited workers and services."""

    @staticmethod
    async def add_favorite(user_id: str, req: FavoriteCreate) -> FavoriteRead:
        """Add worker or service to favorites."""
        user_id_str = str(user_id)
        existing = await FavoriteRepository.get_by_user_and_target(
            user_id=user_id_str, target_type=req.target_type, target_id=req.target_id
        )
        if existing:
            return FavoriteRead.model_validate(existing)

        fav = await FavoriteRepository.add_favorite({
            "user_id": user_id_str,
            "target_type": req.target_type,
            "target_id": str(req.target_id),
            "notes": req.notes,
        })

        await AuditService.log_event(
            user_id=user_id_str,
            event_type=AuditEventType.PROFILE_UPDATES,
            description=f"Added {req.target_type.value} [{req.target_id}] to favorites",
            actor={"id": user_id_str, "role": "customer"},
            metadata={"favorite_id": fav.favorite_id, "target_type": req.target_type.value},
        )
        return FavoriteRead.model_validate(fav)

    @staticmethod
    async def remove_favorite(favorite_id: str, user_id: str) -> bool:
        """Remove item from favorites."""
        success = await FavoriteRepository.delete_favorite(favorite_id=favorite_id, user_id=user_id)
        if not success:
            raise NotFoundException(f"Favorite '{favorite_id}' not found or access denied.")
        return True

    @staticmethod
    async def list_favorites(
        user_id: str,
        target_type: FavoriteType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> FavoriteListRead:
        """List favorite workers and services for user."""
        user_id_str = str(user_id)
        favorites = await FavoriteRepository.list_by_user(
            user_id=user_id_str, target_type=target_type, skip=skip, limit=limit
        )
        total = await FavoriteRepository.count_by_user(user_id=user_id_str, target_type=target_type)
        w_count = await FavoriteRepository.count_by_user(user_id=user_id_str, target_type=FavoriteType.WORKER)
        s_count = await FavoriteRepository.count_by_user(user_id=user_id_str, target_type=FavoriteType.SERVICE)

        fav_dtos = [FavoriteRead.model_validate(f) for f in favorites]
        return FavoriteListRead(
            favorites=fav_dtos,
            total_count=total,
            worker_count=w_count,
            service_count=s_count,
        )

    @staticmethod
    async def is_favorited(user_id: str, target_type: FavoriteType, target_id: str) -> bool:
        """Check if an item is favorited by user."""
        fav = await FavoriteRepository.get_by_user_and_target(user_id, target_type, target_id)
        return fav is not None


# ---------------------------------------------------------------------------
# Recently Viewed Service
# ---------------------------------------------------------------------------

class RecentlyViewedService:
    """Tracks and retrieves recently browsed workers and services."""

    @staticmethod
    async def log_view(user_id: str, req: RecentlyViewedCreate) -> RecentlyViewedRead:
        """Log a recently viewed worker or service."""
        user_id_str = str(user_id)
        item = await RecentlyViewedRepository.log_view(
            user_id=user_id_str,
            item_type=req.item_type,
            item_id=req.item_id,
            metadata=req.metadata,
        )
        return RecentlyViewedRead.model_validate(item)

    @staticmethod
    async def get_recently_viewed(
        user_id: str,
        item_type: ItemType | None = None,
        limit: int = 20,
    ) -> list[RecentlyViewedRead]:
        """Fetch recently viewed items."""
        items = await RecentlyViewedRepository.list_by_user(user_id=str(user_id), item_type=item_type, limit=limit)
        return [RecentlyViewedRead.model_validate(i) for i in items]

    @staticmethod
    async def clear_recently_viewed(user_id: str) -> int:
        """Clear user view history."""
        return await RecentlyViewedRepository.clear_by_user(str(user_id))


# ---------------------------------------------------------------------------
# Saved Searches Service
# ---------------------------------------------------------------------------

class SavedSearchesService:
    """Manages saved search presets."""

    @staticmethod
    async def save_search(user_id: str, req: SavedSearchCreate) -> SavedSearchRead:
        """Save a search preset."""
        user_id_str = str(user_id)
        search = await SavedSearchRepository.save_search({
            "user_id": user_id_str,
            "name": req.name,
            "query": req.query,
            "category_id": req.category_id,
            "filters": req.filters,
        })
        return SavedSearchRead.model_validate(search)

    @staticmethod
    async def list_saved_searches(user_id: str, skip: int = 0, limit: int = 50) -> list[SavedSearchRead]:
        """List saved search presets for user."""
        searches = await SavedSearchRepository.list_by_user(user_id=str(user_id), skip=skip, limit=limit)
        return [SavedSearchRead.model_validate(s) for s in searches]

    @staticmethod
    async def delete_saved_search(search_id: str, user_id: str) -> bool:
        """Delete a saved search preset."""
        success = await SavedSearchRepository.delete_search(search_id=search_id, user_id=user_id)
        if not success:
            raise NotFoundException(f"Saved search '{search_id}' not found or access denied.")
        return True


# ---------------------------------------------------------------------------
# Recommendation Service
# ---------------------------------------------------------------------------

class RecommendationService:
    """Generates personalized worker and service recommendations."""

    @staticmethod
    async def generate_recommendations(user_id: str) -> list[RecommendationItem]:
        """Generate personalized items based on recent views and favorites."""
        user_id_str = str(user_id)

        recent_views = await RecentlyViewedService.get_recently_viewed(user_id_str, limit=5)
        favorites = await FavoriteRepository.list_by_user(user_id_str, limit=10)

        # Baseline popular recommendation items
        recommendations = [
            RecommendationItem(
                item_id="srv_home_cleaning",
                item_type=ItemType.SERVICE,
                title="Deep Home Cleaning",
                rating=4.9,
                reason="Popular choice in your area",
            ),
            RecommendationItem(
                item_id="srv_electrical_repair",
                item_type=ItemType.SERVICE,
                title="Electrical Fitting & Repair",
                rating=4.8,
                reason="Top rated emergency service",
            ),
            RecommendationItem(
                item_id="srv_plumbing_leak",
                item_type=ItemType.SERVICE,
                title="Plumbing Leak Fix",
                rating=4.8,
                reason="Recommended based on popular demand",
            ),
        ]

        if recent_views:
            first_view = recent_views[0]
            recommendations.insert(
                0,
                RecommendationItem(
                    item_id=f"rec_{first_view.item_id}",
                    item_type=first_view.item_type,
                    title=f"Related to your recent view ({first_view.item_id})",
                    rating=5.0,
                    reason="Based on your recent browsing",
                ),
            )

        # Record snapshot in DB
        await RecommendationHistoryRepository.create_history({
            "user_id": user_id_str,
            "recommendation_type": "personalized_home",
            "item_ids": [r.item_id for r in recommendations],
        })

        return recommendations[:5]


# ---------------------------------------------------------------------------
# Personalization Service
# ---------------------------------------------------------------------------

class PersonalizationService:
    """Orchestrates personalized home feeds, continue browsing, and quick rebooking."""

    @staticmethod
    async def get_personalized_home(user_id: str) -> PersonalizedHomeRead:
        """Construct personalized home feed."""
        user_id_str = str(user_id)

        # 1. Continue Browsing (top 5 recent views)
        continue_browsing = await RecentlyViewedService.get_recently_viewed(user_id_str, limit=5)

        # 2. Favorite & Saved Counts
        w_fav_count = await FavoriteRepository.count_by_user(user_id_str, target_type=FavoriteType.WORKER)
        s_fav_count = await FavoriteRepository.count_by_user(user_id_str, target_type=FavoriteType.SERVICE)
        saved_searches_count = await SavedSearchRepository.count_by_user(user_id_str)

        # 3. Quick Rebooking (from user's past bookings if existing)
        quick_rebook: list[QuickRebookItemRead] = []
        try:
            past_bookings = await Booking.find(Booking.customer_id == user_id_str).sort("-created_at").limit(3).to_list()
            for b in past_bookings:
                quick_rebook.append(
                    QuickRebookItemRead(
                        booking_id=str(b.id),
                        service_id=str(getattr(b, "service_id", "service_default")),
                        service_title=getattr(b, "title", "Completed Home Service"),
                        worker_id=str(getattr(b, "worker_id", "worker_default")),
                        worker_name="Assigned Skilled Professional",
                        last_booked_at=getattr(b, "created_at", datetime.now(timezone.utc)),
                    )
                )
        except Exception as e:
            logger.debug("Quick rebooking query skipped: %s", str(e))

        # 4. Personalized Recommendations
        recommendations = await RecommendationService.generate_recommendations(user_id_str)

        return PersonalizedHomeRead(
            user_id=user_id_str,
            continue_browsing=continue_browsing,
            quick_rebook=quick_rebook,
            favorite_workers_count=w_fav_count,
            favorite_services_count=s_fav_count,
            saved_searches_count=saved_searches_count,
            recommendations=recommendations,
        )
