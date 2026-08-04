from app.schemas.mlops import SystemConfiguration
from app.repositories.mlops.config_repository import ConfigRepository
from app.services.mlops.audit_service import AuditService
from typing import Optional

class ConfigService:
    def __init__(self, repo: ConfigRepository, audit: AuditService):
        self.repo = repo
        self.audit = audit

    async def get_configuration(self) -> SystemConfiguration:
        config = await self.repo.get_configuration("global")
        if not config:
            config = SystemConfiguration(id="global")
            await self.repo.update_configuration(config)
        return config

    async def update_configuration(self, updates: SystemConfiguration) -> SystemConfiguration:
        updates.id = "global"
        success = await self.repo.update_configuration(updates)
        if success:
            await self.audit.log_event(
                event_type="CONFIG_CHANGED",
                entity_id="global",
                details={"updates": updates.model_dump()}
            )
        return updates
