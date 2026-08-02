"""
Home Service — Concurrent aggregation layer for Customer Home Screen APIs.
"""

import asyncio
import logging
from app.category.repository import CategoryRepository
from app.category.schemas import CategoryResponse
from app.service.repository import ServiceRepository
from app.service.schemas import ServiceResponse
from app.home.schemas import HomeResponse

logger = logging.getLogger(__name__)


class HomeService:
    """Service aggregating data for the Customer App Home Screen."""

    @classmethod
    async def get_home_data(cls) -> HomeResponse:
        """
        Fetch all home screen sections in parallel using asyncio.gather.
        Guarantees zero N+1 database calls and minimal API latency.
        """
        # Execute parallel queries
        categories_task = CategoryRepository.get_featured_categories(limit=8)
        featured_services_task = ServiceRepository.list_services(is_featured=True, limit=10)
        popular_services_task = ServiceRepository.get_popular_services(limit=10)
        recent_services_task = ServiceRepository.get_recent_services(limit=10)

        raw_categories, raw_featured, raw_popular, raw_recent = await asyncio.gather(
            categories_task,
            featured_services_task,
            popular_services_task,
            recent_services_task,
        )

        featured_categories = [CategoryResponse.model_validate(cat) for cat in (raw_categories or [])]
        featured_services = [ServiceResponse.model_validate(srv) for srv in (raw_featured or [])]
        popular_services = [ServiceResponse.model_validate(srv) for srv in (raw_popular or [])]
        recent_services = [ServiceResponse.model_validate(srv) for srv in (raw_recent or [])]

        # Recommended services placeholder: defaults to featured_services for Phase 4.2.4
        recommended_services = list(featured_services)

        logger.info(
            "Aggregated home payload: categories=%d, featured=%d, popular=%d, recent=%d",
            len(featured_categories),
            len(featured_services),
            len(popular_services),
            len(recent_services),
        )

        return HomeResponse(
            featured_categories=featured_categories,
            featured_services=featured_services,
            popular_services=popular_services,
            recommended_services=recommended_services,
            recent_services=recent_services,
        )
