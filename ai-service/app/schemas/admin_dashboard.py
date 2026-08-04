from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class OverviewStats(BaseModel):
    todays_bookings: int
    todays_revenue: float
    weekly_revenue: float
    monthly_revenue: float
    pending_bookings: int
    completed_jobs: int
    cancelled_jobs: int
    available_workers: int
    busy_workers: int
    platform_health: float
    average_rating: float
    average_response_time: float

class BusinessIntelligence(BaseModel):
    business_growth_summary: str
    revenue_growth: float
    booking_growth: float
    customer_growth: float
    worker_growth: float
    top_categories: List[Dict[str, Any]]
    top_services: List[Dict[str, Any]]
    top_cities: List[str]
    fastest_growing_areas: List[str]

class MarketplaceIntelligence(BaseModel):
    demand_vs_supply_ratio: float
    worker_shortages: List[Dict[str, Any]]
    worker_distribution: Dict[str, int]
    booking_distribution: Dict[str, int]
    area_coverage: float
    service_availability: Dict[str, float]
    low_supply_areas: List[str]
    high_demand_areas: List[str]
    market_balance: str

class WorkerIntelligence(BaseModel):
    top_performing_workers: List[Dict[str, Any]]
    inactive_workers: List[Dict[str, Any]]
    low_rated_workers: List[Dict[str, Any]]
    high_rated_workers: List[Dict[str, Any]]
    cancellation_leaders: List[Dict[str, Any]]
    best_completion_rates: List[Dict[str, Any]]
    fastest_responders: List[Dict[str, Any]]
    slow_responders: List[Dict[str, Any]]
    acceptance_leaders: List[Dict[str, Any]]
    recommendations: List[str]

class CustomerIntelligence(BaseModel):
    active_customers: int
    repeat_customer_rate: float
    average_spend: float
    favourite_services: List[Dict[str, Any]]
    favourite_categories: List[Dict[str, Any]]
    booking_frequency: float
    customer_satisfaction_score: float
    retention_statistics: Dict[str, Any]

class RevenueIntelligence(BaseModel):
    revenue_by_day: Dict[str, float]
    revenue_by_month: Dict[str, float]
    revenue_by_category: Dict[str, float]
    revenue_by_service: Dict[str, float]
    revenue_by_city: Dict[str, float]
    average_order_value: float
    average_quotation: float
    revenue_distribution: Dict[str, float]

class PricingIntelligence(BaseModel):
    average_price: float
    price_distribution: Dict[str, float]
    high_price_areas: List[str]
    low_price_areas: List[str]
    quotation_acceptance_rate: float
    average_worker_quote: float
    price_variance: float
    outlier_pricing: List[Dict[str, Any]]

class RecommendationIntelligence(BaseModel):
    recommendation_requests: int
    acceptance_rate: float
    recommendation_success_rate: float
    recommendation_accuracy: float
    top_recommended_workers: List[Dict[str, Any]]
    recommendation_distribution: Dict[str, int]

class SearchIntelligence(BaseModel):
    most_searched_services: List[Dict[str, Any]]
    most_searched_categories: List[Dict[str, Any]]
    trending_searches: List[str]
    failed_searches: List[str]
    search_success_rate: float
    search_volume: int
    recent_searches: List[str]

class AIInsight(BaseModel):
    id: Optional[str] = None
    insight_text: str
    category: str
    reference_data: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class Anomaly(BaseModel):
    id: Optional[str] = None
    anomaly_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    impact: str
    suggested_action: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class OperationalRecommendation(BaseModel):
    id: Optional[str] = None
    recommendation_text: str
    category: str
    priority: str
    supporting_metrics: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ExecutiveSummary(BaseModel):
    id: Optional[str] = None
    summary_type: str # DAILY, WEEKLY, MONTHLY
    platform_health: str
    achievements: List[str]
    risks: List[str]
    growth: str
    weak_areas: List[str]
    operational_issues: List[str]
    business_opportunities: List[str]
    priority_actions: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class SystemHealth(BaseModel):
    status: str
    uptime: str
    active_services: int
    error_rate: float
    database_health: str

class ExportResponse(BaseModel):
    status: str
    message: str
    file_path: str
    record_count: int
