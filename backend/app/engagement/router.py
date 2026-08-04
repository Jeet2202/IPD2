"""
REST API endpoints for Customer Engagement module.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import ActiveUserDep
from app.engagement.schemas import (
    FavoriteCreate,
    FavoriteListRead,
    FavoriteRead,
    FavoriteType,
    ItemType,
    PersonalizedHomeRead,
    RecentlyViewedCreate,
    RecentlyViewedRead,
    RecommendationItem,
    SavedSearchCreate,
    SavedSearchRead,
)
from app.engagement.service import (
    FavoritesService,
    PersonalizationService,
    RecentlyViewedService,
    RecommendationService,
    SavedSearchesService,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. GET /engagement/home
# ---------------------------------------------------------------------------

@router.get(
    "/home",
    response_model=PersonalizedHomeRead,
    summary="Get personalized home feed",
    description="Retrieve personalized customer home feed including continue browsing, quick rebooking, favorite counts, and recommendations.",
)
async def get_personalized_home(current_user: ActiveUserDep) -> PersonalizedHomeRead:
    """Get personalized home feed."""
    return await PersonalizationService.get_personalized_home(str(current_user.id))


# ---------------------------------------------------------------------------
# 2. Favorites Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/favorites",
    response_model=FavoriteListRead,
    summary="List user favorites",
    description="Retrieve user's favorite workers and services.",
)
async def list_favorites(
    current_user: ActiveUserDep,
    target_type: FavoriteType | None = Query(default=None, description="Filter by favorite target type"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> FavoriteListRead:
    """List favorites."""
    return await FavoritesService.list_favorites(
        user_id=str(current_user.id), target_type=target_type, skip=skip, limit=limit
    )


@router.post(
    "/favorites",
    response_model=FavoriteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add to favorites",
    description="Add a worker or service to user favorites.",
)
async def add_favorite(
    current_user: ActiveUserDep,
    req: FavoriteCreate,
) -> FavoriteRead:
    """Add favorite."""
    return await FavoritesService.add_favorite(user_id=str(current_user.id), req=req)


@router.delete(
    "/favorites/{favorite_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove from favorites",
    description="Remove an item from user favorites.",
)
async def remove_favorite(
    current_user: ActiveUserDep,
    favorite_id: str,
) -> dict[str, str]:
    """Remove favorite."""
    await FavoritesService.remove_favorite(favorite_id=favorite_id, user_id=str(current_user.id))
    return {"message": f"Favorite '{favorite_id}' removed successfully."}


# ---------------------------------------------------------------------------
# 3. Recently Viewed Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/recent",
    response_model=list[RecentlyViewedRead],
    summary="Get recently viewed items",
    description="Retrieve recently browsed workers and services.",
)
async def get_recently_viewed(
    current_user: ActiveUserDep,
    item_type: ItemType | None = Query(default=None, description="Filter by item type"),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[RecentlyViewedRead]:
    """Get recently viewed."""
    return await RecentlyViewedService.get_recently_viewed(
        user_id=str(current_user.id), item_type=item_type, limit=limit
    )


@router.post(
    "/recent",
    response_model=RecentlyViewedRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log recently viewed item",
    description="Record a recently viewed worker or service.",
)
async def log_recently_viewed(
    current_user: ActiveUserDep,
    req: RecentlyViewedCreate,
) -> RecentlyViewedRead:
    """Log recently viewed item."""
    return await RecentlyViewedService.log_view(user_id=str(current_user.id), req=req)


# ---------------------------------------------------------------------------
# 4. Saved Searches Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/saved-searches",
    response_model=list[SavedSearchRead],
    summary="List saved searches",
    description="Retrieve user's saved search criteria and filters.",
)
async def list_saved_searches(
    current_user: ActiveUserDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[SavedSearchRead]:
    """List saved searches."""
    return await SavedSearchesService.list_saved_searches(
        user_id=str(current_user.id), skip=skip, limit=limit
    )


@router.post(
    "/saved-searches",
    response_model=SavedSearchRead,
    status_code=status.HTTP_201_CREATED,
    summary="Save search preset",
    description="Save a search query and filter criteria.",
)
async def save_search(
    current_user: ActiveUserDep,
    req: SavedSearchCreate,
) -> SavedSearchRead:
    """Save search preset."""
    return await SavedSearchesService.save_search(user_id=str(current_user.id), req=req)


@router.delete(
    "/saved-searches/{search_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete saved search",
    description="Delete a saved search preset.",
)
async def delete_saved_search(
    current_user: ActiveUserDep,
    search_id: str,
) -> dict[str, str]:
    """Delete saved search."""
    await SavedSearchesService.delete_saved_search(search_id=search_id, user_id=str(current_user.id))
    return {"message": f"Saved search '{search_id}' deleted successfully."}


# ---------------------------------------------------------------------------
# 5. Recommendation Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/recommendations",
    response_model=list[RecommendationItem],
    summary="Get personalized recommendations",
    description="Retrieve personalized worker and service recommendations for current user.",
)
async def get_recommendations(current_user: ActiveUserDep) -> list[RecommendationItem]:
    """Get recommendations."""
    return await RecommendationService.generate_recommendations(str(current_user.id))
