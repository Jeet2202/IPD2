"""
Unit tests for Phase 3 Canonical Skill Vocabulary & Validation.
"""

import pytest
from unittest.mock import patch, AsyncMock
from app.core.config import settings
from app.worker.service import WorkerService
from app.booking.models import ServiceSnapshot
from app.booking.schemas import ServiceSnapshotResponse
from app.core.exceptions import BadRequestException


@pytest.mark.asyncio
async def test_1_canonical_exact_match():
    # TEST 1: Input ["electrical"] -> accepted
    res = await WorkerService.validate_and_normalize_skills(["electrical"])
    assert res == ["electrical"]


@pytest.mark.asyncio
async def test_2_uppercase_normalization():
    # TEST 2: Input ["Electrical"] -> normalized to ["electrical"]
    res = await WorkerService.validate_and_normalize_skills(["Electrical"])
    assert res == ["electrical"]


@pytest.mark.asyncio
async def test_3_whitespace_normalization():
    # TEST 3: Input [" electrical "] -> normalized to ["electrical"]
    res = await WorkerService.validate_and_normalize_skills([" electrical "])
    assert res == ["electrical"]


@pytest.mark.asyncio
async def test_4_duplicate_normalization():
    # TEST 4: Input ["electrical", "electrical"] -> normalized to ["electrical"]
    res = await WorkerService.validate_and_normalize_skills(["electrical", "electrical"])
    assert res == ["electrical"]


@pytest.mark.asyncio
async def test_5_multi_duplicate_normalization():
    # TEST 5: Input ["electrical", "plumbing", "electrical"] -> ["electrical", "plumbing"]
    res = await WorkerService.validate_and_normalize_skills(["electrical", "plumbing", "electrical"])
    assert res == ["electrical", "plumbing"]


@pytest.mark.asyncio
async def test_6_and_8_and_9_strict_validation_feature_flag():
    # TEST 6 & 8 & 9: Strict validation when SKILL_VALIDATION_ENABLED is True vs False
    mock_active_slugs = ["electrical", "plumbing", "cleaning"]
    
    with patch("app.category.repository.CategoryRepository.get_active_category_slugs", new_callable=AsyncMock) as mock_get_slugs:
        mock_get_slugs.return_value = mock_active_slugs

        # When SKILL_VALIDATION_ENABLED is True
        try:
            settings.SKILL_VALIDATION_ENABLED = True

            # TEST 9: Active category accepted
            accepted = await WorkerService.validate_and_normalize_skills(["Electrical", " plumbing "])
            assert accepted == ["electrical", "plumbing"]

            # TEST 6 & 8: Random skill / inactive category slug "old-category" rejected
            with pytest.raises(BadRequestException, match="Invalid skill domain"):
                await WorkerService.validate_and_normalize_skills(["electrical", "old-category"])

            with pytest.raises(BadRequestException, match="Invalid skill domain"):
                await WorkerService.validate_and_normalize_skills(["random_skill"])

        finally:
            # Revert feature flag setting to default False for rollout
            settings.SKILL_VALIDATION_ENABLED = False

        # Grace period mode (SKILL_VALIDATION_ENABLED = False): Allows with warning
        grace_res = await WorkerService.validate_and_normalize_skills(["electrical", "random_skill"])
        assert grace_res == ["electrical", "random_skill"]


@pytest.mark.asyncio
async def test_7_empty_skill_list():
    # TEST 7: Input [] -> accepted
    res = await WorkerService.validate_and_normalize_skills([])
    assert res == []


@pytest.mark.asyncio
async def test_10_valid_skills_endpoint_response_structure():
    # TEST 10: GET /worker/valid-skills return structure
    mock_slugs = ["ac-repair", "carpentry", "cleaning", "electrical", "painting", "plumbing"]
    with patch("app.category.repository.CategoryRepository.get_active_category_slugs", new_callable=AsyncMock) as mock_get_slugs:
        mock_get_slugs.return_value = mock_slugs

        response = await WorkerService.get_valid_skills()
        assert "skills" in response
        assert response["skills"] == mock_slugs
