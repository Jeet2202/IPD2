from fastapi import APIRouter, Depends, Query, BackgroundTasks
from typing import List, Optional
from app.schemas.search import SearchRequest, SearchResponse, SearchSuggestionModel, SearchHistoryModel
from app.services.hybrid_search_service import HybridSearchService
from app.services.search_analytics_service import SearchAnalyticsService
from app.repositories.search_repository import SearchRepository
from app.repositories.search_history_repository import SearchHistoryRepository
from app.core.dependencies import get_db

router = APIRouter(prefix="/search", tags=["Search"])

def get_hybrid_search_service(db=Depends(get_db)) -> HybridSearchService:
    repo = SearchRepository(db)
    return HybridSearchService(repo)

def get_analytics_service(db=Depends(get_db)) -> SearchAnalyticsService:
    repo = SearchHistoryRepository(db)
    return SearchAnalyticsService(repo)

@router.post("", response_model=SearchResponse)
async def perform_search(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = Query(None, description="Optional user ID for personalized history"),
    search_service: HybridSearchService = Depends(get_hybrid_search_service),
    analytics_service: SearchAnalyticsService = Depends(get_analytics_service)
):
    """
    Perform a hybrid intelligent search (Semantic + Keyword)
    """
    # Log search in background
    background_tasks.add_task(analytics_service.log_search, request.query, user_id)
    
    results, total = await search_service.search(request)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total=total,
        page=request.page,
        page_size=request.page_size
    )

@router.get("/suggestions", response_model=List[SearchSuggestionModel])
async def get_search_suggestions(
    q: Optional[str] = None,
    user_id: Optional[str] = None,
    analytics_service: SearchAnalyticsService = Depends(get_analytics_service)
):
    """Get auto-complete suggestions and recent searches"""
    return await analytics_service.get_suggestions(prefix=q, user_id=user_id)

@router.get("/trending", response_model=List[str])
async def get_trending_searches(
    analytics_service: SearchAnalyticsService = Depends(get_analytics_service)
):
    """Get popular/trending searches globally"""
    return await analytics_service.history_repo.get_trending_searches(limit=10)

@router.get("/history", response_model=List[SearchHistoryModel])
async def get_search_history(
    user_id: str,
    analytics_service: SearchAnalyticsService = Depends(get_analytics_service)
):
    """Retrieve search history for a user"""
    return await analytics_service.history_repo.get_recent_searches(limit=20, user_id=user_id)

@router.delete("/history")
async def clear_search_history(
    user_id: str,
    analytics_service: SearchAnalyticsService = Depends(get_analytics_service)
):
    """Clear search history for a user"""
    await analytics_service.history_repo.clear_history(user_id=user_id)
    return {"message": "Search history cleared"}
