from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PricingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.services_collection = db["services"]

    async def get_service_base_price(self, service_id: str) -> float:
        """
        Fetches the base price for a service from the services collection.
        """
        try:
            from bson import ObjectId
            query_id = ObjectId(service_id) if ObjectId.is_valid(service_id) else service_id
            
            service = await self.services_collection.find_one({"_id": query_id})
            if service and "base_price" in service:
                return float(service["base_price"])
            
            logger.warning(f"No base price found for service {service_id}, returning 500.0 as default")
            return 500.0 # Fallback default
        except Exception as e:
            logger.error(f"Error fetching base price for service {service_id}: {str(e)}")
            return 500.0
