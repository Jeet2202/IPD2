from datetime import datetime
from typing import List, Dict, Any, Optional
import time

from app.repositories.analytics.analytics_booking_repository import AnalyticsBookingRepository
from app.repositories.analytics.analytics_worker_repository import AnalyticsWorkerRepository
from app.repositories.analytics.analytics_customer_repository import AnalyticsCustomerRepository
from app.repositories.analytics.analytics_service_repository import AnalyticsServiceRepository
from app.repositories.analytics.analytics_search_repository import AnalyticsSearchRepository
from app.repositories.analytics.analytics_pricing_repository import AnalyticsPricingRepository

from app.services.analytics.chart_service import ChartService
from app.services.analytics.metrics_service import MetricsService
from app.services.analytics.insight_service import InsightService

from app.schemas.analytics import (
    DashboardStats, BookingAnalytics, WorkerAnalytics, CustomerAnalytics, 
    ServiceAnalytics, PricingAnalytics, SearchAnalytics, RuleBasedInsight
)

class AnalyticsOrchestrator:
    def __init__(
        self,
        booking_repo: AnalyticsBookingRepository,
        worker_repo: AnalyticsWorkerRepository,
        customer_repo: AnalyticsCustomerRepository,
        service_repo: AnalyticsServiceRepository,
        search_repo: AnalyticsSearchRepository,
        pricing_repo: AnalyticsPricingRepository
    ):
        self.booking_repo = booking_repo
        self.worker_repo = worker_repo
        self.customer_repo = customer_repo
        self.service_repo = service_repo
        self.search_repo = search_repo
        self.pricing_repo = pricing_repo
        
        # Simple cache for dashboard
        self._dashboard_cache = None
        self._dashboard_cache_time = 0

    async def get_dashboard_stats(self, cache_ttl: int = 300) -> DashboardStats:
        current_time = time.time()
        if self._dashboard_cache and (current_time - self._dashboard_cache_time) < cache_ttl:
            return self._dashboard_cache

        # Calculate "today" boundaries
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Fetch required metrics concurrently or sequentially (sequential for simplicity here)
        booking_status_counts = await self.booking_repo.get_status_counts()
        today_booking_counts = await self.booking_repo.get_status_counts(start_date=today_start)
        today_revenue = await self.booking_repo.get_total_revenue(start_date=today_start)
        
        worker_status_counts = await self.worker_repo.get_worker_status_counts()
        avg_rating = await self.worker_repo.get_average_rating()
        
        pricing_metrics = await self.pricing_repo.get_price_metrics()
        
        service_popularity = await self.service_repo.get_service_popularity(limit=1)
        top_service = service_popularity[0]["service_name"] if service_popularity else "None"
        
        category_dist = await self.service_repo.get_category_distribution()
        top_category = category_dist[0]["category_name"] if category_dist else "None"
        
        stats = DashboardStats(
            today_bookings=sum(today_booking_counts.values()),
            today_revenue=today_revenue,
            active_workers=worker_status_counts.get("active", 0) + worker_status_counts.get("busy", 0),
            online_workers=worker_status_counts.get("active", 0),
            completed_jobs=booking_status_counts.get("completed", 0),
            pending_jobs=booking_status_counts.get("pending", 0) + booking_status_counts.get("requested", 0),
            average_rating=round(avg_rating, 2),
            average_price=round(pricing_metrics["avg_quote"], 2),
            top_category=top_category,
            top_service=top_service,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self._dashboard_cache = stats
        self._dashboard_cache_time = current_time
        return stats

    async def get_booking_analytics(self) -> BookingAnalytics:
        status_counts = await self.booking_repo.get_status_counts()
        avg_completion = await self.booking_repo.get_average_completion_time()
        trend_data = await self.booking_repo.get_bookings_over_time(days_back=30)
        
        return BookingAnalytics(
            total_bookings=sum(status_counts.values()),
            completed_bookings=status_counts.get("completed", 0),
            cancelled_bookings=status_counts.get("cancelled", 0) + status_counts.get("rejected", 0),
            pending_bookings=status_counts.get("pending", 0) + status_counts.get("requested", 0),
            active_bookings=status_counts.get("accepted", 0) + status_counts.get("in_progress", 0),
            average_completion_time_hours=round(avg_completion, 2),
            average_response_time_minutes=15.5, # placeholder for future expansion
            bookings_trend=ChartService.format_time_series(trend_data, dataset_label="Bookings")
        )

    async def get_worker_analytics(self) -> WorkerAnalytics:
        status_counts = await self.worker_repo.get_worker_status_counts()
        verification_counts = await self.worker_repo.get_worker_verification_counts()
        avg_rating = await self.worker_repo.get_average_rating()
        avg_quote = await self.worker_repo.get_average_quote_amount()
        
        total = sum(status_counts.values())
        
        return WorkerAnalytics(
            total_workers=total,
            verified_workers=verification_counts.get(True, 0),
            available_workers=status_counts.get("active", 0),
            busy_workers=status_counts.get("busy", 0),
            inactive_workers=status_counts.get("inactive", 0) + status_counts.get("suspended", 0),
            average_rating=round(avg_rating, 2),
            completion_rate=85.5, # placeholder
            acceptance_rate=78.2, # placeholder
            cancellation_rate=12.1, # placeholder
            average_quote=round(avg_quote, 2),
            average_response_time_minutes=12.5, # placeholder
            status_distribution=ChartService.format_status_distribution(status_counts)
        )

    async def get_customer_analytics(self) -> CustomerAnalytics:
        total = await self.customer_repo.get_total_customers()
        new_30d = await self.customer_repo.get_new_customers(days_back=30)
        repeats = await self.customer_repo.get_repeat_customers()
        
        return CustomerAnalytics(
            total_customers=total,
            new_customers_30d=new_30d,
            active_customers_30d=int(total * 0.4), # placeholder estimation
            repeat_customers=repeats,
            average_spend=1250.0, # placeholder
            average_rating_given=4.2 # placeholder
        )

    async def get_service_analytics(self) -> ServiceAnalytics:
        most_req = await self.service_repo.get_service_popularity(limit=5)
        least_req = await self.service_repo.get_service_popularity(limit=5, ascending=True)
        cat_dist = await self.service_repo.get_category_distribution()
        
        return ServiceAnalytics(
            most_requested_services=most_req,
            least_requested_services=least_req,
            most_popular_categories=cat_dist[:5],
            category_distribution=ChartService.format_category_distribution(cat_dist)
        )

    async def get_pricing_analytics(self) -> PricingAnalytics:
        metrics = await self.pricing_repo.get_price_metrics()
        distribution = await self.pricing_repo.get_price_distribution()
        
        return PricingAnalytics(
            average_quote=round(metrics["avg_quote"], 2),
            minimum_quote=round(metrics["min_quote"], 2),
            maximum_quote=round(metrics["max_quote"], 2),
            median_quote=round(metrics["avg_quote"], 2), # approx
            price_variance=round(metrics["std_dev"], 2),
            price_distribution=ChartService.format_time_series(distribution, label_key="_id", value_key="count", dataset_label="Price Distribution")
        )

    async def get_search_analytics(self) -> SearchAnalytics:
        total = await self.search_repo.get_total_searches()
        trending = await self.search_repo.get_trending_searches(limit=10)
        success_rate = await self.search_repo.get_search_success_rate()
        
        return SearchAnalytics(
            total_searches=total,
            success_rate=round(success_rate, 2),
            most_searched_services=[], # derived from bookings/search
            most_searched_categories=[],
            trending_searches=trending
        )

    async def get_insights(self) -> List[RuleBasedInsight]:
        # Generate some insights based on current data
        stats = await self.get_dashboard_stats()
        
        booking_insights = InsightService.generate_booking_insights(
            today_bookings=stats.today_bookings,
            active_bookings=stats.pending_jobs + stats.active_workers,
            top_service=stats.top_service
        )
        
        worker_insights = InsightService.generate_worker_insights(
            active_workers=stats.active_workers,
            avg_rating=stats.average_rating
        )
        
        return booking_insights + worker_insights
