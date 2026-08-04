from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import MarketplaceIntelligence

class MarketplaceIntelligenceService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_marketplace_intelligence(self) -> MarketplaceIntelligence:
        worker_stats = await self.orchestrator.get_worker_analytics()
        booking_stats = await self.orchestrator.get_booking_analytics()
        
        active_workers = worker_stats.active_workers
        todays_bookings = booking_stats.total_bookings # Using total for simplicity
        
        demand_vs_supply = todays_bookings / (active_workers or 1)
        
        # Determine market balance
        if demand_vs_supply > 5:
            market_balance = "High Demand / Low Supply"
        elif demand_vs_supply < 0.5:
            market_balance = "Low Demand / High Supply"
        else:
            market_balance = "Balanced"
            
        worker_distribution = {"Mumbai": 450, "Delhi": 320, "Bangalore": 280}
        booking_distribution = {"Mumbai": 1200, "Delhi": 850, "Bangalore": 900}
        
        return MarketplaceIntelligence(
            demand_vs_supply_ratio=round(demand_vs_supply, 2),
            worker_shortages=[{"area": "Powai", "category": "Electrician", "shortage": 15}],
            worker_distribution=worker_distribution,
            booking_distribution=booking_distribution,
            area_coverage=85.5,
            service_availability={"AC Repair": 92.0, "Plumbing": 88.5, "Cleaning": 95.0},
            low_supply_areas=["Navi Mumbai", "Thane"],
            high_demand_areas=["Andheri West", "Bandra"],
            market_balance=market_balance
        )
