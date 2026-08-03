import pytest
import os
import json
from unittest.mock import AsyncMock, patch

from app.services.analytics.metrics_service import MetricsService
from app.services.analytics.chart_service import ChartService
from app.services.analytics.insight_service import InsightService
from app.services.analytics.dataset_builder_service import DatasetBuilderService
from app.services.analytics.export_service import ExportService
from app.schemas.analytics import ExportRequest

class TestMetricsService:
    def test_calculate_variance_positive(self):
        assert MetricsService.calculate_variance(150, 100) == 50.0

    def test_calculate_variance_negative(self):
        assert MetricsService.calculate_variance(50, 100) == -50.0

    def test_calculate_variance_zero_prev(self):
        assert MetricsService.calculate_variance(100, 0) == 100.0
        assert MetricsService.calculate_variance(0, 0) == 0.0

    def test_calculate_percentage(self):
        assert MetricsService.calculate_percentage(25, 100) == 25.0
        assert MetricsService.calculate_percentage(0, 100) == 0.0
        assert MetricsService.calculate_percentage(50, 0) == 0.0

class TestChartService:
    def test_format_time_series(self):
        data = [
            {"_id": "2023-01-01", "count": 10},
            {"_id": "2023-01-02", "count": 15}
        ]
        result = ChartService.format_time_series(data)
        assert len(result.labels) == 2
        assert result.labels[0] == "2023-01-01"
        assert len(result.datasets) == 1
        assert result.datasets[0].data == [10, 15]

    def test_format_category_distribution(self):
        data = [
            {"category_name": "Plumbing", "count": 50},
            {"category_name": "Cleaning", "count": 30}
        ]
        result = ChartService.format_category_distribution(data)
        assert result.labels == ["Plumbing", "Cleaning"]
        assert result.datasets[0].data == [50, 30]

    def test_format_status_distribution(self):
        data = {"active": 10, "busy": 5}
        result = ChartService.format_status_distribution(data)
        assert result.labels == ["active", "busy"]
        assert result.datasets[0].data == [10, 5]

class TestInsightService:
    def test_generate_booking_insights(self):
        insights = InsightService.generate_booking_insights(100, 20, "Plumbing")
        assert len(insights) >= 2
        assert any(i.sentiment == "positive" and "volume" in i.insight.lower() for i in insights)
        assert any("Plumbing" in i.insight for i in insights)

    def test_generate_worker_insights(self):
        insights = InsightService.generate_worker_insights(10, 4.8)
        assert len(insights) == 2
        assert any("excellent" in i.insight.lower() for i in insights)

class TestDatasetBuilderService:
    def test_flatten_booking_dataset(self):
        raw_data = [
            {
                "_id": "b1",
                "user_id": "u1",
                "assigned_worker_id": "w1",
                "final_price": 500,
                "created_at": "2023-10-01T10:00:00Z"
            }
        ]
        flattened = DatasetBuilderService.flatten_booking_dataset(raw_data)
        assert len(flattened) == 1
        assert flattened[0]["booking_id"] == "b1"
        assert flattened[0]["final_price"] == 500
        assert "day_of_week" in flattened[0]
        assert flattened[0]["is_weekend"] in [0, 1]

class TestExportService:
    def test_export_json(self, tmp_path):
        import app.core.config
        original_dir = app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR
        app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR = str(tmp_path)
        
        data = [{"col1": "val1", "col2": 2}]
        filepath = ExportService.export_json(data, "test_entity")
        
        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            loaded = json.load(f)
            assert loaded == data
            
        app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR = original_dir

    def test_export_csv(self, tmp_path):
        import app.core.config
        original_dir = app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR
        app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR = str(tmp_path)
        
        data = [{"col1": "val1", "col2": 2}]
        filepath = ExportService.export_csv(data, "test_entity")
        
        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
            assert "col1,col2" in content
            assert "val1,2" in content
            
        app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR = original_dir

from app.api.analytics import get_orchestrator
from unittest.mock import AsyncMock

async def override_get_orchestrator():
    from app.schemas.analytics import DashboardStats, BookingAnalytics, ChartData, WorkerAnalytics, CustomerAnalytics, ServiceAnalytics, PricingAnalytics, SearchAnalytics, RuleBasedInsight
    mock = AsyncMock()
    # Mock return values for endpoint responses to pass schema validation
    mock.get_dashboard_stats.return_value = DashboardStats(
        today_bookings=1, today_revenue=100.0, active_workers=1, online_workers=1, completed_jobs=1, pending_jobs=1, average_rating=5.0, average_price=100.0, top_category="Cat", top_service="Srv", timestamp="2023-01-01T00:00:00"
    )
    mock.get_booking_analytics.return_value = BookingAnalytics(
        total_bookings=1, completed_bookings=1, cancelled_bookings=0, pending_bookings=0, active_bookings=0, average_completion_time_hours=1.0, average_response_time_minutes=1.0, bookings_trend=ChartData(labels=[], datasets=[])
    )
    mock.get_worker_analytics.return_value = WorkerAnalytics(
        total_workers=1, verified_workers=1, available_workers=1, busy_workers=0, inactive_workers=0, average_rating=5.0, completion_rate=100.0, acceptance_rate=100.0, cancellation_rate=0.0, average_quote=100.0, average_response_time_minutes=1.0, status_distribution=ChartData(labels=[], datasets=[])
    )
    mock.get_customer_analytics.return_value = CustomerAnalytics(
        total_customers=1, new_customers_30d=1, active_customers_30d=1, repeat_customers=1, average_spend=100.0, average_rating_given=5.0
    )
    mock.get_service_analytics.return_value = ServiceAnalytics(
        most_requested_services=[], least_requested_services=[], most_popular_categories=[], category_distribution=ChartData(labels=[], datasets=[])
    )
    mock.get_pricing_analytics.return_value = PricingAnalytics(
        average_quote=100.0, minimum_quote=50.0, maximum_quote=150.0, median_quote=100.0, price_variance=10.0, price_distribution=ChartData(labels=[], datasets=[])
    )
    mock.get_search_analytics.return_value = SearchAnalytics(
        total_searches=1, success_rate=100.0, most_searched_services=[], most_searched_categories=[], trending_searches=[]
    )
    mock.get_insights.return_value = [RuleBasedInsight(insight="Test", sentiment="neutral", metric_type="booking")]
    return mock

@pytest.mark.asyncio
async def test_analytics_endpoints(async_client):
    """
    Test the analytics API endpoints via the test client.
    Because we haven't loaded actual DB data in test DB, they might return mostly 0s, 
    but we can assert the schema structure is correct and status is 200.
    """
    endpoints = [
        "/analytics/dashboard",
        "/analytics/bookings",
        "/analytics/workers",
        "/analytics/customers",
        "/analytics/services",
        "/analytics/pricing",
        "/analytics/recommendations",
        "/analytics/search",
        "/analytics/insights"
    ]
    
    from app.main import app as main_app
    main_app.dependency_overrides[get_orchestrator] = override_get_orchestrator
    
    for ep in endpoints:
        response = await async_client.get(ep)
        assert response.status_code == 200, f"Endpoint {ep} failed with {response.status_code} - {response.text}"
        
    main_app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_analytics_export_endpoint(async_client, tmp_path):
    import app.core.config
    original_dir = app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR
    app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR = str(tmp_path)

    payload = {
        "entity": "bookings",
        "format": "json"
    }
    
    from app.core.dependencies import get_db
    
    async def override_get_db_for_export():
        mock_db = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{"_id": "b1", "final_price": 100}]
        mock_db.__getitem__.return_value.find.return_value.limit.return_value = mock_cursor
        return mock_db

    from app.main import app as main_app
    main_app.dependency_overrides[get_db] = override_get_db_for_export
    
    response = await async_client.post("/analytics/datasets/export", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "file_path" in data
    
    main_app.dependency_overrides.clear()
    app.core.config.settings.ANALYTICS_DATASET_EXPORT_DIR = original_dir
