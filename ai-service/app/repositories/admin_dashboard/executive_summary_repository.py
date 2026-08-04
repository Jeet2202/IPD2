from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.schemas.admin_dashboard import ExecutiveSummary

class ExecutiveSummaryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["dashboard_executive_summaries"]
        
    async def save_summary(self, summary: ExecutiveSummary) -> str:
        summary_dict = summary.model_dump(exclude={"id"})
        summary_dict["generated_at"] = summary.generated_at or datetime.utcnow()
        result = await self.collection.insert_one(summary_dict)
        return str(result.inserted_id)
        
    async def get_latest_summary(self, summary_type: str) -> Optional[ExecutiveSummary]:
        doc = await self.collection.find_one(
            {"summary_type": summary_type},
            sort=[("generated_at", -1)]
        )
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return ExecutiveSummary(**doc)
        return None
