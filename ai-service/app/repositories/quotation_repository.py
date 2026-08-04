from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
import logging
from app.models.domain_models import QuotationModel

logger = logging.getLogger(__name__)

class QuotationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["quotations"]

    async def get_quotations_by_service_and_city(self, service_id: str, city: str, limit: int = 100) -> List[QuotationModel]:
        """
        Fetches historical quotations for a specific service and city to perform pricing analysis.
        Limits the results to the most recent ones.
        """
        try:
            # We assume quotations have a reference to service_id and city.
            # In Ally, quotations are linked to bookings. For this repository, 
            # we query quotations directly assuming denormalized metadata or join-like retrieval 
            # (here we just use a flat query for demonstration/Phase 5.4 requirements)
            query = {
                "service_id": service_id,
                "city": city,
                "status": {"$in": ["accepted", "completed"]} # Use successful quotes for accurate pricing
            }
            cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
            
            quotations = []
            async for doc in cursor:
                quotations.append(QuotationModel(
                    id=str(doc.get("_id")),
                    booking_id=str(doc.get("booking_id")),
                    worker_id=str(doc.get("worker_id")),
                    amount=float(doc.get("amount", 0.0)),
                    status=doc.get("status", "pending"),
                    created_at=doc.get("created_at", "")
                ))
            return quotations
        except Exception as e:
            logger.error(f"Error fetching quotations: {str(e)}")
            return []
