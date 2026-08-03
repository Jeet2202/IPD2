from typing import List, Tuple
from app.schemas.pricing import HistoricalSummary
from app.models.domain_models import QuotationModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OutlierDetectionService:
    @staticmethod
    def detect_outliers(quotations: List[QuotationModel], summary: HistoricalSummary) -> Tuple[List[QuotationModel], int]:
        """
        Flags quotations that fall outside the acceptable standard deviation range.
        Does not remove them, just counts/flags them for analytical purposes.
        """
        if summary.data_points < 5 or summary.std_dev == 0:
            return quotations, 0
            
        outliers_count = 0
        threshold = settings.OUTLIER_STD_DEV_THRESHOLD * summary.std_dev
        
        lower_bound = summary.avg_price - threshold
        upper_bound = summary.avg_price + threshold
        
        for quote in quotations:
            if quote.amount < lower_bound or quote.amount > upper_bound:
                outliers_count += 1
                logger.debug(f"Quote {quote.id} with amount {quote.amount} flagged as outlier (Bounds: {lower_bound}-{upper_bound})")
                
        return quotations, outliers_count

    @staticmethod
    def clamp_price(calculated_price: float, base_price: float) -> float:
        """
        Ensures the calculated price does not swing too wildly from the base price.
        """
        max_variance = settings.MAX_PRICE_VARIANCE_PERCENT / 100.0
        max_allowed = base_price * (1.0 + max_variance)
        min_allowed = base_price * (1.0 - max_variance)
        
        clamped = max(min_allowed, min(calculated_price, max_allowed))
        return round(clamped, 2)
