from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.schemas.admin_dashboard import ExportResponse

class ReportRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["dashboard_reports"]
        
    async def save_report(self, report: ExportResponse) -> str:
        report_dict = report.model_dump()
        report_dict["generated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(report_dict)
        return str(result.inserted_id)
        
    async def get_recent_reports(self, limit: int = 50) -> List[ExportResponse]:
        cursor = self.collection.find().sort("generated_at", -1).limit(limit)
        reports = []
        async for doc in cursor:
            # Not returning ID for ExportResponse as per schema, just the data
            reports.append(ExportResponse(**doc))
        return reports
