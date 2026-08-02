"""
Customer profile Beanie document model.
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field


class CustomerProfile(Document):
    """
    Customer profile document linked 1:1 with User.

    Collection: customer_profiles
    """

    user_id: Annotated[PydanticObjectId, Indexed(unique=True)]
    addresses: list[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "customer_profiles"
        use_state_management = True
