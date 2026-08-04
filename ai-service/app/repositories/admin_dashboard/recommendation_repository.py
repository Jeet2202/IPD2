from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.schemas.admin_dashboard import OperationalRecommendation

class RecommendationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["dashboard_recommendations"]
        
    async def save_recommendation(self, recommendation: OperationalRecommendation) -> str:
        rec_dict = recommendation.model_dump(exclude={"id"})
        rec_dict["generated_at"] = recommendation.generated_at or datetime.utcnow()
        result = await self.collection.insert_one(rec_dict)
        return str(result.inserted_id)
        
    async def get_recent_recommendations(self, limit: int = 50) -> List[OperationalRecommendation]:
        cursor = self.collection.find().sort("generated_at", -1).limit(limit)
        recommendations = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            recommendations.append(OperationalRecommendation(**doc))
        return recommendations
