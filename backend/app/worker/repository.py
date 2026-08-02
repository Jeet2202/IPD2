"""
Worker Repository — Database access operations for worker profiles.
"""

import logging

from beanie import PydanticObjectId

from app.worker.models import WorkerProfile

logger = logging.getLogger(__name__)


class WorkerRepository:
    """Encapsulates Beanie queries for WorkerProfile document collection."""

    @staticmethod
    async def get_by_user_id(user_id: str | PydanticObjectId) -> WorkerProfile | None:
        """Find worker profile document linked to user_id."""
        oid = PydanticObjectId(str(user_id)) if isinstance(user_id, str) else user_id
        return await WorkerProfile.find_one(WorkerProfile.user_id == oid)

    @staticmethod
    async def create_profile(user_id: str | PydanticObjectId) -> WorkerProfile:
        """Create and persist default WorkerProfile for user_id."""
        oid = PydanticObjectId(str(user_id)) if isinstance(user_id, str) else user_id
        profile = WorkerProfile(user_id=oid)
        await profile.insert()
        logger.info("Created new WorkerProfile for user_id=%s", oid)
        return profile

    @staticmethod
    async def save_profile(profile: WorkerProfile) -> WorkerProfile:
        """Persist updates to worker profile."""
        await profile.save()
        return profile
