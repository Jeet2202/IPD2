from motor.motor_asyncio import AsyncIOMotorDatabase
import datetime
from typing import List, Dict
import logging
from app.core.config import settings
from app.schemas.search import SearchHistoryModel

logger = logging.getLogger(__name__)

class SearchHistoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[settings.SEARCH_HISTORY_COLLECTION]

    async def log_search(self, query: str, user_id: str = None):
        try:
            doc = {
                "query": query,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            await self.collection.insert_one(doc)
        except Exception as e:
            logger.error(f"Failed to log search history: {str(e)}")

    async def get_recent_searches(self, limit: int = 10, user_id: str = None) -> List[SearchHistoryModel]:
        try:
            query = {"user_id": user_id} if user_id else {}
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            results = []
            async for doc in cursor:
                results.append(SearchHistoryModel(
                    query=doc.get("query"),
                    timestamp=doc.get("timestamp"),
                    user_id=doc.get("user_id")
                ))
            return results
        except Exception as e:
            logger.error(f"Failed to get recent searches: {str(e)}")
            return []

    async def get_trending_searches(self, limit: int = 5) -> List[str]:
        try:
            # Group by query and count frequency
            pipeline = [
                {"$group": {"_id": "$query", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            cursor = self.collection.aggregate(pipeline)
            return [doc["_id"] async for doc in cursor if doc["_id"]]
        except Exception as e:
            logger.error(f"Failed to calculate trending searches: {str(e)}")
            return []

    async def clear_history(self, user_id: str = None):
        try:
            query = {"user_id": user_id} if user_id else {}
            await self.collection.delete_many(query)
        except Exception as e:
            logger.error(f"Failed to clear search history: {str(e)}")
