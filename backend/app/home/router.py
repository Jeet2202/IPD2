"""
Home Router — Endpoints for Customer Home Screen aggregation.
"""

import logging
from fastapi import APIRouter, status
from app.home.schemas import HomeResponse
from app.home.service import HomeService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/home",
    response_model=HomeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated Customer Home Screen data",
    description="Public endpoint returning featured categories, featured services, popular services, recent services, and recommended services in a single optimized payload.",
)
async def get_home_data() -> HomeResponse:
    """Retrieve home screen data."""
    return await HomeService.get_home_data()
