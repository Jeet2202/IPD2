"""
Category API Router — Endpoints for service categories management and discovery.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from app.category.schemas import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
    ReorderCategoriesRequest,
)
from app.service.schemas import ServiceListResponse
from app.category.service import CategoryService
from app.core.dependencies import AdminDep, OptionalUserDep

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all service categories",
    description="Retrieve all active service categories ordered by display_order. Admins can pass include_inactive=true to view soft-deleted categories.",
)
async def list_categories(
    include_inactive: bool = Query(default=False, description="Include soft-deleted categories (Admin only)"),
    user: OptionalUserDep = None,
) -> CategoryListResponse:
    """List service categories."""
    return await CategoryService.list_categories(include_inactive=include_inactive, current_user=user)


@router.get(
    "/slug/{slug}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by slug",
    description="Retrieve a single category by its URL slug.",
)
async def get_category_by_slug(
    slug: str,
) -> CategoryResponse:
    """Get category by slug."""
    return await CategoryService.get_category_by_slug(slug)


@router.get(
    "/{id}/services",
    response_model=ServiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List services by category ID",
    description="Retrieve paginated active services belonging to a specific category.",
)
async def get_category_services(
    id: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="display_order", description="Sort field (display_order, -created_at, price_asc, price_desc, title_asc, title_desc)"),
    is_featured: bool | None = Query(default=None, description="Filter featured services"),
    min_price: float | None = Query(default=None, ge=0, description="Minimum price filter"),
    max_price: float | None = Query(default=None, ge=0, description="Maximum price filter"),
    max_duration: int | None = Query(default=None, ge=0, description="Maximum estimated duration in minutes"),
    user: OptionalUserDep = None,
) -> ServiceListResponse:
    """Get services by category ID with pagination."""
    return await CategoryService.get_category_services(
        category_id=id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        is_featured=is_featured,
        min_price=min_price,
        max_price=max_price,
        max_duration=max_duration,
        current_user=user,
    )


@router.get(
    "/{id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
    description="Retrieve a single category by its MongoDB ObjectId string.",
)
async def get_category_by_id(
    id: str,
) -> CategoryResponse:
    """Get category by ID."""
    return await CategoryService.get_category_by_id(id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category (Admin only)",
    description="Create a new service category with auto-generated unique slug.",
)
async def create_category(
    payload: CategoryCreateRequest,
    admin: AdminDep,
) -> CategoryResponse:
    """Create new service category."""
    return await CategoryService.create_category(payload)


@router.put(
    "/{id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category (Admin only)",
    description="Update an existing service category.",
)
async def update_category(
    id: str,
    payload: CategoryUpdateRequest,
    admin: AdminDep,
) -> CategoryResponse:
    """Update service category."""
    return await CategoryService.update_category(id, payload)


@router.delete(
    "/{id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete category (Admin only - Soft Delete)",
    description="Soft delete a service category by setting is_active = false.",
)
async def delete_category(
    id: str,
    admin: AdminDep,
) -> CategoryResponse:
    """Soft delete service category."""
    return await CategoryService.delete_category(id)


@router.patch(
    "/reorder",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Reorder categories (Admin only)",
    description="Bulk update category display orders.",
)
async def reorder_categories(
    payload: ReorderCategoriesRequest,
    admin: AdminDep,
) -> CategoryListResponse:
    """Reorder service categories."""
    return await CategoryService.reorder_categories(payload)
