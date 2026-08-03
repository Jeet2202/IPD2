from datetime import datetime, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class AnalyticsCustomerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = db["users"]
        self.bookings = db["bookings"]

    async def get_total_customers(self) -> int:
        return await self.users.count_documents({"role": "customer"})

    async def get_new_customers(self, days_back: int = 30) -> int:
        start_date = datetime.utcnow() - timedelta(days=days_back)
        return await self.users.count_documents({
            "role": "customer",
            "created_at": {"$gte": start_date.isoformat()}
        })

    async def get_repeat_customers(self) -> int:
        pipeline = [
            {"$group": {
                "_id": "$user_id",
                "booking_count": {"$sum": 1}
            }},
            {"$match": {"booking_count": {"$gt": 1}}},
            {"$count": "repeat_customers"}
        ]
        cursor = self.bookings.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0]["repeat_customers"] if result else 0
