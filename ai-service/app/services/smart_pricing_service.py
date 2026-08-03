import logging
from app.core.config import settings
from app.schemas.pricing import PricingEstimateRequest, PricingEstimateResponse, HistoricalAnalyticsResponse
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.pricing_repository import PricingRepository
from app.repositories.booking_repository import BookingRepository
from app.services.historical_analysis_service import HistoricalAnalysisService
from app.services.demand_analysis_service import DemandAnalysisService
from app.services.outlier_detection_service import OutlierDetectionService
from app.services.pricing_confidence_service import PricingConfidenceService
from app.services.pricing_explanation_service import PricingExplanationService
from app.services.pricing_feature_generator import PricingFeatureGenerator

logger = logging.getLogger(__name__)

class SmartPricingService:
    def __init__(
        self,
        quotation_repo: QuotationRepository,
        marketplace_repo: MarketplaceRepository,
        pricing_repo: PricingRepository,
        booking_repo: BookingRepository
    ):
        self.quotation_repo = quotation_repo
        self.marketplace_repo = marketplace_repo
        self.pricing_repo = pricing_repo
        self.booking_repo = booking_repo

    async def get_estimate(self, request: PricingEstimateRequest) -> PricingEstimateResponse:
        logger.info(f"Generating price estimate for booking {request.booking_id}")
        
        booking = await self.booking_repo.get_booking_by_id(request.booking_id)
        if not booking:
            raise ValueError(f"Booking {request.booking_id} not found")

        service_id = booking.service_id
        
        # 1. Fetch base price
        base_price = await self.pricing_repo.get_service_base_price(service_id)
        
        # 2. Historical Analysis
        quotations = await self.quotation_repo.get_quotations_by_service_and_city(service_id, request.city)
        historical_summary = HistoricalAnalysisService.analyze_history(quotations)
        _, outlier_count = OutlierDetectionService.detect_outliers(quotations, historical_summary)
        
        # 3. Demand Analysis
        worker_stats = await self.marketplace_repo.get_worker_stats(service_id, request.city)
        demand_level = DemandAnalysisService.calculate_demand_level(worker_stats)
        demand_multiplier = DemandAnalysisService.get_demand_multiplier(demand_level)
        
        # 4. Feature Extraction
        features = PricingFeatureGenerator.extract_features(request)
        
        # 5. Price Calculation
        calculated_price = base_price * request.estimated_duration_hours
        
        # Apply Historical Weight if we have enough data
        if historical_summary.data_points >= 5:
            calculated_price = (calculated_price * (1.0 - settings.PRICE_WEIGHT_HISTORICAL)) + (historical_summary.avg_price * settings.PRICE_WEIGHT_HISTORICAL)

        # Apply Multipliers
        calculated_price *= demand_multiplier
        
        if features.get("is_weekend"):
            calculated_price *= settings.PRICE_MULTIPLIER_WEEKEND
        if features.get("is_urgent"):
            calculated_price *= settings.PRICE_MULTIPLIER_URGENT
            
        # Ensure it doesn't swing too wildly
        final_price = OutlierDetectionService.clamp_price(calculated_price, base_price * request.estimated_duration_hours)
        
        # 6. Confidence & Risk
        confidence = PricingConfidenceService.calculate_confidence(historical_summary, demand_level)
        risk_level = "high" if confidence < 40 else "medium" if confidence < 70 else "low"
        
        # 7. Explanations
        reasons = PricingExplanationService.generate_reasons(features, demand_level, historical_summary.avg_price)
        
        return PricingEstimateResponse(
            booking_id=request.booking_id,
            estimated_price=final_price,
            min_price=historical_summary.min_price if historical_summary.data_points > 0 else final_price * 0.8,
            max_price=historical_summary.max_price if historical_summary.data_points > 0 else final_price * 1.2,
            confidence_percentage=confidence,
            risk_level=risk_level,
            reasons=reasons,
            demand_level=demand_level,
            historical_summary=historical_summary
        )

    async def get_history(self, service_id: str, city: str) -> HistoricalAnalyticsResponse:
        quotations = await self.quotation_repo.get_quotations_by_service_and_city(service_id, city)
        historical_summary = HistoricalAnalysisService.analyze_history(quotations)
        _, outlier_count = OutlierDetectionService.detect_outliers(quotations, historical_summary)
        
        recent_prices = [q.amount for q in quotations[:10]] # Get last 10 prices for trend
        
        return HistoricalAnalyticsResponse(
            service_id=service_id,
            city=city,
            historical_summary=historical_summary,
            recent_price_trends=recent_prices,
            outliers_detected=outlier_count
        )
