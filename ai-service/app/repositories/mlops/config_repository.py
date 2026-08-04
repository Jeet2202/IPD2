from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.mlops import SystemConfiguration

class ConfigRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["mlops_config"]

    async def get_configuration(self, config_id: str = "global") -> Optional[SystemConfiguration]:
        doc = await self.collection.find_one({"_id": config_id})
        if doc:
            doc["id"] = doc.pop("_id")
            return SystemConfiguration(**doc)
        return None

    async def update_configuration(self, config: SystemConfiguration) -> bool:
        doc = config.model_dump(mode='json')
        doc.pop("id", None)
        result = await self.collection.update_one(
            {"_id": config.id},
            {"$set": doc},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
