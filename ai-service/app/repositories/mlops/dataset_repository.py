from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.mlops import DatasetMetadata

class DatasetRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["mlops_datasets"]

    async def create_dataset(self, dataset: DatasetMetadata) -> str:
        ds_dict = dataset.model_dump(mode='json')
        ds_dict["_id"] = ds_dict.pop("id")
        await self.collection.insert_one(ds_dict)
        return dataset.id

    async def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        doc = await self.collection.find_one({"_id": dataset_id})
        if doc:
            doc["id"] = doc.pop("_id")
            return DatasetMetadata(**doc)
        return None

    async def get_all_datasets(self) -> List[DatasetMetadata]:
        cursor = self.collection.find()
        datasets = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            datasets.append(DatasetMetadata(**doc))
        return datasets
