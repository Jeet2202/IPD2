from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.mlops import ModelMetadata

class ModelRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["mlops_models"]

    async def create_model(self, model: ModelMetadata) -> str:
        model_dict = model.model_dump(mode='json')
        model_dict["_id"] = model_dict.pop("id")
        await self.collection.insert_one(model_dict)
        return model.id

    async def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        doc = await self.collection.find_one({"_id": model_id})
        if doc:
            doc["id"] = doc.pop("_id")
            return ModelMetadata(**doc)
        return None

    async def update_model(self, model: ModelMetadata) -> bool:
        model_dict = model.model_dump(mode='json')
        model_dict.pop("id")
        result = await self.collection.update_one({"_id": model.id}, {"$set": model_dict})
        return result.modified_count > 0

    async def get_all_models(self) -> List[ModelMetadata]:
        cursor = self.collection.find()
        models = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            models.append(ModelMetadata(**doc))
        return models

    async def get_model_history(self, name: str) -> List[ModelMetadata]:
        cursor = self.collection.find({"name": name}).sort("version", -1)
        models = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            models.append(ModelMetadata(**doc))
        return models
