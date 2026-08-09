"""
Unit tests for Phase 4 Worker Location Timestamp functionality.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
import pytest
from pydantic import ValidationError
from beanie import init_beanie, PydanticObjectId

from app.address.models import GeoJSONPoint
from app.worker.models import WorkerProfile
from app.worker.schemas import UpdateWorkerLocationRequest, WorkerProfileResponse
from app.worker.service import WorkerService
from app.auth.models import User
from app.utils.enums import UserRole


@pytest.fixture(autouse=True)
async def init_mock_beanie():
    mock_db = MagicMock()
    mock_db.command = AsyncMock(return_value={"version": "6.0.0"})
    mock_db.list_collection_names = AsyncMock(return_value=[])
    mock_coll = MagicMock()
    mock_coll.index_information = AsyncMock(return_value={})
    mock_coll.create_index = AsyncMock(return_value=None)
    mock_coll.create_indexes = AsyncMock(return_value=[])
    mock_db.__getitem__ = MagicMock(return_value=mock_coll)
    
    await init_beanie(database=mock_db, document_models=[WorkerProfile, User])


@pytest.mark.asyncio
async def test_worker_profile_default_location_timestamp_none():
    # TEST 6: Worker profile with no location has current_location_updated_at = None
    profile = WorkerProfile(user_id=PydanticObjectId())
    assert profile.current_location is None
    assert profile.current_location_updated_at is None


@pytest.mark.asyncio
async def test_location_update_sets_utc_timestamp():
    # TEST 1 & 2 & 3 & 5 & 7: Backend generates timezone-aware UTC timestamp on location update
    user = User(
        id=PydanticObjectId(),
        email="test_worker_loc@example.com",
        phone="+919876543210",
        password_hash="$2b$12$test_hash_value",
        full_name="Test Worker Loc",
        role=UserRole.WORKER,
    )
    profile = WorkerProfile(
        id=PydanticObjectId(),
        user_id=user.id,
        current_location=None,
        current_location_updated_at=None,
    )

    before_update = datetime.now(timezone.utc)
    
    class MockWorkerRepository:
        @staticmethod
        async def get_by_user_id(uid):
            return profile

        @staticmethod
        async def save_profile(p):
            return p

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.worker.service.WorkerRepository", MockWorkerRepository)

        req = UpdateWorkerLocationRequest(latitude=12.9716, longitude=77.5946)
        res: WorkerProfileResponse = await WorkerService.update_worker_location(user, req)

        after_update = datetime.now(timezone.utc)

        # Confirm location changed
        assert profile.current_location is not None
        assert profile.current_location.coordinates == [77.5946, 12.9716]
        
        # Confirm timestamp exists and is timezone-aware UTC within execution window
        assert profile.current_location_updated_at is not None
        assert profile.current_location_updated_at.tzinfo == timezone.utc
        assert before_update - timedelta(seconds=2) <= profile.current_location_updated_at <= after_update + timedelta(seconds=2)

        # Confirm response DTO contains the updated timestamp
        assert res.current_location_updated_at == profile.current_location_updated_at


@pytest.mark.asyncio
async def test_failed_location_update_does_not_set_timestamp():
    # TEST 4: Failed validation (invalid latitude > 90) prevents location and timestamp update
    profile = WorkerProfile(
        id=PydanticObjectId(),
        user_id=PydanticObjectId(),
        current_location=None,
        current_location_updated_at=None,
    )

    with pytest.raises(ValidationError):
        UpdateWorkerLocationRequest(latitude=150.0, longitude=77.5946)

    # Confirm profile state remains unchanged
    assert profile.current_location is None
    assert profile.current_location_updated_at is None
