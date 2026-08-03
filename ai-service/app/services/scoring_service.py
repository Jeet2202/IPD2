from typing import Dict
from app.core.config import settings

class ScoringService:
    @staticmethod
    def calculate_score(features: Dict[str, float]) -> float:
        """
        Calculates a weighted score based on extracted features and configured weights.
        Returns a score between 0.0 and 100.0.
        """
        score = 0.0
        
        score += features.get("distance_score", 0.0) * settings.WEIGHT_DISTANCE
        score += features.get("rating_score", 0.0) * settings.WEIGHT_RATING
        score += features.get("experience_score", 0.0) * settings.WEIGHT_EXPERIENCE
        score += features.get("completion_score", 0.0) * settings.WEIGHT_COMPLETION
        score += features.get("availability_score", 0.0) * settings.WEIGHT_AVAILABILITY
        score += features.get("response_time_score", 0.0) * settings.WEIGHT_RESPONSE_TIME
        
        # Normalize to out of 100
        total_weight = (
            settings.WEIGHT_DISTANCE + 
            settings.WEIGHT_RATING + 
            settings.WEIGHT_EXPERIENCE + 
            settings.WEIGHT_COMPLETION + 
            settings.WEIGHT_AVAILABILITY + 
            settings.WEIGHT_RESPONSE_TIME
        )
        
        if total_weight > 0:
            final_score = (score / total_weight) * 100.0
        else:
            final_score = 0.0
            
        return round(final_score, 2)
