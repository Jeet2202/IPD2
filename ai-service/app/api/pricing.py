from fastapi import APIRouter, Depends
from app.schemas.pricing import PricingEstimateRequest, PricingEstimateResponse, HistoricalAnalyticsResponse
from app.services.smart_pricing_service import SmartPricingService
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.pricing_repository import PricingRepository
from app.repositories.booking_repository import BookingRepository
from app.core.dependencies import get_db

router = APIRouter(prefix="/pricing", tags=["Smart Pricing"])

def get_pricing_service(db=Depends(get_db)) -> SmartPricingService:
    quotation_repo = QuotationRepository(db)
    marketplace_repo = MarketplaceRepository(db)
    pricing_repo = PricingRepository(db)
    booking_repo = BookingRepository(db)
    return SmartPricingService(quotation_repo, marketplace_repo, pricing_repo, booking_repo)

@router.post("/estimate", response_model=PricingEstimateResponse)
async def estimate_price(
    request: PricingEstimateRequest,
    service: SmartPricingService = Depends(get_pricing_service)
):
    """
    Generates an advisory price estimate for a booking.
    """
    return await service.get_estimate(request)

@router.get("/history/{service_id}", response_model=HistoricalAnalyticsResponse)
async def get_historical_pricing(
    service_id: str,
    city: str,
    service: SmartPricingService = Depends(get_pricing_service)
):
    """
    Returns historical pricing analytics for a specific service in a given city.
    """
    return await service.get_history(service_id, city)
