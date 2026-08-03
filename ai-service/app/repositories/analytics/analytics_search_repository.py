from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class AnalyticsSearchRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.search_history = db["search_history"]

    async def get_total_searches(self) -> int:
        return await self.search_history.count_documents({})

    async def get_trending_searches(self, limit: int = 10) -> List[str]:
        pipeline = [
            {"$group": {
                "_id": "$query",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        cursor = self.search_history.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return [item["_id"] for item in results if item["_id"]]

    async def get_search_success_rate(self) -> float:
        pipeline = [
            {"$group": {
                "_id": "$has_results",
                "count": {"$sum": 1}
            }}
        ]
        cursor = self.search_history.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        total = 0
        success = 0
        for item in results:
            total += item["count"]
            if item["_id"] is True:
                success += item["count"]
                
        return (success / total * 100) if total > 0 else 0.0
