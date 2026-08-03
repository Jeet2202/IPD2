from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MarketplaceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.workers_collection = db["workers"]
        self.bookings_collection = db["bookings"]

    async def get_worker_stats(self, service_id: str, city: str) -> Dict[str, int]:
        """
        Gets counts of available vs busy workers for a specific service in a city.
        """
        try:
            # Note: city field in nested location might need proper query depending on schema
            # Using simple query for now.
            base_query = {
                "services": service_id,
                "address.city": city, # Assuming address is stored like this or we approximate
                "is_active": True,
                "is_verified": True,
                "is_suspended": {"$ne": True}
            }
            
            total_workers = await self.workers_collection.count_documents(base_query)
            
            available_query = {**base_query, "is_available": True}
            available_workers = await self.workers_collection.count_documents(available_query)
            
            return {
                "total": total_workers,
                "available": available_workers,
                "busy": total_workers - available_workers
            }
        except Exception as e:
            logger.error(f"Error fetching worker stats: {str(e)}")
            return {"total": 0, "available": 0, "busy": 0}

    async def get_recent_booking_volume(self, service_id: str, city: str, days: int = 7) -> int:
        """
        Gets the volume of recent bookings for this service to gauge demand.
        """
        try:
            # Here we just mock the query by counting all bookings for the service.
            # In a real scenario, we'd filter by `created_at` within `days`.
            count = await self.bookings_collection.count_documents({
                "service_id": service_id,
                # "location.city": city # If applicable
            })
            return count
        except Exception as e:
            logger.error(f"Error fetching booking volume: {str(e)}")
            return 0
