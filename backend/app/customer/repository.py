"""
Customer Repository — Database access operations for customer profiles.
"""

import logging

from beanie import PydanticObjectId

from app.customer.models import CustomerProfile

logger = logging.getLogger(__name__)


class CustomerRepository:
    """Encapsulates Beanie queries for CustomerProfile document collection."""

    @staticmethod
    async def get_by_user_id(user_id: str | PydanticObjectId) -> CustomerProfile | None:
        """Find customer profile document linked to user_id."""
        oid = PydanticObjectId(str(user_id)) if isinstance(user_id, str) else user_id
        return await CustomerProfile.find_one(CustomerProfile.user_id == oid)

    @staticmethod
    async def create_profile(user_id: str | PydanticObjectId) -> CustomerProfile:
        """Create and persist default CustomerProfile for user_id."""
        oid = PydanticObjectId(str(user_id)) if isinstance(user_id, str) else user_id
        profile = CustomerProfile(user_id=oid)
        await profile.insert()
        logger.info("Created new CustomerProfile for user_id=%s", oid)
        return profile

    @staticmethod
    async def save_profile(profile: CustomerProfile) -> CustomerProfile:
        """Persist updates to customer profile."""
        await profile.save()
        return profile
