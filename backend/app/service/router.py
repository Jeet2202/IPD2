"""
Service API Router — Endpoints for service management, discovery, and search.
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.service.schemas import (
    CreateServiceRequest,
    ServiceListResponse,
    ServiceResponse,
    UpdateServiceRequest,
)
from app.service.service import ServiceManagementService
from app.core.dependencies import AdminDep, OptionalUserDep

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/services",
    response_model=ServiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all services",
    description="Retrieve paginated services with optional category filtering, featured status, search query, and sorting. Admins can pass include_inactive=true.",
)
async def list_services(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    category_id: str | None = Query(default=None, description="Filter by category ObjectId string or slug"),
    is_featured: bool | None = Query(default=None, description="Filter featured services"),
    min_price: float | None = Query(default=None, ge=0, description="Minimum price filter"),
    max_price: float | None = Query(default=None, ge=0, description="Maximum price filter"),
    max_duration: int | None = Query(default=None, ge=0, description="Maximum estimated duration in minutes"),
    search: str | None = Query(default=None, description="Search query string (title, tags, keywords)"),
    sort_by: str = Query(default="display_order", description="Sort field (display_order, -created_at, price_asc, price_desc, title_asc, title_desc)"),
    include_inactive: bool = Query(default=False, description="Include soft-deleted services (Admin only)"),
    user: OptionalUserDep = None,
) -> ServiceListResponse:
    """List services."""
    return await ServiceManagementService.list_services(
        page=page,
        limit=limit,
        category_id=category_id,
        is_featured=is_featured,
        min_price=min_price,
        max_price=max_price,
        max_duration=max_duration,
        search=search,
        sort_by=sort_by,
        include_inactive=include_inactive,
        current_user=user,
    )


@router.get(
    "/services/search",
    response_model=ServiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="Global search services",
    description="Search active services by title, category, tags, keywords, short description, and description with relevance ranking and filtering.",
)
async def search_services(
    query: str | None = Query(default=None, description="Search query string"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(default=None, description="Filter by category ID or slug"),
    featured: bool | None = Query(default=None, description="Filter by featured status"),
    min_price: float | None = Query(default=None, ge=0, description="Minimum price filter"),
    max_price: float | None = Query(default=None, ge=0, description="Maximum price filter"),
    max_duration: int | None = Query(default=None, ge=0, description="Maximum estimated duration in minutes"),
    sort_by: str = Query(default="relevance", description="Sort field (relevance, display_order, -created_at, price_asc, price_desc, title_asc, title_desc)"),
) -> ServiceListResponse:
    """Global search services."""
    return await ServiceManagementService.search_services(
        query=query,
        page=page,
        page_size=page_size,
        category=category,
        featured=featured,
        min_price=min_price,
        max_price=max_price,
        max_duration=max_duration,
        sort_by=sort_by,
    )


@router.get(
    "/services/slug/{slug}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service by slug",
    description="Retrieve a single service by its URL slug.",
)
async def get_service_by_slug(
    slug: str,
) -> ServiceResponse:
    """Get service by slug."""
    return await ServiceManagementService.get_service_by_slug(slug)


@router.get(
    "/services/{id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service by ID",
    description="Retrieve a single service by its MongoDB ObjectId string.",
)
async def get_service_by_id(
    id: str,
) -> ServiceResponse:
    """Get service by ID."""
    return await ServiceManagementService.get_service_by_id(id)


@router.get(
    "/categories/{category_id}/services",
    response_model=ServiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List services by category ID",
    description="Retrieve paginated active services belonging to a specific category.",
)
async def list_services_by_category(
    category_id: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="display_order", description="Sort field (display_order, -created_at, price_asc, price_desc)"),
    user: OptionalUserDep = None,
) -> ServiceListResponse:
    """List services by category with pagination."""
    from app.category.service import CategoryService
    return await CategoryService.get_category_services(
        category_id=category_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        current_user=user,
    )


@router.post(
    "/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create service (Admin only)",
    description="Create a new service linked to a parent category.",
)
async def create_service(
    payload: CreateServiceRequest,
    admin: AdminDep,
) -> ServiceResponse:
    """Create service."""
    return await ServiceManagementService.create_service(payload)


@router.put(
    "/services/{id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update service (Admin only)",
    description="Update an existing service.",
)
async def update_service(
    id: str,
    payload: UpdateServiceRequest,
    admin: AdminDep,
) -> ServiceResponse:
    """Update service."""
    return await ServiceManagementService.update_service(id, payload)


@router.delete(
    "/services/{id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete service (Admin only - Soft Delete)",
    description="Soft delete a service by setting is_active = false.",
)
async def delete_service(
    id: str,
    admin: AdminDep,
) -> ServiceResponse:
    """Soft delete service."""
    return await ServiceManagementService.delete_service(id)


@router.post(
    "/services/{service_id}/image",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload or replace service image (Admin only)",
    description="Upload or replace a service image on Cloudinary under kaamsetu/service_images.",
)
async def upload_service_image(
    service_id: str,
    admin: AdminDep,
    file: UploadFile = File(...),
) -> ServiceResponse:
    """Upload or replace service image."""
    file_bytes = await file.read()
    filename = file.filename or "service.jpg"
    return await ServiceManagementService.upload_service_image(
        service_id=service_id,
        file_bytes=file_bytes,
        filename=filename,
        content_type=file.content_type,
    )


@router.delete(
    "/services/{service_id}/image",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete service image (Admin only)",
    description="Delete service image from Cloudinary and clear image fields in database.",
)
async def delete_service_image(
    service_id: str,
    admin: AdminDep,
) -> ServiceResponse:
    """Delete service image."""
    return await ServiceManagementService.delete_service_image(service_id)

