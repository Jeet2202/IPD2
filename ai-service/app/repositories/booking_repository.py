from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
import logging
from app.models.domain_models import BookingModel, Location

logger = logging.getLogger(__name__)

class BookingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["bookings"]

    async def get_booking_by_id(self, booking_id: str) -> Optional[BookingModel]:
        try:
            # Ally might be using ObjectIds for bookings
            query_id = ObjectId(booking_id) if ObjectId.is_valid(booking_id) else booking_id
            doc = await self.collection.find_one({"_id": query_id})
            
            if not doc:
                return None
                
            # Map MongoDB document to Domain Model
            return BookingModel(
                id=str(doc.get("_id")),
                service_id=str(doc.get("service_id", "")),
                category_id=str(doc.get("category_id", "")),
                location=Location(
                    coordinates=doc.get("location", {}).get("coordinates", [0.0, 0.0])
                ),
                status=doc.get("status", "pending")
            )
        except Exception as e:
            logger.error(f"Error fetching booking {booking_id}: {str(e)}")
            raise
