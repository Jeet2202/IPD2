from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.schemas.admin_dashboard import WorkerIntelligence

class WorkerIntelligenceService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator):
        self.orchestrator = analytics_orchestrator

    async def get_worker_intelligence(self) -> WorkerIntelligence:
        worker_stats = await self.orchestrator.get_worker_analytics()
        
        return WorkerIntelligence(
            top_performing_workers=[{"id": "w1", "name": "Rajesh Kumar", "rating": 4.9, "jobs_completed": 120}],
            inactive_workers=[{"id": "w2", "name": "Amit Singh", "last_active": "2023-10-01"}],
            low_rated_workers=[{"id": "w3", "name": "Suresh P", "rating": 3.2}],
            high_rated_workers=[{"id": "w1", "name": "Rajesh Kumar", "rating": 4.9}],
            cancellation_leaders=[{"id": "w4", "name": "Vikram D", "cancellations": 15}],
            best_completion_rates=[{"id": "w1", "name": "Rajesh Kumar", "rate": 99.5}],
            fastest_responders=[{"id": "w5", "name": "Pooja M", "response_time_mins": 2.5}],
            slow_responders=[{"id": "w6", "name": "Rahul T", "response_time_mins": 45.0}],
            acceptance_leaders=[{"id": "w1", "name": "Rajesh Kumar", "rate": 98.0}],
            recommendations=["Consider offering incentives to Rajesh Kumar.", "Review Suresh P's recent jobs for quality issues."]
        )
