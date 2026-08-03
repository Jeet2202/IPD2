from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

from app.core.dependencies import get_db
from app.core.config import settings

from app.repositories.analytics.analytics_booking_repository import AnalyticsBookingRepository
from app.repositories.analytics.analytics_worker_repository import AnalyticsWorkerRepository
from app.repositories.analytics.analytics_customer_repository import AnalyticsCustomerRepository
from app.repositories.analytics.analytics_service_repository import AnalyticsServiceRepository
from app.repositories.analytics.analytics_search_repository import AnalyticsSearchRepository
from app.repositories.analytics.analytics_pricing_repository import AnalyticsPricingRepository
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator
from app.services.analytics.dataset_builder_service import DatasetBuilderService
from app.services.analytics.export_service import ExportService

from app.schemas.analytics import (
    DashboardStats, BookingAnalytics, WorkerAnalytics, CustomerAnalytics, 
    ServiceAnalytics, PricingAnalytics, SearchAnalytics, RuleBasedInsight,
    ExportRequest, ExportResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Global orchestrator instance for simple caching
_orchestrator_instance = None

def get_orchestrator(db: AsyncIOMotorDatabase = Depends(get_db)) -> AnalyticsOrchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AnalyticsOrchestrator(
            booking_repo=AnalyticsBookingRepository(db),
            worker_repo=AnalyticsWorkerRepository(db),
            customer_repo=AnalyticsCustomerRepository(db),
            service_repo=AnalyticsServiceRepository(db),
            search_repo=AnalyticsSearchRepository(db),
            pricing_repo=AnalyticsPricingRepository(db)
        )
    return _orchestrator_instance

@router.get("/dashboard", response_model=DashboardStats, summary="Get top-level dashboard metrics")
async def get_dashboard(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_dashboard_stats(cache_ttl=settings.ANALYTICS_DASHBOARD_CACHE_TTL_SEC)

@router.get("/bookings", response_model=BookingAnalytics, summary="Get booking analytics and trends")
async def get_bookings(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_booking_analytics()

@router.get("/workers", response_model=WorkerAnalytics, summary="Get worker performance analytics")
async def get_workers(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_worker_analytics()

@router.get("/customers", response_model=CustomerAnalytics, summary="Get customer behavior analytics")
async def get_customers(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_customer_analytics()

@router.get("/services", response_model=ServiceAnalytics, summary="Get service popularity and category distribution")
async def get_services(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_service_analytics()

@router.get("/pricing", response_model=PricingAnalytics, summary="Get pricing variance and distribution")
async def get_pricing(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_pricing_analytics()

@router.get("/recommendations", summary="Get recommendation analytics")
async def get_recommendations():
    # Placeholder for recommendation metrics
    return {
        "total_requests": 1500,
        "acceptance_rate": 85.5,
        "average_score": 92.4,
        "top_recommended_workers": []
    }

@router.get("/search", response_model=SearchAnalytics, summary="Get search behavior and trending queries")
async def get_search(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_search_analytics()

@router.get("/insights", response_model=List[RuleBasedInsight], summary="Get rule-based business insights")
async def get_insights(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)):
    return await orchestrator.get_insights()

@router.post("/datasets/export", response_model=ExportResponse, summary="Generate and export a dataset for ML")
async def export_dataset(request: ExportRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    if request.entity == "bookings":
        cursor = db["bookings"].find({}).limit(1000) # In real scenario, paginate or use async stream
        raw_data = await cursor.to_list(length=1000)
        flat_data = DatasetBuilderService.flatten_booking_dataset(raw_data)
        
        if request.format == "csv":
            filepath = ExportService.export_csv(flat_data, "bookings")
        else:
            filepath = ExportService.export_json(flat_data, "bookings")
            
        return ExportResponse(
            status="success",
            message="Dataset exported successfully",
            file_path=filepath,
            record_count=len(flat_data)
        )
    else:
        raise HTTPException(status_code=400, detail=f"Export for entity {request.entity} is not supported yet.")

@router.get("/datasets/download", summary="Download an exported dataset")
async def download_dataset(filepath: str):
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Ensure it's in the export dir to prevent path traversal
    export_dir = os.path.abspath(settings.ANALYTICS_DATASET_EXPORT_DIR)
    abs_filepath = os.path.abspath(filepath)
    if not abs_filepath.startswith(export_dir):
        raise HTTPException(status_code=403, detail="Access denied")
        
    return FileResponse(path=abs_filepath, filename=os.path.basename(abs_filepath))
