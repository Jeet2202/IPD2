from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import BusinessIntelligence

class BusinessIntelligenceService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_business_intelligence(self) -> BusinessIntelligence:
        # Fetch base analytics
        booking_stats = await self.orchestrator.get_booking_analytics()
        service_stats = await self.orchestrator.get_service_analytics()
        
        # In a real scenario, we would calculate MoM/YoY growth from historical data.
        # Since Phase 5.6 Analytics Platform provides some of this, we'll synthesize it.
        revenue_growth = 12.5 # Mocked for now, normally computed from historical booking data
        booking_growth = 8.2
        customer_growth = 5.1
        worker_growth = 3.4
        
        top_categories = []
        for cat in service_stats.most_popular_categories[:5]:
            top_categories.append(cat)
            
        top_services = []
        for srv in service_stats.most_requested_services[:5]:
            top_services.append(srv)
            
        return BusinessIntelligence(
            business_growth_summary="Steady growth across most categories, with a 12.5% increase in revenue compared to last month.",
            revenue_growth=revenue_growth,
            booking_growth=booking_growth,
            customer_growth=customer_growth,
            worker_growth=worker_growth,
            top_categories=top_categories,
            top_services=top_services,
            top_cities=["Mumbai", "Delhi", "Bangalore"], # Mocked
            fastest_growing_areas=["Andheri East", "Bandra West", "Powai"] # Mocked
        )
