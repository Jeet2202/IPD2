from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import psutil
import os
from typing import Dict, Any
from app.core.config import Settings, settings
from app.core.dependencies import get_settings, get_db
from app.utils.model_loader import ModelLoader

router = APIRouter(tags=["Infrastructure"])

@router.get("/")
async def root() -> Dict[str, str]:
    return {
        "service": "KaamSetu AI Service",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }

@router.get("/health")
async def health_check(db=Depends(get_db)) -> JSONResponse:
    """
    Returns 200 OK when all components are healthy, 503 when any component is degraded.
    """
    health_status: Dict[str, Any] = {
        "status": "ok",
        "components": {
            "database": "unknown",
            "filesystem": "ok"
        }
    }
    
    # Check Database
    try:
        await db.command("ping")
        health_status["components"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = f"error: {str(e)}"

    # Check Filesystem
    try:
        os.makedirs(settings.MODEL_DIRECTORY, exist_ok=True)
        os.makedirs(settings.DATASET_DIRECTORY, exist_ok=True)
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["filesystem"] = f"error: {str(e)}"

    # Return 503 if degraded so load balancers / k8s can detect unhealthy pods
    http_status = 200 if health_status["status"] == "ok" else 503
    return JSONResponse(status_code=http_status, content=health_status)

@router.get("/ready")
async def readiness_check() -> Dict[str, bool]:
    return {"ready": True}

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "memory_usage_mb": round(memory_info.rss / (1024 * 1024), 2),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "open_files": len(process.open_files())
    }

@router.get("/models")
async def get_loaded_models() -> Dict[str, list[str]]:
    return {
        "cached_models": ModelLoader.get_loaded_models()
    }

@router.get("/config")
async def get_safe_config(config: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """Return a safe overview of the configuration (masking secrets)"""
    safe_config = config.model_dump()
    
    # Mask secrets — always mask regardless of value to prevent accidental exposure
    safe_config["MONGO_URI"] = "***"
    safe_config["GROQ_API_KEY"] = "***"
        
    return safe_config
