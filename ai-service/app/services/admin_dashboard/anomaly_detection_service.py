from typing import List, Dict, Any
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.repositories.admin_dashboard.anomaly_repository import AnomalyRepository
from app.schemas.admin_dashboard import Anomaly

class AnomalyDetectionService:
    def __init__(self, analytics_orchestrator: AnalyticsOrchestrator, anomaly_repo: AnomalyRepository):
        self.orchestrator = analytics_orchestrator
        self.anomaly_repo = anomaly_repo

    async def detect_anomalies(self) -> List[Anomaly]:
        # Fetch data
        worker_stats = await self.orchestrator.get_worker_analytics()
        booking_stats = await self.orchestrator.get_booking_analytics()
        
        anomalies = []
        
        # Worker supply anomaly
        total_active_workers = worker_stats.available_workers + worker_stats.busy_workers
        if total_active_workers < 20 and booking_stats.total_bookings > 50:
            anomalies.append(Anomaly(
                anomaly_type="Worker Shortage",
                severity="HIGH",
                description="Active worker count is unusually low.",
                impact="May lead to unfulfilled bookings and customer churn.",
                suggested_action="Incentivize workers to come online."
            ))
            
        for anomaly in anomalies:
            await self.anomaly_repo.save_anomaly(anomaly)
            
        return anomalies

    async def get_recent_anomalies(self, limit: int = 10) -> List[Anomaly]:
        anomalies = await self.anomaly_repo.get_recent_anomalies(limit)
        if not anomalies:
            anomalies = await self.detect_anomalies()
        return anomalies[:limit]
