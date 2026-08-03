from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Chart Data Schemas
# -----------------------------------------------------------------------------
class ChartDataset(BaseModel):
    label: str
    data: List[Union[int, float]]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[ChartDataset]

# -----------------------------------------------------------------------------
# Insight Schemas
# -----------------------------------------------------------------------------
class RuleBasedInsight(BaseModel):
    insight: str
    sentiment: str = Field(..., description="positive, negative, or neutral")
    metric_type: str = Field(..., description="e.g., booking, revenue, worker")

# -----------------------------------------------------------------------------
# Dashboard & Specific Analytics Schemas
# -----------------------------------------------------------------------------
class DashboardStats(BaseModel):
    today_bookings: int
    today_revenue: float
    active_workers: int
    online_workers: int
    completed_jobs: int
    pending_jobs: int
    average_rating: float
    average_price: float
    top_category: str
    top_service: str
    timestamp: str

class BookingAnalytics(BaseModel):
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    pending_bookings: int
    active_bookings: int
    average_completion_time_hours: float
    average_response_time_minutes: float
    bookings_trend: ChartData

class WorkerAnalytics(BaseModel):
    total_workers: int
    verified_workers: int
    available_workers: int
    busy_workers: int
    inactive_workers: int
    average_rating: float
    completion_rate: float
    acceptance_rate: float
    cancellation_rate: float
    average_quote: float
    average_response_time_minutes: float
    status_distribution: ChartData

class CustomerAnalytics(BaseModel):
    total_customers: int
    new_customers_30d: int
    active_customers_30d: int
    repeat_customers: int
    average_spend: float
    average_rating_given: float

class ServiceAnalytics(BaseModel):
    most_requested_services: List[Dict[str, Any]]
    least_requested_services: List[Dict[str, Any]]
    most_popular_categories: List[Dict[str, Any]]
    category_distribution: ChartData

class PricingAnalytics(BaseModel):
    average_quote: float
    minimum_quote: float
    maximum_quote: float
    median_quote: float
    price_variance: float
    price_distribution: ChartData

class RecommendationAnalytics(BaseModel):
    total_requests: int
    acceptance_rate: float
    average_score: float

class SearchAnalytics(BaseModel):
    total_searches: int
    success_rate: float
    most_searched_services: List[Dict[str, Any]]
    most_searched_categories: List[Dict[str, Any]]
    trending_searches: List[str]

# -----------------------------------------------------------------------------
# Export Schemas
# -----------------------------------------------------------------------------
class ExportRequest(BaseModel):
    entity: str = Field(..., description="bookings, workers, customers, services, pricing")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format: str = Field(default="csv", description="csv or json")

class ExportResponse(BaseModel):
    status: str
    message: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    record_count: int
