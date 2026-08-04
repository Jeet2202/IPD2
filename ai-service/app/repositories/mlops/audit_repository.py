from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.mlops import AuditLogEntry

class AuditRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["mlops_audit_logs"]

    async def save_log(self, log_entry: AuditLogEntry) -> bool:
        doc = log_entry.model_dump(mode='json')
        doc.pop("id", None)
        result = await self.collection.insert_one(doc)
        return result.inserted_id is not None

    async def get_logs(self, limit: int = 100) -> List[AuditLogEntry]:
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        logs = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            logs.append(AuditLogEntry(**doc))
        return logs
