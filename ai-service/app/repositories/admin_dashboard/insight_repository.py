from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.schemas.admin_dashboard import AIInsight

class InsightRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["dashboard_insights"]
        
    async def save_insight(self, insight: AIInsight) -> str:
        insight_dict = insight.model_dump(exclude={"id"})
        insight_dict["generated_at"] = insight.generated_at or datetime.utcnow()
        result = await self.collection.insert_one(insight_dict)
        return str(result.inserted_id)
        
    async def get_recent_insights(self, limit: int = 50) -> List[AIInsight]:
        cursor = self.collection.find().sort("generated_at", -1).limit(limit)
        insights = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            insights.append(AIInsight(**doc))
        return insights
