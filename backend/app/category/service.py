"""
Category Service — Business logic for category management, slug generation, sorting, and soft deletion.
"""

import logging
from app.category.models import ServiceCategory, generate_slug
from app.category.repository import CategoryRepository
from app.category.schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
    ReorderCategoriesRequest,
)
from app.core.dependencies import CurrentUser
from app.core.exceptions import BadRequestException, NotFoundException
from app.service.repository import ServiceRepository
from app.service.schemas import ServiceListResponse, ServiceResponse
from app.auth.models import User
from app.utils.enums import UserRole

logger = logging.getLogger(__name__)


class CategoryService:
    """Service layer managing category business logic."""

    @classmethod
    async def generate_unique_slug(cls, base_name_or_slug: str, exclude_id: str | None = None) -> str:
        """
        Generate a unique URL slug from a category name or base slug.
        If slug exists, appends incremental suffix (-2, -3, ...).
        """
        base_slug = generate_slug(base_name_or_slug)
        if not base_slug:
            base_slug = "category"

        candidate_slug = base_slug
        counter = 2

        while await CategoryRepository.category_exists(slug=candidate_slug, exclude_id=exclude_id):
            candidate_slug = f"{base_slug}-{counter}"
            counter += 1

        return candidate_slug

    @classmethod
    async def create_category(cls, payload: CategoryCreateRequest) -> CategoryResponse:
        """Create a new service category."""
        # 1. Check for duplicate name
        existing_by_name = await CategoryRepository.get_category_by_name(payload.name)
        if existing_by_name:
            raise BadRequestException(
                message=f"Category with name '{payload.name}' already exists.",
                error_code="DUPLICATE_CATEGORY_NAME",
            )

        # 2. Resolve unique slug
        data = payload.model_dump()
        raw_slug = data.get("slug")
        target_base = raw_slug if (raw_slug and raw_slug.strip()) else payload.name
        data["slug"] = await cls.generate_unique_slug(target_base)

        # 3. Create document
        category = await CategoryRepository.create_category(data)
        logger.info("Created new category: name='%s', slug='%s', id='%s'", category.name, category.slug, category.id)
        return CategoryResponse.model_validate(category)

    @classmethod
    async def get_category_by_id(cls, category_id: str, include_inactive: bool = False) -> CategoryResponse:
        """Retrieve category by ID."""
        category = await CategoryRepository.get_category_by_id(category_id)
        if not category:
            raise NotFoundException(
                message=f"Category with ID '{category_id}' not found.",
                error_code="CATEGORY_NOT_FOUND",
            )
        if not category.is_active and not include_inactive:
            raise NotFoundException(
                message=f"Category with ID '{category_id}' is inactive.",
                error_code="CATEGORY_NOT_FOUND",
            )
        return CategoryResponse.model_validate(category)

    @classmethod
    async def get_category_services(
        cls,
        category_id: str,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "display_order",
        current_user: User | None = None,
    ) -> ServiceListResponse:
        """Fetch paginated services for a given category ID."""
        # 1. Verify category exists
        await cls.get_category_by_id(category_id)

        # 2. Check admin include_inactive status
        include_inactive = False
        if current_user and getattr(current_user, "role", None) == UserRole.ADMIN:
            include_inactive = True

        # 3. Fetch paginated services
        items, total = await ServiceRepository.list_services_by_category_paginated(
            category_id=category_id,
            page=page,
            limit=limit,
            sort_by=sort_by,
            include_inactive=include_inactive,
        )

        pages = (total + limit - 1) // limit if total > 0 else 1
        service_responses = [ServiceResponse.model_validate(s) for s in items]

        return ServiceListResponse(
            items=service_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    @classmethod
    async def get_category_by_slug(cls, slug: str, include_inactive: bool = False) -> CategoryResponse:
        """Retrieve category by slug."""
        category = await CategoryRepository.get_category_by_slug(slug)
        if not category:
            raise NotFoundException(
                message=f"Category with slug '{slug}' not found.",
                error_code="CATEGORY_NOT_FOUND",
            )
        if not category.is_active and not include_inactive:
            raise NotFoundException(
                message=f"Category with slug '{slug}' is inactive.",
                error_code="CATEGORY_NOT_FOUND",
            )
        return CategoryResponse.model_validate(category)

    @classmethod
    async def list_categories(
        cls,
        include_inactive: bool = False,
        current_user: CurrentUser | None = None,
    ) -> CategoryListResponse:
        """
        List categories ordered by display_order.
        Only admins can pass include_inactive=True.
        """
        allow_inactive = include_inactive and (current_user is not None and current_user.role == UserRole.ADMIN)
        categories = await CategoryRepository.list_categories(include_inactive=allow_inactive)
        items = [CategoryResponse.model_validate(cat) for cat in categories]
        return CategoryListResponse(items=items, total=len(items))

    @classmethod
    async def update_category(cls, category_id: str, payload: CategoryUpdateRequest) -> CategoryResponse:
        """Update an existing category."""
        category = await CategoryRepository.get_category_by_id(category_id)
        if not category:
            raise NotFoundException(
                message=f"Category with ID '{category_id}' not found.",
                error_code="CATEGORY_NOT_FOUND",
            )

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

        # Handle name change & slug update
        if "name" in update_data and update_data["name"] != category.name:
            new_name = update_data["name"]
            if await CategoryRepository.category_exists(name=new_name, exclude_id=str(category.id)):
                raise BadRequestException(
                    message=f"Category with name '{new_name}' already exists.",
                    error_code="DUPLICATE_CATEGORY_NAME",
                )
            if "slug" not in update_data:
                update_data["slug"] = await cls.generate_unique_slug(new_name, exclude_id=str(category.id))

        if "slug" in update_data:
            new_slug = update_data["slug"]
            if await CategoryRepository.category_exists(slug=new_slug, exclude_id=str(category.id)):
                update_data["slug"] = await cls.generate_unique_slug(new_slug, exclude_id=str(category.id))

        updated_category = await CategoryRepository.update_category(category, update_data)
        logger.info("Updated category id='%s': fields=%s", category_id, list(update_data.keys()))
        return CategoryResponse.model_validate(updated_category)

    @classmethod
    async def delete_category(cls, category_id: str) -> CategoryResponse:
        """Soft delete category by setting is_active = False."""
        category = await CategoryRepository.get_category_by_id(category_id)
        if not category:
            raise NotFoundException(
                message=f"Category with ID '{category_id}' not found.",
                error_code="CATEGORY_NOT_FOUND",
            )

        soft_deleted = await CategoryRepository.soft_delete_category(category)
        logger.info("Soft-deleted category id='%s' (is_active=False)", category_id)
        return CategoryResponse.model_validate(soft_deleted)

    @classmethod
    async def reorder_categories(cls, payload: ReorderCategoriesRequest) -> CategoryListResponse:
        """Bulk update display orders."""
        items_dict = [item.model_dump() for item in payload.items]
        await CategoryRepository.reorder_categories(items_dict)
        return await cls.list_categories(include_inactive=True, current_user=CurrentUser(id="admin", role=UserRole.ADMIN, phone="+910000000000"))
