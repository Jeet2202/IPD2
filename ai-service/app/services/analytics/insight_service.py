from typing import List, Dict, Any
from app.schemas.analytics import RuleBasedInsight

class InsightService:
    @staticmethod
    def generate_booking_insights(today_bookings: int, active_bookings: int, top_service: str) -> List[RuleBasedInsight]:
        insights = []
        if top_service:
            insights.append(RuleBasedInsight(
                insight=f"{top_service} is currently the most requested service.",
                sentiment="positive",
                metric_type="booking"
            ))
            
        if today_bookings > 50:
            insights.append(RuleBasedInsight(
                insight="High booking volume detected today.",
                sentiment="positive",
                metric_type="booking"
            ))
        elif today_bookings < 5:
            insights.append(RuleBasedInsight(
                insight="Booking volume is lower than usual today.",
                sentiment="neutral",
                metric_type="booking"
            ))
            
        return insights

    @staticmethod
    def generate_worker_insights(active_workers: int, avg_rating: float) -> List[RuleBasedInsight]:
        insights = []
        if active_workers > 0:
            insights.append(RuleBasedInsight(
                insight=f"{active_workers} workers are currently active and available.",
                sentiment="positive",
                metric_type="worker"
            ))
            
        if avg_rating >= 4.5:
            insights.append(RuleBasedInsight(
                insight="Overall worker rating is excellent.",
                sentiment="positive",
                metric_type="worker"
            ))
        elif avg_rating > 0 and avg_rating < 3.5:
            insights.append(RuleBasedInsight(
                insight="Overall worker rating is below target.",
                sentiment="negative",
                metric_type="worker"
            ))
            
        return insights
