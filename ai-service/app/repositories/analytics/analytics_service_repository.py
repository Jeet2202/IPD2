from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class AnalyticsServiceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.bookings = db["bookings"]

    async def get_service_popularity(self, limit: int = 5, ascending: bool = False) -> List[Dict[str, Any]]:
        sort_order = 1 if ascending else -1
        pipeline = [
            {"$group": {
                "_id": {"service_id": "$service_id", "service_name": "$service_name"},
                "request_count": {"$sum": 1}
            }},
            {"$sort": {"request_count": sort_order}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "service_id": "$_id.service_id",
                "service_name": "$_id.service_name",
                "request_count": 1
            }}
        ]
        cursor = self.bookings.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_category_distribution(self) -> List[Dict[str, Any]]:
        pipeline = [
            {"$group": {
                "_id": {"category_id": "$category_id", "category_name": "$category_name"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$project": {
                "_id": 0,
                "category_id": "$_id.category_id",
                "category_name": "$_id.category_name",
                "count": 1
            }}
        ]
        cursor = self.bookings.aggregate(pipeline)
        return await cursor.to_list(length=None)
