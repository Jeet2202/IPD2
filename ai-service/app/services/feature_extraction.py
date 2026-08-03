from typing import Dict, Any
from app.models.domain_models import WorkerModel
from app.core.config import settings

class FeatureExtractionService:
    @staticmethod
    def extract_features(worker: WorkerModel, distance_km: float) -> Dict[str, float]:
        """
        Normalizes worker attributes into a feature vector with scores from 0.0 to 1.0.
        Higher is better.
        """
        features = {}
        
        # Distance Feature: Inverse proportion to max radius
        # 0 km = 1.0 score, MAX_RADIUS km = 0.0 score
        max_dist = max(settings.MAX_SEARCH_RADIUS_KM, 1.0)
        dist_score = max(0.0, (max_dist - distance_km) / max_dist)
        features["distance_score"] = dist_score
        
        # Rating Feature: Linear from min rating to 5.0
        # Rating 5.0 = 1.0 score, MIN_RATING = 0.0 score
        min_rat = settings.MIN_WORKER_RATING
        if worker.rating >= 5.0:
            rating_score = 1.0
        elif worker.rating <= min_rat:
            rating_score = 0.0
        else:
            rating_score = (worker.rating - min_rat) / (5.0 - min_rat)
        features["rating_score"] = rating_score
        
        # Experience Feature: Cap at 10 years for max score
        # 10+ years = 1.0 score
        exp_score = min(1.0, worker.experience_years / 10.0)
        features["experience_score"] = exp_score
        
        # Completion Feature: Direct percentage
        features["completion_score"] = max(0.0, min(1.0, worker.completion_rate / 100.0))
        
        # Availability Feature: Binary
        features["availability_score"] = 1.0 if worker.is_available else 0.0
        
        # Response Time Feature: Inverse. Assume 60 mins is max acceptable for scoring
        # 0 mins = 1.0 score, >=60 mins = 0.0 score
        resp_score = max(0.0, (60.0 - min(worker.avg_response_time_mins, 60.0)) / 60.0)
        features["response_time_score"] = resp_score
        
        return features
