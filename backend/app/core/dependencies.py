"""
Reusable FastAPI dependencies — shared across all feature modules.

Architecture:
    - Database: re-exported from app.database for convenience.
    - Auth placeholders: raise UnauthorizedException until auth is built.
    - Role guards: compose on get_current_user, check user.role.
    - Pagination: query parameter dependency with validation.

Import convention:
    from app.core.dependencies import (
        DatabaseDep,
        CurrentUserDep,
        AdminDep,
        PaginationDep,
    )

    @router.get("/workers")
    async def list_workers(
        user: CurrentUserDep,
        pagination: PaginationDep,
        db: DatabaseDep,
    ):
        ...

Design decisions:
    - Uses Annotated[..., Depends()] (PEP 593) — the modern FastAPI
      pattern. Cleaner than default parameter syntax, reusable as types.
    - Auth placeholders RAISE, not return stubs. Routes that depend on
      auth will fail immediately until auth is implemented, preventing
      silent security holes.
    - CurrentUser is a DI contract schema (not a database model).
      Feature modules type-hint against this minimal interface.
"""

from enum import Enum
from typing import Annotated

from fastapi import Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.database import get_database as _get_database


# ---------------------------------------------------------------------------
# Database Dependency
# ---------------------------------------------------------------------------
# Re-exported from app.database for import convenience.
# Most routes use Beanie Document methods directly and don't need this.
# Use when you need raw MongoDB access (aggregation, admin commands).
#
# Usage:
#     @router.get("/stats")
#     async def stats(db: DatabaseDep):
#         return await db.command("dbStats")

DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(_get_database)]


# ---------------------------------------------------------------------------
# User Role Enum
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    """
    User roles in the marketplace.

    Used by auth guards to restrict route access by role.
    Maps directly to the role field stored in the user document.
    """
    CUSTOMER = "customer"
    WORKER = "worker"
    ADMIN = "admin"


# ---------------------------------------------------------------------------
# Current User Schema (DI Contract)
# ---------------------------------------------------------------------------

class CurrentUser(BaseModel):
    """
    Minimal user identity returned by the auth dependency.

    This is a DI contract — not a database model. It defines the
    interface that feature modules depend on. The auth module will
    populate this from JWT claims + database lookup.

    Fields:
        id: User's MongoDB document ID (string).
        role: One of customer, worker, admin.
        phone: Phone number (primary identifier in blue-collar markets).
        is_active: Whether the account is enabled.
    """
    id: str
    role: UserRole
    phone: str
    is_active: bool = True


# ---------------------------------------------------------------------------
# Auth Placeholders
# ---------------------------------------------------------------------------
# These raise UnauthorizedException until the auth module is built.
# When auth is implemented:
#   1. Create app/auth/dependencies.py with real JWT decode logic.
#   2. Update get_current_user() below to call the real auth dependency.
#   3. Role guards (get_current_admin, etc.) work unchanged.

async def get_current_user() -> CurrentUser:
    """
    Extract and validate the current user from the request.

    PLACEHOLDER — raises until auth module is implemented.

    When implemented, this will:
        1. Extract JWT from Authorization header.
        2. Decode and validate the token.
        3. Fetch user from database.
        4. Set user_id_var in context for logging.
        5. Return CurrentUser.
    """
    raise UnauthorizedException(
        message="Authentication not implemented yet",
        error_code="AUTH_NOT_IMPLEMENTED",
    )


async def get_current_active_user(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    Verify the current user's account is active.

    Layer on top of get_current_user — rejects disabled accounts.
    Use this instead of get_current_user in routes that require
    an active account (most routes).
    """
    if not user.is_active:
        raise ForbiddenException(
            message="Account is deactivated",
            error_code="ACCOUNT_DEACTIVATED",
        )
    return user


# ---------------------------------------------------------------------------
# Role-Based Guards
# ---------------------------------------------------------------------------
# Each guard depends on get_current_active_user and checks the role.
# Usage:
#     @router.get("/admin/dashboard")
#     async def dashboard(admin: AdminDep):
#         ...  # Only admins reach here

async def get_current_admin(
    user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    """
    Require the current user to have the admin role.

    Raises ForbiddenException if the user is authenticated but not an admin.
    """
    if user.role != UserRole.ADMIN:
        raise ForbiddenException(
            message="Admin access required",
            error_code="ADMIN_REQUIRED",
        )
    return user


async def get_current_worker(
    user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    """
    Require the current user to have the worker role.

    Raises ForbiddenException if the user is not a registered worker.
    """
    if user.role != UserRole.WORKER:
        raise ForbiddenException(
            message="Worker access required",
            error_code="WORKER_REQUIRED",
        )
    return user


async def get_current_customer(
    user: CurrentUser = Depends(get_current_active_user),
) -> CurrentUser:
    """
    Require the current user to have the customer role.

    Raises ForbiddenException if the user is not a registered customer.
    """
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenException(
            message="Customer access required",
            error_code="CUSTOMER_REQUIRED",
        )
    return user


# ---------------------------------------------------------------------------
# Annotated Type Aliases (for router type hints)
# ---------------------------------------------------------------------------
# These are the public API of this module. Feature routers import these
# types and use them as parameter annotations — no Depends() boilerplate.

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_active_user)]
AdminDep = Annotated[CurrentUser, Depends(get_current_admin)]
WorkerDep = Annotated[CurrentUser, Depends(get_current_worker)]
CustomerDep = Annotated[CurrentUser, Depends(get_current_customer)]


# ---------------------------------------------------------------------------
# Pagination Dependency
# ---------------------------------------------------------------------------

class PaginationParams:
    """
    Query parameter dependency for paginated list endpoints.

    Validates and clamps page/page_size to safe ranges.
    Pre-computes 'skip' so repositories don't repeat the arithmetic.

    Usage:
        @router.get("/workers")
        async def list_workers(pagination: PaginationDep):
            workers = await Worker.find_all()
                .skip(pagination.skip)
                .limit(pagination.page_size)
                .to_list()

    Query parameters:
        ?page=1&page_size=20  (defaults)
        ?page=3&page_size=50  (custom)
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(
            default=20, ge=1, le=100, description="Items per page (max 100)"
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size

    def __repr__(self) -> str:
        return f"PaginationParams(page={self.page}, page_size={self.page_size}, skip={self.skip})"


PaginationDep = Annotated[PaginationParams, Depends()]


# ---------------------------------------------------------------------------
# Sorting Dependency
# ---------------------------------------------------------------------------

class SortParams:
    """
    Query parameter dependency for sorted list endpoints.

    Provides sort_by (field name) and sort_order (asc/desc).
    Repositories use these to build MongoDB sort queries.

    Usage:
        @router.get("/workers")
        async def list_workers(sort: SortDep):
            direction = 1 if sort.sort_order == "asc" else -1
            workers = await Worker.find_all()
                .sort((sort.sort_by, direction))
                .to_list()
    """

    def __init__(
        self,
        sort_by: str = Query(
            default="created_at",
            description="Field name to sort by",
        ),
        sort_order: str = Query(
            default="desc",
            pattern="^(asc|desc)$",
            description="Sort direction: asc or desc",
        ),
    ) -> None:
        self.sort_by = sort_by
        self.sort_order = sort_order

    def __repr__(self) -> str:
        return f"SortParams(sort_by={self.sort_by}, sort_order={self.sort_order})"


SortDep = Annotated[SortParams, Depends()]
