from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import RevenueIntelligence

class RevenueIntelligenceService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_revenue_intelligence(self) -> RevenueIntelligence:
        # Mocked data since AnalyticsPlatform might not have full historical revenue
        return RevenueIntelligence(
            revenue_by_day={"2023-10-01": 15000.0, "2023-10-02": 16500.0},
            revenue_by_month={"2023-09": 450000.0, "2023-10": 480000.0},
            revenue_by_category={"Appliance Repair": 150000.0, "Cleaning": 120000.0},
            revenue_by_service={"AC Repair": 85000.0, "Deep Cleaning": 70000.0},
            revenue_by_city={"Mumbai": 250000.0, "Delhi": 150000.0, "Bangalore": 80000.0},
            average_order_value=850.50,
            average_quotation=920.00,
            revenue_distribution={"B2C": 75.0, "B2B": 25.0}
        )
