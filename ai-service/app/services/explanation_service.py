from typing import Dict, List

class ExplanationService:
    @staticmethod
    def generate_explanations(features: Dict[str, float]) -> List[str]:
        """
        Analyzes the feature vector and generates human-readable reasons for recommendation.
        """
        reasons = []
        
        if features.get("rating_score", 0.0) >= 0.8:
            reasons.append("Highly Rated")
            
        if features.get("distance_score", 0.0) >= 0.8:
            reasons.append("Nearby")
            
        if features.get("experience_score", 0.0) >= 0.5: # 5+ years
            reasons.append("Experienced")
            
        if features.get("response_time_score", 0.0) >= 0.8: # < 12 mins
            reasons.append("Fast Responder")
            
        if features.get("completion_score", 0.0) >= 0.9: # 90%+ completion
            reasons.append("Excellent Completion History")
            
        # Ensure there's at least one reason if they made it this far
        if not reasons:
            reasons.append("Good Match")
            
        return reasons
