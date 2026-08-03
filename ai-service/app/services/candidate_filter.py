from typing import List, Tuple
from app.models.domain_models import WorkerModel, BookingModel
from app.services.distance_service import DistanceService
from app.core.config import settings

class CandidateFilter:
    @staticmethod
    def filter_candidates(
        workers: List[WorkerModel], 
        booking: BookingModel
    ) -> List[Tuple[WorkerModel, float]]:
        """
        Filters candidates based on availability, service match, and distance.
        Returns a list of tuples containing the worker and their calculated distance to the booking.
        """
        eligible = []
        
        for worker in workers:
            # 1. Check availability
            if not worker.is_available:
                continue
                
            # 2. Check service match
            if booking.service_id not in worker.services:
                continue
                
            # 3. Check rating threshold
            if worker.rating < settings.MIN_WORKER_RATING:
                continue
                
            # 4. Check distance
            distance = DistanceService.haversine_distance(
                booking.location.coordinates,
                worker.location.coordinates
            )
            
            if distance <= settings.MAX_SEARCH_RADIUS_KM:
                eligible.append((worker, distance))
                
        return eligible
