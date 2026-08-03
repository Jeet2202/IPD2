from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class AnalyticsWorkerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.workers = db["workers"]
        self.quotations = db["quotations"]

    async def get_worker_status_counts(self) -> Dict[str, int]:
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        cursor = self.workers.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return {item["_id"]: item["count"] for item in results}
        
    async def get_worker_verification_counts(self) -> Dict[bool, int]:
        pipeline = [
            {"$group": {
                "_id": "$verified",
                "count": {"$sum": 1}
            }}
        ]
        cursor = self.workers.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return {item["_id"]: item["count"] for item in results}

    async def get_average_rating(self) -> float:
        pipeline = [
            {"$match": {"rating": {"$gt": 0}}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"}
            }}
        ]
        cursor = self.workers.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0]["avg_rating"] if result and result[0]["avg_rating"] else 0.0

    async def get_average_quote_amount(self) -> float:
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_amount": {"$avg": "$amount"}
            }}
        ]
        cursor = self.quotations.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0]["avg_amount"] if result and result[0]["avg_amount"] else 0.0
