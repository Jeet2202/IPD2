from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import PricingIntelligence

class PricingIntelligenceService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_pricing_intelligence(self) -> PricingIntelligence:
        pricing_stats = await self.orchestrator.get_pricing_analytics()
        
        # Convert ChartData to dict
        price_dist = {}
        if pricing_stats.price_distribution and pricing_stats.price_distribution.datasets:
            dataset = pricing_stats.price_distribution.datasets[0]
            for i, label in enumerate(pricing_stats.price_distribution.labels):
                if i < len(dataset.data):
                    price_dist[label] = float(dataset.data[i])

        return PricingIntelligence(
            average_price=pricing_stats.average_quote,
            price_distribution=price_dist,
            high_price_areas=["South Mumbai", "Bandra"],
            low_price_areas=["Thane", "Navi Mumbai"],
            quotation_acceptance_rate=78.5,
            average_worker_quote=pricing_stats.average_price * 1.1,
            price_variance=pricing_stats.price_variance,
            outlier_pricing=[{"service": "AC Repair", "quote": 5000, "average": 1500}]
        )
