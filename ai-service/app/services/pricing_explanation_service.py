from typing import List

class PricingExplanationService:
    @staticmethod
    def generate_reasons(features: dict, demand_level: str, historical_avg: float) -> List[str]:
        """
        Generates human-readable reasons for the estimated price.
        """
        reasons = []
        
        if features.get("is_urgent"):
            reasons.append("Premium applied for urgent request")
            
        if features.get("is_weekend"):
            reasons.append("Weekend pricing in effect")
            
        if features.get("is_complex"):
            reasons.append("Adjusted for high complexity")
            
        if demand_level in ["High", "Peak"]:
            reasons.append(f"Price increased due to {demand_level.lower()} demand in locality")
        elif demand_level == "Low":
            reasons.append("Discount applied due to low demand")
            
        if historical_avg > 0:
            reasons.append("Aligned with recent historical averages in your area")
            
        if not reasons:
            reasons.append("Standard base rate applied")
            
        return reasons
