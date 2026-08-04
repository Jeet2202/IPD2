from app.schemas.mlops import AIHealthStatus
from app.core.database import Database
from app.utils.backend_client import BackendClient
import os
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase

class HealthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_health_status(self) -> AIHealthStatus:
        status = AIHealthStatus()
        
        # Check DB
        try:
            await self.db.command("ping")
            status.database_status = "ONLINE"
        except Exception:
            status.database_status = "OFFLINE"
            status.overall_score -= 20
            
        # Check Groq Connectivity (Phase 5.5)
        try:
            if settings.GROQ_API_KEY:
                status.groq_connectivity = "ONLINE"
            else:
                status.groq_connectivity = "OFFLINE"
                status.overall_score -= 10
        except Exception:
            status.groq_connectivity = "OFFLINE"
            
        # Check File System
        if os.path.exists(settings.MODEL_DIRECTORY):
            status.filesystem_status = "ONLINE"
        else:
            status.filesystem_status = "OFFLINE"
            status.overall_score -= 10
            
        # Check Core APIs
        if BackendClient._client:
            status.api_status = "ONLINE"
        else:
            status.api_status = "OFFLINE"
            status.overall_score -= 10
            
        # Determine overall
        if status.overall_score < 70:
            status.status = "UNHEALTHY"
        elif status.overall_score < 90:
            status.status = "DEGRADED"
        else:
            status.status = "HEALTHY"
            
        return status
