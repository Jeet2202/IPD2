"""
Unit tests for Customer Engagement module (Phase 9.1).
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.engagement.schemas import (
    FavoriteCreate,
    FavoriteType,
    ItemType,
    RecentlyViewedCreate,
    SavedSearchCreate,
)
from app.engagement.service import (
    FavoritesService,
    PersonalizationService,
    RecentlyViewedService,
    RecommendationService,
    SavedSearchesService,
)


@pytest.mark.asyncio
async def test_favorites_workflow():
    """Test adding, listing, checking, and removing favorite workers/services."""
    user_id = "cust_fav_test_user_123"

    mock_fav1 = MagicMock(favorite_id="fav_001", user_id=user_id, target_type=FavoriteType.WORKER, target_id="worker_456", notes="Great plumber")
    mock_fav2 = MagicMock(favorite_id="fav_002", user_id=user_id, target_type=FavoriteType.SERVICE, target_id="cat_electrical_789", notes=None)

    with patch("app.engagement.repository.FavoriteRepository.get_by_user_and_target", new_callable=AsyncMock) as mock_get_target, \
         patch("app.engagement.repository.FavoriteRepository.add_favorite", new_callable=AsyncMock) as mock_add, \
         patch("app.engagement.repository.FavoriteRepository.list_by_user", new_callable=AsyncMock) as mock_list, \
         patch("app.engagement.repository.FavoriteRepository.count_by_user", new_callable=AsyncMock) as mock_count, \
         patch("app.engagement.repository.FavoriteRepository.delete_favorite", new_callable=AsyncMock) as mock_delete, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        mock_get_target.side_effect = [None, mock_fav1]
        mock_add.return_value = mock_fav1
        mock_list.return_value = [mock_fav1, mock_fav2]
        mock_count.side_effect = [2, 1, 1]
        mock_delete.return_value = True

        # Add favorite worker
        fav1 = await FavoritesService.add_favorite(
            user_id=user_id,
            req=FavoriteCreate(target_type=FavoriteType.WORKER, target_id="worker_456", notes="Great plumber"),
        )
        assert fav1.favorite_id == "fav_001"
        assert fav1.target_type == FavoriteType.WORKER

        # Check is_favorited
        is_fav = await FavoritesService.is_favorited(user_id, FavoriteType.WORKER, "worker_456")
        assert is_fav is True

        # List favorites
        fav_list = await FavoritesService.list_favorites(user_id=user_id)
        assert fav_list.total_count == 2

        # Remove favorite
        removed = await FavoritesService.remove_favorite("fav_001", user_id)
        assert removed is True


@pytest.mark.asyncio
async def test_recently_viewed_workflow():
    """Test logging and listing recently viewed items."""
    user_id = "cust_view_test_user_123"

    mock_view1 = MagicMock(view_id="view_001", user_id=user_id, item_type=ItemType.WORKER, item_id="worker_789", metadata={"source": "search"})
    mock_view2 = MagicMock(view_id="view_002", user_id=user_id, item_type=ItemType.SERVICE, item_id="srv_cleaning_001", metadata={})

    with patch("app.engagement.repository.RecentlyViewedRepository.log_view", new_callable=AsyncMock) as mock_log, \
         patch("app.engagement.repository.RecentlyViewedRepository.list_by_user", new_callable=AsyncMock) as mock_list, \
         patch("app.engagement.repository.RecentlyViewedRepository.clear_by_user", new_callable=AsyncMock) as mock_clear:

        mock_log.return_value = mock_view1
        mock_list.return_value = [mock_view1, mock_view2]
        mock_clear.return_value = 2

        v1 = await RecentlyViewedService.log_view(
            user_id=user_id,
            req=RecentlyViewedCreate(item_type=ItemType.WORKER, item_id="worker_789", metadata={"source": "search"}),
        )
        assert v1.view_id == "view_001"

        recent = await RecentlyViewedService.get_recently_viewed(user_id)
        assert len(recent) == 2

        cleared = await RecentlyViewedService.clear_recently_viewed(user_id)
        assert cleared == 2


@pytest.mark.asyncio
async def test_saved_searches_workflow():
    """Test saving and listing search presets."""
    user_id = "cust_search_test_user_123"

    mock_search = MagicMock()
    mock_search.search_id = "search_001"
    mock_search.user_id = user_id
    mock_search.name = "Emergency Electrician Mumbai"
    mock_search.query = "electrician"
    mock_search.category_id = "cat_electrical"
    mock_search.filters = {"urgency": "high"}
    mock_search.created_at = "2026-08-04T12:00:00Z"

    with patch("app.engagement.repository.SavedSearchRepository.save_search", new_callable=AsyncMock) as mock_save, \
         patch("app.engagement.repository.SavedSearchRepository.list_by_user", new_callable=AsyncMock) as mock_list, \
         patch("app.engagement.repository.SavedSearchRepository.delete_search", new_callable=AsyncMock) as mock_delete:

        mock_save.return_value = mock_search
        mock_list.return_value = [mock_search]
        mock_delete.return_value = True

        s1 = await SavedSearchesService.save_search(
            user_id=user_id,
            req=SavedSearchCreate(name="Emergency Electrician Mumbai", query="electrician", category_id="cat_electrical"),
        )
        assert s1.search_id == "search_001"

        searches = await SavedSearchesService.list_saved_searches(user_id)
        assert len(searches) == 1

        deleted = await SavedSearchesService.delete_saved_search("search_001", user_id)
        assert deleted is True


@pytest.mark.asyncio
async def test_personalization_and_home_feed():
    """Test personalized recommendations and home feed aggregation."""
    user_id = "cust_pers_test_user_123"

    mock_recent = [MagicMock(view_id="view_001", user_id=user_id, item_type=ItemType.SERVICE, item_id="srv_ac_repair", metadata={})]

    with patch("app.engagement.service.RecentlyViewedService.get_recently_viewed", new_callable=AsyncMock) as mock_recent_svc, \
         patch("app.engagement.repository.FavoriteRepository.list_by_user", new_callable=AsyncMock, return_value=[]), \
         patch("app.engagement.repository.FavoriteRepository.count_by_user", new_callable=AsyncMock, return_value=0), \
         patch("app.engagement.repository.SavedSearchRepository.count_by_user", new_callable=AsyncMock, return_value=0), \
         patch("app.engagement.repository.RecommendationHistoryRepository.create_history", new_callable=AsyncMock):

        mock_recent_svc.return_value = mock_recent

        recs = await RecommendationService.generate_recommendations(user_id)
        assert len(recs) >= 3

        home = await PersonalizationService.get_personalized_home(user_id)
        assert home.user_id == user_id
        assert len(home.continue_browsing) == 1
        assert len(home.recommendations) >= 3
