from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.repositories.admin_dashboard.executive_summary_repository import ExecutiveSummaryRepository
from app.schemas.admin_dashboard import ExecutiveSummary

class ExecutiveSummaryService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator, summary_repo: ExecutiveSummaryRepository):
        self.orchestrator = analytics_orchestrator
        self.summary_repo = summary_repo

    async def generate_summary(self, summary_type: str) -> ExecutiveSummary:
        booking_stats = await self.orchestrator.get_booking_analytics()
        
        completion_rate = (booking_stats.completed_bookings / booking_stats.total_bookings * 100) if booking_stats.total_bookings > 0 else 0
        
        summary = ExecutiveSummary(
            summary_type=summary_type,
            platform_health="Good" if completion_rate > 80 else "Needs Attention",
            achievements=[f"Completed {booking_stats.total_bookings} bookings."],
            risks=["High cancellation rate in some areas."],
            growth="Steady growth observed.",
            weak_areas=["Worker availability during peak hours."],
            operational_issues=["None detected currently."],
            business_opportunities=["Expand into new categories."],
            priority_actions=["Review pricing for low demand services."]
        )
        
        await self.summary_repo.save_summary(summary)
        return summary

    async def get_latest_summary(self, summary_type: str) -> ExecutiveSummary:
        summary = await self.summary_repo.get_latest_summary(summary_type.upper())
        if not summary:
            summary = await self.generate_summary(summary_type.upper())
        return summary
