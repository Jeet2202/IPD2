"""
Worker profile Beanie document model.
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field

from app.utils.enums import WorkerAvailability


class WorkerProfile(Document):
    """
    Worker profile document linked 1:1 with User.

    Collection: worker_profiles
    """

    user_id: Annotated[PydanticObjectId, Indexed(unique=True)]
    skills: list[str] = Field(default_factory=list)
    availability: WorkerAvailability = WorkerAvailability.AVAILABLE
    rating: float = 0.0
    review_count: int = 0
    bio: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "worker_profiles"
        use_state_management = True
