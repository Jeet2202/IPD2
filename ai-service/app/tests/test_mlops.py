import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.schemas.mlops import (
    ModelMetadata, DatasetMetadata, ExperimentMetadata,
    AIHealthStatus, ModelMetrics, AuditLogEntry, SystemConfiguration
)
from app.api.mlops import get_db

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
    
    mock_update_result = MagicMock()
    mock_update_result.modified_count = 1
    mock_update_result.upserted_id = None
    mock_collection.update_one = AsyncMock(return_value=mock_update_result)
    
    mock_db.__getitem__.return_value = mock_collection
    return mock_db

@pytest.fixture(autouse=True)
def apply_overrides():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides = {}

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

@pytest.mark.asyncio
async def test_register_model(client: AsyncClient):
    req = {
        "name": "Test Model",
        "description": "Test description",
        "version": "1.0.0",
        "supported_tasks": ["search"],
        "tags": ["test"],
        "owner": "test-team"
    }
    response = await client.post("/ml/models/register", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Model"
    assert data["version"] == "1.0.0"
    assert "test-model-v1-0-0" in data["id"]

@pytest.mark.asyncio
async def test_get_models(client: AsyncClient):
    response = await client.get("/ml/models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_register_dataset(client: AsyncClient):
    req = {
        "name": "Test Dataset",
        "version": "v1",
        "description": "Test DS",
        "source": "s3://test/data.csv",
        "schema_definition": {"col1": "int"},
        "statistics": {"rows": 100},
        "feature_list": ["f1"],
        "supported_models": ["m1"]
    }
    response = await client.post("/ml/datasets/register", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dataset"
    assert data["id"].startswith("ds-")

@pytest.mark.asyncio
async def test_log_experiment(client: AsyncClient):
    req = {
        "name": "Test Exp",
        "model_id": "m1",
        "dataset_id": "d1",
        "parameters": {"lr": 0.01},
        "metrics": {"accuracy": 0.95},
        "results": {"status": "success"},
        "status": "COMPLETED",
        "execution_time_seconds": 120.5,
        "owner": "test-user"
    }
    response = await client.post("/ml/experiments", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Exp"
    assert data["id"].startswith("exp-")

@pytest.mark.asyncio
async def test_get_health(client: AsyncClient):
    response = await client.get("/ml/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "overall_score" in data

@pytest.mark.asyncio
async def test_get_metrics(client: AsyncClient):
    response = await client.get("/ml/metrics?model_id=m1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_config(client: AsyncClient):
    response = await client.get("/ml/configuration")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "global"

@pytest.mark.asyncio
async def test_get_audit_logs(client: AsyncClient):
    response = await client.get("/ml/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
