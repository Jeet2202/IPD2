from typing import Dict, Any

class DemandAnalysisService:
    @staticmethod
    def calculate_demand_level(worker_stats: Dict[str, int]) -> str:
        """
        Calculates the demand level based on worker availability.
        Returns: 'Low', 'Normal', 'High', 'Peak'
        """
        total = worker_stats.get("total", 0)
        available = worker_stats.get("available", 0)
        
        if total == 0:
            return "Normal" # Default if no data
            
        busy_ratio = (total - available) / total
        
        if busy_ratio >= 0.8:
            return "Peak"
        elif busy_ratio >= 0.6:
            return "High"
        elif busy_ratio <= 0.2:
            return "Low"
        else:
            return "Normal"

    @staticmethod
    def get_demand_multiplier(demand_level: str) -> float:
        from app.core.config import settings
        if demand_level == "Peak":
            return settings.DEMAND_MULTIPLIER_PEAK
        elif demand_level == "High":
            return settings.DEMAND_MULTIPLIER_HIGH
        elif demand_level == "Low":
            return settings.DEMAND_MULTIPLIER_LOW
        return 1.0
