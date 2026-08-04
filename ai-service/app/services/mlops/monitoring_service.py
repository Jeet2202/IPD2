from typing import List
from app.schemas.mlops import ModelMetrics
from app.repositories.mlops.metrics_repository import MetricsRepository
from app.core.logging import logger

class MonitoringService:
    def __init__(self, repo: MetricsRepository):
        self.repo = repo

    async def record_metrics(self, metrics: ModelMetrics) -> bool:
        success = await self.repo.save_metrics(metrics)
        if not success:
            logger.error(f"Failed to record metrics for model {metrics.model_id}")
        return success

    async def get_metrics(self, model_id: str, limit: int = 100) -> List[ModelMetrics]:
        return await self.repo.get_metrics_for_model(model_id, limit)
