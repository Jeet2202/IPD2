from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.core.database import Database

from app.schemas.mlops import (
    ModelRegistrationRequest, ModelMetadata, DatasetRegistrationRequest,
    DatasetMetadata, ExperimentRequest, ExperimentMetadata, AIHealthStatus,
    ModelMetrics, AuditLogEntry, SystemConfiguration
)
from app.repositories.mlops.model_repository import ModelRepository
from app.repositories.mlops.dataset_repository import DatasetRepository
from app.repositories.mlops.experiment_repository import ExperimentRepository
from app.repositories.mlops.metrics_repository import MetricsRepository
from app.repositories.mlops.audit_repository import AuditRepository
from app.repositories.mlops.config_repository import ConfigRepository

from app.services.mlops.model_registry_service import ModelRegistryService
from app.services.mlops.dataset_registry_service import DatasetRegistryService
from app.services.mlops.experiment_service import ExperimentService
from app.services.mlops.monitoring_service import MonitoringService
from app.services.mlops.health_service import HealthService
from app.services.mlops.audit_service import AuditService
from app.services.mlops.config_service import ConfigService

router = APIRouter(prefix="/ml", tags=["MLOps"])

def get_db():
    return Database.get_db()

# Dependency factories
def get_model_service(db = Depends(get_db)):
    return ModelRegistryService(ModelRepository(db))

def get_dataset_service(db = Depends(get_db)):
    return DatasetRegistryService(DatasetRepository(db))

def get_experiment_service(db = Depends(get_db)):
    return ExperimentService(ExperimentRepository(db))

def get_monitoring_service(db = Depends(get_db)):
    return MonitoringService(MetricsRepository(db))

def get_health_service(db = Depends(get_db)):
    return HealthService(db)

def get_audit_service(db = Depends(get_db)):
    return AuditService(AuditRepository(db))

def get_config_service(db = Depends(get_db), audit_svc = Depends(get_audit_service)):
    return ConfigService(ConfigRepository(db), audit_svc)

# ================================
# Models
# ================================
@router.get("/models", response_model=List[ModelMetadata])
async def get_all_models(svc: ModelRegistryService = Depends(get_model_service)):
    return await svc.get_all_models()

@router.post("/models/register", response_model=ModelMetadata)
async def register_model(req: ModelRegistrationRequest, svc: ModelRegistryService = Depends(get_model_service)):
    try:
        return await svc.register_model(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/models/{id}/activate", response_model=dict)
async def activate_model(id: str, svc: ModelRegistryService = Depends(get_model_service)):
    try:
        await svc.activate_model(id)
        return {"status": "success", "message": f"Activated model {id}"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/models/history", response_model=List[ModelMetadata])
async def get_model_history(name: str, svc: ModelRegistryService = Depends(get_model_service)):
    return await svc.get_model_history(name)

# ================================
# Datasets
# ================================
@router.get("/datasets", response_model=List[DatasetMetadata])
async def get_all_datasets(svc: DatasetRegistryService = Depends(get_dataset_service)):
    return await svc.get_all_datasets()

@router.post("/datasets/register", response_model=DatasetMetadata)
async def register_dataset(req: DatasetRegistrationRequest, svc: DatasetRegistryService = Depends(get_dataset_service)):
    return await svc.register_dataset(req)

# ================================
# Experiments
# ================================
@router.get("/experiments", response_model=List[ExperimentMetadata])
async def get_all_experiments(svc: ExperimentService = Depends(get_experiment_service)):
    return await svc.get_all_experiments()

@router.post("/experiments", response_model=ExperimentMetadata)
async def log_experiment(req: ExperimentRequest, svc: ExperimentService = Depends(get_experiment_service)):
    return await svc.log_experiment(req)

# ================================
# Health & Monitoring
# ================================
@router.get("/health", response_model=AIHealthStatus)
async def get_health(svc: HealthService = Depends(get_health_service)):
    return await svc.get_health_status()

@router.get("/metrics", response_model=List[ModelMetrics])
async def get_metrics(model_id: str, limit: int = 100, svc: MonitoringService = Depends(get_monitoring_service)):
    return await svc.get_metrics(model_id, limit)

# ================================
# Configuration & Audit
# ================================
@router.get("/configuration", response_model=SystemConfiguration)
async def get_configuration(svc: ConfigService = Depends(get_config_service)):
    return await svc.get_configuration()

@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(limit: int = 100, svc: AuditService = Depends(get_audit_service)):
    return await svc.get_logs(limit)
