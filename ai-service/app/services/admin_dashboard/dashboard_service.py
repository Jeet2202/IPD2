from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import OverviewStats, SystemHealth
from app.schemas.analytics import DashboardStats

class DashboardService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_overview_stats(self) -> OverviewStats:
        # Fetch base dashboard stats
        base_stats: DashboardStats = await self.orchestrator.get_dashboard_stats()
        booking_stats = await self.orchestrator.get_booking_analytics()
        worker_stats = await self.orchestrator.get_worker_analytics()
        
        return OverviewStats(
            todays_bookings=booking_stats.total_bookings,
            todays_revenue=base_stats.today_revenue, 
            weekly_revenue=base_stats.today_revenue * 5, # Mock estimation
            monthly_revenue=base_stats.today_revenue * 20, # Mock estimation
            pending_bookings=base_stats.pending_jobs,
            completed_jobs=base_stats.completed_jobs,
            cancelled_jobs=booking_stats.cancelled_bookings,
            available_workers=worker_stats.available_workers,
            busy_workers=booking_stats.active_bookings,
            platform_health=95.5,
            average_rating=4.7,
            average_response_time=12.5 # mins
        )

    async def get_system_health(self) -> SystemHealth:
        return SystemHealth(
            status="Healthy",
            uptime="99.99%",
            active_services=6,
            error_rate=0.01,
            database_health="Connected"
        )
