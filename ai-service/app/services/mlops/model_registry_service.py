from typing import List, Optional
from datetime import datetime
import uuid

from app.schemas.mlops import ModelMetadata, ModelRegistrationRequest, MODEL_STATUS_ACTIVE, MODEL_STATUS_INACTIVE
from app.repositories.mlops.model_repository import ModelRepository
from app.core.logging import logger

class ModelRegistryService:
    def __init__(self, repo: ModelRepository):
        self.repo = repo

    async def register_model(self, req: ModelRegistrationRequest) -> ModelMetadata:
        model_id = f"{req.name.replace(' ', '-').lower()}-v{req.version.replace('.', '-')}"
        
        existing = await self.repo.get_model(model_id)
        if existing:
            raise ValueError(f"Model version {req.version} already exists for {req.name}")
            
        model = ModelMetadata(
            id=model_id,
            name=req.name,
            description=req.description,
            version=req.version,
            supported_tasks=req.supported_tasks,
            tags=req.tags,
            owner=req.owner,
            notes=req.notes,
            status=MODEL_STATUS_INACTIVE
        )
        
        await self.repo.create_model(model)
        logger.info(f"Registered new model: {model_id}")
        return model

    async def activate_model(self, model_id: str) -> bool:
        model = await self.repo.get_model(model_id)
        if not model:
            raise FileNotFoundError(f"Model not found: {model_id}")
            
        # Deprecate old active models of the same name
        history = await self.repo.get_model_history(model.name)
        for old_model in history:
            if old_model.status == MODEL_STATUS_ACTIVE:
                old_model.status = MODEL_STATUS_INACTIVE
                await self.repo.update_model(old_model)
                
        model.status = MODEL_STATUS_ACTIVE
        model.deployed_at = datetime.utcnow()
        await self.repo.update_model(model)
        logger.info(f"Activated model: {model_id}")
        return True

    async def get_all_models(self) -> List[ModelMetadata]:
        return await self.repo.get_all_models()

    async def get_model_history(self, name: str) -> List[ModelMetadata]:
        return await self.repo.get_model_history(name)
