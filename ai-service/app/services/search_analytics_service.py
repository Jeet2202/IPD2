from typing import List
from app.repositories.search_history_repository import SearchHistoryRepository
from app.schemas.search import SearchSuggestionModel

class SearchAnalyticsService:
    def __init__(self, history_repo: SearchHistoryRepository):
        self.history_repo = history_repo

    async def log_search(self, query: str, user_id: str = None):
        """Logs a search query asynchronously"""
        if query and len(query.strip()) > 2:
            await self.history_repo.log_search(query.strip(), user_id)

    async def get_suggestions(self, prefix: str = "", user_id: str = None) -> List[SearchSuggestionModel]:
        """Returns auto-suggestions combining recent, trending, and basic autocomplete"""
        suggestions = []
        
        # In a full system, you would query an autocomplete index for the prefix.
        # For now, we will fetch recent and trending, and filter by prefix if provided.
        
        recent = await self.history_repo.get_recent_searches(limit=5, user_id=user_id)
        trending = await self.history_repo.get_trending_searches(limit=5)
        
        seen = set()
        
        # Add Recent
        for r in recent:
            if not prefix or r.query.lower().startswith(prefix.lower()):
                if r.query not in seen:
                    suggestions.append(SearchSuggestionModel(suggestion=r.query, type="recent"))
                    seen.add(r.query)
                    
        # Add Trending
        for t in trending:
            if not prefix or t.lower().startswith(prefix.lower()):
                if t not in seen:
                    suggestions.append(SearchSuggestionModel(suggestion=t, type="trending"))
                    seen.add(t)
                    
        # Simple autocomplete fallback (mocked)
        if prefix and len(suggestions) < 3:
            suggestions.append(SearchSuggestionModel(suggestion=f"{prefix} near me", type="autocomplete"))
            
        return suggestions
