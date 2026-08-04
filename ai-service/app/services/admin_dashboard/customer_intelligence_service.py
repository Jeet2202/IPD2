from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import CustomerIntelligence

class CustomerIntelligenceService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_customer_intelligence(self) -> CustomerIntelligence:
        customer_stats = await self.orchestrator.get_customer_analytics()
        
        return CustomerIntelligence(
            active_customers=customer_stats.active_customers,
            repeat_customer_rate=customer_stats.repeat_customer_rate,
            average_spend=1250.50, # Example value
            favourite_services=[{"name": "AC Cleaning", "bookings": 350}],
            favourite_categories=[{"name": "Appliance Repair", "bookings": 800}],
            booking_frequency=1.5, # bookings per month
            customer_satisfaction_score=4.6,
            retention_statistics={"30_days": 85.0, "90_days": 65.0, "365_days": 40.0}
        )
