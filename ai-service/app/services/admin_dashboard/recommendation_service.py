from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.repositories.admin_dashboard.recommendation_repository import RecommendationRepository
from app.schemas.admin_dashboard import OperationalRecommendation

class RecommendationService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator, recommendation_repo: RecommendationRepository):
        self.orchestrator = analytics_orchestrator
        self.recommendation_repo = recommendation_repo

    async def generate_recommendations(self) -> List[OperationalRecommendation]:
        # Fetch base data
        booking_stats = await self.orchestrator.get_booking_analytics()
        
        recommendations = []
        
        completion_rate = (booking_stats.completed_bookings / booking_stats.total_bookings * 100) if booking_stats.total_bookings > 0 else 0
        if completion_rate < 85:
            recommendations.append(OperationalRecommendation(
                recommendation_text="Investigate high booking cancellation/failure rate.",
                category="Operations",
                priority="HIGH",
                supporting_metrics={"completion_rate": completion_rate}
            ))
            
        # Add a default recommendation if none
        if not recommendations:
            recommendations.append(OperationalRecommendation(
                recommendation_text="Promote highly rated workers in top categories.",
                category="Growth",
                priority="MEDIUM",
                supporting_metrics={}
            ))
            
        for rec in recommendations:
            await self.recommendation_repo.save_recommendation(rec)
            
        return recommendations

    async def get_recent_recommendations(self, limit: int = 10) -> List[OperationalRecommendation]:
        recs = await self.recommendation_repo.get_recent_recommendations(limit)
        if not recs:
            recs = await self.generate_recommendations()
        return recs[:limit]
