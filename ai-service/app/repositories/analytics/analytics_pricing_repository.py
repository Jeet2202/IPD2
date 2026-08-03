from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class AnalyticsPricingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.quotations = db["quotations"]

    async def get_price_metrics(self) -> Dict[str, float]:
        pipeline = [
            {"$group": {
                "_id": None,
                "avg_quote": {"$avg": "$amount"},
                "min_quote": {"$min": "$amount"},
                "max_quote": {"$max": "$amount"},
                "std_dev": {"$stdDevPop": "$amount"}
            }}
        ]
        cursor = self.quotations.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        if not result:
            return {"avg_quote": 0.0, "min_quote": 0.0, "max_quote": 0.0, "std_dev": 0.0}
            
        r = result[0]
        return {
            "avg_quote": r.get("avg_quote", 0.0) or 0.0,
            "min_quote": r.get("min_quote", 0.0) or 0.0,
            "max_quote": r.get("max_quote", 0.0) or 0.0,
            "std_dev": r.get("std_dev", 0.0) or 0.0,
        }

    async def get_price_distribution(self, bucket_size: int = 500) -> List[Dict[str, Any]]:
        pipeline = [
            {"$bucketAuto": {
                "groupBy": "$amount",
                "buckets": 10,
                "output": {
                    "count": {"$sum": 1}
                }
            }}
        ]
        cursor = self.quotations.aggregate(pipeline)
        return await cursor.to_list(length=None)
