from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import logging
from app.models.domain_models import WorkerModel, Location

logger = logging.getLogger(__name__)

class WorkerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["workers"]

    async def get_active_workers(self) -> List[WorkerModel]:
        try:
            # Only fetch workers who are active, verified, and not suspended
            cursor = self.collection.find({
                "is_active": True,
                "is_verified": True,
                "is_suspended": {"$ne": True}
            })
            
            workers = []
            async for doc in cursor:
                try:
                    worker = WorkerModel(
                        id=str(doc.get("_id")),
                        is_active=doc.get("is_active", True),
                        is_verified=doc.get("is_verified", True),
                        is_suspended=doc.get("is_suspended", False),
                        services=[str(s) for s in doc.get("services", [])],
                        location=Location(
                            coordinates=doc.get("location", {}).get("coordinates", [0.0, 0.0])
                        ),
                        rating=float(doc.get("rating", 0.0)),
                        experience_years=int(doc.get("experience_years", 0)),
                        completion_rate=float(doc.get("completion_rate", 0.0)),
                        acceptance_rate=float(doc.get("acceptance_rate", 0.0)),
                        cancellation_rate=float(doc.get("cancellation_rate", 0.0)),
                        avg_response_time_mins=float(doc.get("avg_response_time_mins", 60.0)),
                        is_available=doc.get("is_available", True)
                    )
                    workers.append(worker)
                except Exception as e:
                    logger.warning(f"Skipping worker {doc.get('_id')} due to parsing error: {str(e)}")
                    continue
                    
            return workers
        except Exception as e:
            logger.error(f"Error fetching workers: {str(e)}")
            raise
