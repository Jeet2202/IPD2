from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.core.config import settings

# Repositories
from app.repositories.admin_dashboard.insight_repository import InsightRepository
from app.repositories.admin_dashboard.recommendation_repository import RecommendationRepository
from app.repositories.admin_dashboard.anomaly_repository import AnomalyRepository
from app.repositories.admin_dashboard.executive_summary_repository import ExecutiveSummaryRepository
from app.repositories.admin_dashboard.report_repository import ReportRepository

# Analytics orchestrator
from app.api.analytics import get_orchestrator
from app.services.analytics.analytics_orchestrator import AnalyticsOrchestrator

# Services
from app.services.admin_dashboard.dashboard_service import DashboardService
from app.services.admin_dashboard.business_intelligence_service import BusinessIntelligenceService
from app.services.admin_dashboard.marketplace_intelligence_service import MarketplaceIntelligenceService
from app.services.admin_dashboard.worker_intelligence_service import WorkerIntelligenceService
from app.services.admin_dashboard.customer_intelligence_service import CustomerIntelligenceService
from app.services.admin_dashboard.revenue_intelligence_service import RevenueIntelligenceService
from app.services.admin_dashboard.pricing_intelligence_service import PricingIntelligenceService
from app.services.admin_dashboard.search_intelligence_service import SearchIntelligenceService
from app.services.admin_dashboard.insight_service import InsightService
from app.services.admin_dashboard.anomaly_detection_service import AnomalyDetectionService
from app.services.admin_dashboard.recommendation_service import RecommendationService
from app.services.admin_dashboard.executive_summary_service import ExecutiveSummaryService
from app.services.admin_dashboard.report_service import ReportService

# Schemas
from app.schemas.admin_dashboard import (
    OverviewStats, BusinessIntelligence, MarketplaceIntelligence, WorkerIntelligence,
    CustomerIntelligence, RevenueIntelligence, PricingIntelligence, SearchIntelligence,
    AIInsight, Anomaly, OperationalRecommendation, ExecutiveSummary, SystemHealth,
    ExportResponse
)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard Intelligence"])

# Dependencies to inject services
def get_dashboard_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> DashboardService:
    return DashboardService(orchestrator)

def get_bi_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> BusinessIntelligenceService:
    return BusinessIntelligenceService(orchestrator)

def get_marketplace_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> MarketplaceIntelligenceService:
    return MarketplaceIntelligenceService(orchestrator)

def get_worker_intel_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> WorkerIntelligenceService:
    return WorkerIntelligenceService(orchestrator)

def get_customer_intel_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> CustomerIntelligenceService:
    return CustomerIntelligenceService(orchestrator)

def get_revenue_intel_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> RevenueIntelligenceService:
    return RevenueIntelligenceService(orchestrator)

def get_pricing_intel_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> PricingIntelligenceService:
    return PricingIntelligenceService(orchestrator)

def get_search_intel_service(orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> SearchIntelligenceService:
    return SearchIntelligenceService(orchestrator)

def get_insight_service(db: AsyncIOMotorDatabase = Depends(get_db), orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> InsightService:
    return InsightService(orchestrator, InsightRepository(db))

def get_anomaly_service(db: AsyncIOMotorDatabase = Depends(get_db), orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> AnomalyDetectionService:
    return AnomalyDetectionService(orchestrator, AnomalyRepository(db))

def get_recommendation_service(db: AsyncIOMotorDatabase = Depends(get_db), orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> RecommendationService:
    return RecommendationService(orchestrator, RecommendationRepository(db))

def get_executive_summary_service(db: AsyncIOMotorDatabase = Depends(get_db), orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator)) -> ExecutiveSummaryService:
    return ExecutiveSummaryService(orchestrator, ExecutiveSummaryRepository(db))

def get_report_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> ReportService:
    return ReportService(ReportRepository(db))

# Note: Security (Admin auth) would typically be applied via dependency here or in main.py router inclusion

@router.get("/dashboard", response_model=OverviewStats)
@router.get("/overview", response_model=OverviewStats)
async def get_overview(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_overview_stats()

@router.get("/business", response_model=BusinessIntelligence)
async def get_business_intelligence(service: BusinessIntelligenceService = Depends(get_bi_service)):
    return await service.get_business_intelligence()

@router.get("/marketplace", response_model=MarketplaceIntelligence)
async def get_marketplace_intelligence(service: MarketplaceIntelligenceService = Depends(get_marketplace_service)):
    return await service.get_marketplace_intelligence()

@router.get("/workers", response_model=WorkerIntelligence)
async def get_worker_intelligence(service: WorkerIntelligenceService = Depends(get_worker_intel_service)):
    return await service.get_worker_intelligence()

@router.get("/customers", response_model=CustomerIntelligence)
async def get_customer_intelligence(service: CustomerIntelligenceService = Depends(get_customer_intel_service)):
    return await service.get_customer_intelligence()

@router.get("/revenue", response_model=RevenueIntelligence)
async def get_revenue_intelligence(service: RevenueIntelligenceService = Depends(get_revenue_intel_service)):
    return await service.get_revenue_intelligence()

@router.get("/pricing", response_model=PricingIntelligence)
async def get_pricing_intelligence(service: PricingIntelligenceService = Depends(get_pricing_intel_service)):
    return await service.get_pricing_intelligence()

@router.get("/search", response_model=SearchIntelligence)
async def get_search_intelligence(service: SearchIntelligenceService = Depends(get_search_intel_service)):
    return await service.get_search_intelligence()

@router.get("/recommendations", response_model=List[OperationalRecommendation])
async def get_recommendations(service: RecommendationService = Depends(get_recommendation_service)):
    return await service.get_recent_recommendations()

@router.get("/insights", response_model=List[AIInsight])
async def get_insights(service: InsightService = Depends(get_insight_service)):
    return await service.get_recent_insights()

@router.get("/anomalies", response_model=List[Anomaly])
async def get_anomalies(service: AnomalyDetectionService = Depends(get_anomaly_service)):
    return await service.get_recent_anomalies()

@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_system_health()

@router.get("/executive-summary", response_model=ExecutiveSummary)
async def get_executive_summary(type: str = Query("DAILY", description="DAILY, WEEKLY, or MONTHLY"), service: ExecutiveSummaryService = Depends(get_executive_summary_service)):
    return await service.get_latest_summary(type)

class ExportRequest(BaseModel):
    report_name: str
    format: str = "csv" # csv, json
    
@router.post("/reports/export", response_model=ExportResponse)
async def export_report(request: ExportRequest, 
                        bi_service: BusinessIntelligenceService = Depends(get_bi_service),
                        report_service: ReportService = Depends(get_report_service)):
    
    # We could fetch any data source based on report_name. For demo, let's fetch BI.
    if request.report_name == "business_intelligence":
        bi = await bi_service.get_business_intelligence()
        # Convert Pydantic to dict list for CSV compatibility if needed, or just let report_service handle JSON
        data = [bi.model_dump()]
    else:
        # Default mock data
        data = [{"id": 1, "metric": "test"}]
        
    return await report_service.generate_report(request.report_name, request.format, data)

@router.get("/reports", response_model=List[ExportResponse])
async def get_reports(db: AsyncIOMotorDatabase = Depends(get_db)):
    repo = ReportRepository(db)
    return await repo.get_recent_reports()
