from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.schemas.admin_dashboard import Anomaly

class AnomalyRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["dashboard_anomalies"]
        
    async def save_anomaly(self, anomaly: Anomaly) -> str:
        anomaly_dict = anomaly.model_dump(exclude={"id"})
        anomaly_dict["detected_at"] = anomaly.detected_at or datetime.utcnow()
        result = await self.collection.insert_one(anomaly_dict)
        return str(result.inserted_id)
        
    async def get_recent_anomalies(self, limit: int = 50) -> List[Anomaly]:
        cursor = self.collection.find().sort("detected_at", -1).limit(limit)
        anomalies = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            anomalies.append(Anomaly(**doc))
        return anomalies
