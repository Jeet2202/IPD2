from typing import List, Dict, Any
from app.schemas.mlops import AuditLogEntry
from app.repositories.mlops.audit_repository import AuditRepository
from app.core.logging import logger

class AuditService:
    def __init__(self, repo: AuditRepository):
        self.repo = repo

    async def log_event(self, event_type: str, entity_id: str, details: Dict[str, Any], level: str = "INFO"):
        entry = AuditLogEntry(
            event_type=event_type,
            entity_id=entity_id,
            details=details,
            level=level
        )
        await self.repo.save_log(entry)
        
        log_msg = f"Audit: [{event_type}] for {entity_id} - {details}"
        if level == "ERROR":
            logger.error(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

    async def get_logs(self, limit: int = 100) -> List[AuditLogEntry]:
        return await self.repo.get_logs(limit)
