from typing import List, Dict, Any

class MetricsService:
    @staticmethod
    def calculate_variance(current: float, previous: float) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100.0

    @staticmethod
    def calculate_percentage(part: float, whole: float) -> float:
        if whole == 0:
            return 0.0
        return (part / whole) * 100.0
