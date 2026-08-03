import numpy as np
from typing import List
from app.models.domain_models import QuotationModel
from app.schemas.pricing import HistoricalSummary

class HistoricalAnalysisService:
    @staticmethod
    def analyze_history(quotations: List[QuotationModel]) -> HistoricalSummary:
        """
        Calculates basic statistical measures for historical quotes.
        """
        if not quotations:
            return HistoricalSummary(
                min_price=0.0,
                max_price=0.0,
                avg_price=0.0,
                median_price=0.0,
                std_dev=0.0,
                data_points=0
            )

        prices = [q.amount for q in quotations if q.amount > 0]
        
        if not prices:
            return HistoricalSummary(
                min_price=0.0,
                max_price=0.0,
                avg_price=0.0,
                median_price=0.0,
                std_dev=0.0,
                data_points=0
            )
            
        return HistoricalSummary(
            min_price=float(np.min(prices)),
            max_price=float(np.max(prices)),
            avg_price=float(np.round(np.mean(prices), 2)),
            median_price=float(np.median(prices)),
            std_dev=float(np.round(np.std(prices), 2)),
            data_points=len(prices)
        )
