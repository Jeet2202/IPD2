"""
Standard API response schemas — the success side of ErrorResponse.

ErrorResponse (in exceptions.py) handles all errors.
This module handles all successes:

    SuccessResponse  — single item or action confirmation
    PaginatedResponse — list endpoints with pagination metadata
    MessageResponse  — simple message (delete confirmations, etc.)

Every success response has `success: true` so frontend clients
can check one field regardless of the endpoint.

Usage:
    from app.utils.responses import SuccessResponse, PaginatedResponse

    @router.get("/workers/{worker_id}")
    async def get_worker(worker_id: str) -> SuccessResponse:
        worker = await worker_service.get_by_id(worker_id)
        return SuccessResponse(data=worker)

    @router.get("/workers")
    async def list_workers(pagination: PaginationDep) -> PaginatedResponse:
        workers, total = await worker_service.list(pagination)
        return PaginatedResponse.build(
            data=workers,
            page=pagination.page,
            page_size=pagination.page_size,
            total_items=total,
        )
"""

from math import ceil
from typing import Any

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Standard success response wrapping a single result.

    Used for:
        - GET single resource (GET /workers/{id})
        - POST create (POST /jobs)
        - PUT/PATCH update (PUT /workers/me)
    """
    success: bool = True
    data: Any = Field(
        ...,
        description="Response payload — the requested resource or result",
    )
    message: str = Field(
        default="Operation successful",
        description="Human-readable success message",
    )


class MessageResponse(BaseModel):
    """
    Simple message response — no data payload.

    Used for:
        - DELETE confirmations
        - Action acknowledgements (mark as read, logout, etc.)
        - Status changes that don't return updated data
    """
    success: bool = True
    message: str = Field(
        ...,
        description="Human-readable confirmation message",
        examples=["Resource deleted successfully"],
    )


class PaginationMeta(BaseModel):
    """
    Pagination metadata included in paginated responses.

    Frontend uses these fields to render pagination controls
    (page numbers, next/previous buttons, "showing X of Y").
    """
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total items across all pages")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_previous: bool = Field(..., description="Whether a previous page exists")


class PaginatedResponse(BaseModel):
    """
    Standard paginated list response.

    Used for all list endpoints that support pagination:
        GET /api/v1/workers?page=2&page_size=20
        GET /api/v1/jobs?page=1&page_size=50

    Use the build() class method to construct this from query results.
    """
    success: bool = True
    data: list[Any] = Field(
        ...,
        description="List of items for the current page",
    )
    pagination: PaginationMeta

    @classmethod
    def build(
        cls,
        data: list[Any],
        page: int,
        page_size: int,
        total_items: int,
    ) -> "PaginatedResponse":
        """
        Construct a PaginatedResponse from query results.

        Calculates total_pages, has_next, and has_previous automatically.

        Args:
            data: List of items for the current page.
            page: Current page number (1-indexed).
            page_size: Items per page.
            total_items: Total count across all pages.

        Returns:
            Complete PaginatedResponse ready for return.
        """
        total_pages = ceil(total_items / page_size) if page_size > 0 else 0

        return cls(
            data=data,
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
            ),
        )
