from app.schemas.pricing import HistoricalSummary

class PricingConfidenceService:
    @staticmethod
    def calculate_confidence(summary: HistoricalSummary, demand_level: str) -> int:
        """
        Calculates a confidence score (0-100) for the price estimate.
        Based on data volume and variance.
        """
        confidence = 50 # Base confidence
        
        # Factor 1: Data Volume
        if summary.data_points >= 20:
            confidence += 30
        elif summary.data_points >= 10:
            confidence += 20
        elif summary.data_points >= 5:
            confidence += 10
        elif summary.data_points == 0:
            confidence -= 30 # Low confidence with no data
            
        # Factor 2: Variance (Standard Deviation vs Avg Price)
        if summary.avg_price > 0:
            cv = summary.std_dev / summary.avg_price # Coefficient of variation
            if cv < 0.1: # Very stable prices
                confidence += 20
            elif cv < 0.2:
                confidence += 10
            elif cv > 0.5: # Highly volatile
                confidence -= 20
                
        # Factor 3: Demand Stability
        if demand_level == "Peak":
            confidence -= 10 # Harder to predict during peak
            
        return max(0, min(100, int(confidence)))
