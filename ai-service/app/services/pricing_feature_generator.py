from datetime import datetime
from app.schemas.pricing import PricingEstimateRequest

class PricingFeatureGenerator:
    @staticmethod
    def extract_features(request: PricingEstimateRequest) -> dict:
        """
        Extracts boolean/numeric features from the request for pricing rules.
        """
        features = {
            "is_weekend": False,
            "is_urgent": False,
            "is_complex": False
        }
        
        if request.preferred_date:
            try:
                date_obj = datetime.strptime(request.preferred_date, "%Y-%m-%d")
                if date_obj.weekday() >= 5: # 5=Sat, 6=Sun
                    features["is_weekend"] = True
            except ValueError:
                pass
                
        if request.urgency_level in ["high", "critical"]:
            features["is_urgent"] = True
            
        if request.complexity_level == "high":
            features["is_complex"] = True
            
        return features
