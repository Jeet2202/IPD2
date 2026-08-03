from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class AnalyticsBookingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.bookings = db["bookings"]

    async def get_status_counts(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, int]:
        match_stage = {}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date: match_stage["created_at"]["$gte"] = start_date.isoformat()
            if end_date: match_stage["created_at"]["$lte"] = end_date.isoformat()
            
        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})
            
        pipeline.append({
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        })
        
        cursor = self.bookings.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        return {item["_id"]: item["count"] for item in results}

    async def get_total_revenue(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        match_stage = {"status": "completed"}
        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date: match_stage["created_at"]["$gte"] = start_date.isoformat()
            if end_date: match_stage["created_at"]["$lte"] = end_date.isoformat()
            
        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$final_price"}
            }}
        ]
        
        cursor = self.bookings.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        return result[0]["total_revenue"] if result else 0.0

    async def get_bookings_over_time(self, group_by: str = "day", days_back: int = 30) -> List[Dict[str, Any]]:
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        # group_by could be mapped to mongo date parts, for simplicity string matching
        date_format = "%Y-%m-%d"
        if group_by == "month":
            date_format = "%Y-%m"
            
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date.isoformat()}}},
            {"$addFields": {
                "date_parsed": {"$dateFromString": {"dateString": "$created_at"}}
            }},
            {"$group": {
                "_id": {"$dateToString": {"format": date_format, "date": "$date_parsed"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        cursor = self.bookings.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_average_completion_time(self) -> float:
        pipeline = [
            {"$match": {"status": "completed", "completed_at": {"$exists": True}, "created_at": {"$exists": True}}},
            {"$addFields": {
                "created_date": {"$dateFromString": {"dateString": "$created_at"}},
                "completed_date": {"$dateFromString": {"dateString": "$completed_at"}}
            }},
            {"$project": {
                "duration_ms": {"$subtract": ["$completed_date", "$created_date"]}
            }},
            {"$group": {
                "_id": None,
                "avg_duration": {"$avg": "$duration_ms"}
            }}
        ]
        cursor = self.bookings.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        # return in hours
        return (result[0]["avg_duration"] / (1000 * 60 * 60)) if result and result[0]["avg_duration"] else 0.0
