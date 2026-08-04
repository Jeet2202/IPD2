from typing import List
import uuid
from app.schemas.mlops import ExperimentMetadata, ExperimentRequest
from app.repositories.mlops.experiment_repository import ExperimentRepository
from app.core.logging import logger

class ExperimentService:
    def __init__(self, repo: ExperimentRepository):
        self.repo = repo

    async def log_experiment(self, req: ExperimentRequest) -> ExperimentMetadata:
        exp_id = f"exp-{uuid.uuid4().hex[:8]}"
        
        experiment = ExperimentMetadata(
            id=exp_id,
            name=req.name,
            model_id=req.model_id,
            dataset_id=req.dataset_id,
            parameters=req.parameters,
            metrics=req.metrics,
            results=req.results,
            status=req.status,
            execution_time_seconds=req.execution_time_seconds,
            owner=req.owner,
            notes=req.notes
        )
        
        await self.repo.create_experiment(experiment)
        logger.info(f"Logged new experiment: {exp_id}")
        return experiment

    async def get_all_experiments(self) -> List[ExperimentMetadata]:
        return await self.repo.get_all_experiments()
