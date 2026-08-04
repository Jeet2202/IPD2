from typing import List, Optional
import uuid
from app.schemas.mlops import DatasetMetadata, DatasetRegistrationRequest
from app.repositories.mlops.dataset_repository import DatasetRepository
from app.core.logging import logger

class DatasetRegistryService:
    def __init__(self, repo: DatasetRepository):
        self.repo = repo

    async def register_dataset(self, req: DatasetRegistrationRequest) -> DatasetMetadata:
        ds_id = f"ds-{uuid.uuid4().hex[:8]}"
        
        dataset = DatasetMetadata(
            id=ds_id,
            name=req.name,
            version=req.version,
            description=req.description,
            source=req.source,
            schema_definition=req.schema_definition,
            statistics=req.statistics,
            feature_list=req.feature_list,
            supported_models=req.supported_models
        )
        
        await self.repo.create_dataset(dataset)
        logger.info(f"Registered new dataset: {ds_id}")
        return dataset

    async def get_all_datasets(self) -> List[DatasetMetadata]:
        return await self.repo.get_all_datasets()
