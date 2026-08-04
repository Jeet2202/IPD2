from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.repositories.admin_dashboard.insight_repository import InsightRepository
from app.schemas.admin_dashboard import AIInsight
import datetime

class InsightService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator, insight_repo: InsightRepository):
        self.orchestrator = analytics_orchestrator
        self.insight_repo = insight_repo

    async def generate_insights(self) -> List[AIInsight]:
        # Fetch base analytics
        booking_stats = await self.orchestrator.get_booking_analytics()
        search_stats = await self.orchestrator.get_search_analytics()
        
        new_insights = []
        
        # Rule 1: High search volume for a category
        for query in search_stats.trending_searches[:2]:
            new_insights.append(AIInsight(
                insight_text=f"Searches for '{query}' have increased significantly.",
                category="Marketplace",
                reference_data={"query": query, "volume": 150} # Mock volume
            ))
            
        # Rule 2: Booking trends
        if booking_stats.total_bookings > 100:
            new_insights.append(AIInsight(
                insight_text="Booking volume is higher than average this week.",
                category="Business",
                reference_data={"total_bookings": booking_stats.total_bookings}
            ))
            
        # Save generated insights
        for insight in new_insights:
            await self.insight_repo.save_insight(insight)
            
        return new_insights

    async def get_recent_insights(self, limit: int = 10) -> List[AIInsight]:
        # First check DB
        insights = await self.insight_repo.get_recent_insights(limit)
        
        if not insights:
            # Generate if none exist
            insights = await self.generate_insights()
            
        return insights[:limit]
