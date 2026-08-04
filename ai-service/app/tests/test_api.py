import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_root(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Ally AI Service"

@pytest.mark.asyncio
async def test_ready(async_client):
    response = await async_client.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True

@pytest.mark.asyncio
async def test_metrics(async_client):
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "memory_usage_mb" in data
    assert "cpu_percent" in data

@pytest.mark.asyncio
async def test_config_masks_secrets(async_client):
    response = await async_client.get("/config")
    assert response.status_code == 200
    data = response.json()
    # MONGO_URI must ALWAYS be masked — even when empty
    assert data["MONGO_URI"] == "***"
    # GROQ_API_KEY must ALWAYS be masked
    assert data["GROQ_API_KEY"] == "***"

@pytest.mark.asyncio
async def test_middleware_request_id(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers

@pytest.mark.asyncio
async def test_health_degraded_returns_503(async_client):
    """Verify /health returns HTTP 503 when DB is unreachable, not a misleading 200."""
    with patch("app.api.infrastructure.get_db") as mock_get_db:
        # Override the dependency to raise on ping
        async def failing_db_dep():
            db = AsyncMock()
            db.command.side_effect = Exception("Connection refused")
            yield db
        mock_get_db.return_value = failing_db_dep()
        # We can't easily inject the dep in the running ASGI app without overriding,
        # so we test the logic directly via the router function
        from app.api.infrastructure import health_check
        from unittest.mock import AsyncMock as AM
        db_mock = AM()
        db_mock.command.side_effect = Exception("Connection refused")
        result = await health_check(db=db_mock)
        assert result.status_code == 503
        import json
        body = json.loads(result.body)
        assert body["status"] == "degraded"
