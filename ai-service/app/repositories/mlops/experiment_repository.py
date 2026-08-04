from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.mlops import ExperimentMetadata

class ExperimentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["mlops_experiments"]

    async def create_experiment(self, experiment: ExperimentMetadata) -> str:
        exp_dict = experiment.model_dump(mode='json')
        exp_dict["_id"] = exp_dict.pop("id")
        await self.collection.insert_one(exp_dict)
        return experiment.id

    async def get_experiment(self, experiment_id: str) -> Optional[ExperimentMetadata]:
        doc = await self.collection.find_one({"_id": experiment_id})
        if doc:
            doc["id"] = doc.pop("_id")
            return ExperimentMetadata(**doc)
        return None

    async def get_all_experiments(self) -> List[ExperimentMetadata]:
        cursor = self.collection.find().sort("created_at", -1)
        experiments = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            experiments.append(ExperimentMetadata(**doc))
        return experiments
