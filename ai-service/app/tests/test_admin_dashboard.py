import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from app.main import app
from app.core.dependencies import get_db
from app.api.analytics import get_orchestrator
from app.schemas.analytics import DashboardStats, BookingAnalytics, ChartData, WorkerAnalytics, CustomerAnalytics, ServiceAnalytics, PricingAnalytics, SearchAnalytics

async def override_get_orchestrator():
    mock = AsyncMock()
    mock.get_dashboard_stats.return_value = DashboardStats(
        total_revenue=100.0, pending_jobs=1, completed_jobs=1, active_jobs=1,
        today_bookings=1, today_revenue=100.0, active_workers=1, online_workers=1, 
        average_rating=5.0, average_price=100.0, top_category="Cat", top_service="Srv", 
        timestamp="2023-01-01T00:00:00"
    )
    mock.get_booking_analytics.return_value = BookingAnalytics(
        total_bookings=1, completed_bookings=1, cancelled_bookings=0, pending_bookings=0, active_bookings=0, 
        completion_rate=100.0, average_completion_time_hours=1.0, average_response_time_minutes=1.0, 
        bookings_trend=ChartData(labels=[], datasets=[])
    )
    mock.get_worker_analytics.return_value = WorkerAnalytics(
        active_workers=1, total_workers=1, verified_workers=1, available_workers=1, busy_workers=0, inactive_workers=0, 
        average_rating=5.0, completion_rate=100.0, acceptance_rate=100.0, cancellation_rate=0.0, average_quote=100.0, 
        average_response_time_minutes=1.0, status_distribution=ChartData(labels=[], datasets=[])
    )
    mock.get_customer_analytics.return_value = CustomerAnalytics(
        active_customers=1, repeat_customer_rate=10.0, total_customers=1, new_customers_30d=1, active_customers_30d=1, 
        repeat_customers=1, average_spend=100.0, average_rating_given=5.0
    )
    mock.get_service_analytics.return_value = ServiceAnalytics(
        category_distribution=ChartData(labels=["Plumbing"], datasets=[]),
        most_popular_categories=[{"name": "Plumbing", "count": 10}],
        most_requested_services=[{"name": "AC", "count": 5}],
        least_requested_services=[]
    )
    mock.get_pricing_analytics.return_value = PricingAnalytics(
        average_price=100.0, price_distribution=ChartData(labels=["100"], datasets=[{"label": "test", "data": [1.0]}]), price_variance=10.0,
        average_quote=100.0, minimum_quote=50.0, maximum_quote=150.0, median_quote=100.0
    )
    mock.get_search_analytics.return_value = SearchAnalytics(
        most_searched_services=[{"service_name": "AC", "count": 10}], trending_searches=["AC"], total_searches=1, success_rate=100.0, 
        most_searched_categories=[]
    )
    return mock

from unittest.mock import AsyncMock, MagicMock

async def override_get_db():
    mock_db = MagicMock()
    
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    
    mock_collection = MagicMock()
    mock_collection.find.return_value = mock_cursor
    mock_collection.find_one = AsyncMock(return_value=None)
    
    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = "mock_id"
    mock_collection.insert_one = AsyncMock(return_value=mock_insert_result)
    mock_collection.insert_many = AsyncMock(return_value=mock_insert_result)
    
    mock_db.__getitem__.return_value = mock_collection
    return mock_db

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_orchestrator] = override_get_orchestrator
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_admin_dashboard_overview():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/admin/overview")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "todays_bookings" in data
    assert "todays_revenue" in data

@pytest.mark.asyncio
async def test_admin_business_intelligence():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/admin/business")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "business_growth_summary" in data

@pytest.mark.asyncio
async def test_admin_insights():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/admin/insights")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_admin_anomalies():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/admin/anomalies")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_admin_recommendations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/admin/recommendations")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_admin_executive_summary():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/admin/executive-summary?type=DAILY")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "platform_health" in data
    assert "achievements" in data
