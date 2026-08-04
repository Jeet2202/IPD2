from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.mlops import ModelMetrics

class MetricsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["mlops_metrics"]

    async def save_metrics(self, metrics: ModelMetrics) -> bool:
        doc = metrics.model_dump(mode='json')
        result = await self.collection.insert_one(doc)
        return result.inserted_id is not None

    async def get_metrics_for_model(self, model_id: str, limit: int = 100) -> List[ModelMetrics]:
        cursor = self.collection.find({"model_id": model_id}).sort("timestamp", -1).limit(limit)
        metrics_list = []
        async for doc in cursor:
            doc.pop("_id", None)
            metrics_list.append(ModelMetrics(**doc))
        return metrics_list
