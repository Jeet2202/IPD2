"""
Reusable FastAPI dependencies — shared across all feature modules.

Architecture:
    - Database: re-exported from app.database for convenience.
    - Auth: extracts and validates JWT tokens from Authorization header.
      Uses OAuth2PasswordBearer for Swagger integration.
    - Role guards: compose on get_current_active_user, check user.role.
    - Optional auth: returns None for unauthenticated requests.
    - Pagination: query parameter dependency with validation.

Import convention:
    from app.core.dependencies import (
        DatabaseDep,
        CurrentUserDep,
        AdminDep,
        OptionalUserDep,
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
    - OAuth2PasswordBearer is pre-wired so Swagger UI shows the
      Authorize button and lock icons on protected endpoints.
    - Auth placeholder RAISES, not returns stubs. Routes that depend on
      auth will fail immediately until auth is implemented, preventing
      silent security holes.
    - CurrentUser is a DI contract schema (not a database model).
      Feature modules type-hint against this minimal interface.
    - OptionalUserDep returns None for unauthenticated requests,
      enabling endpoints that work for both anonymous and logged-in users.
"""

from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.database import get_database as _get_database
from app.utils.enums import TokenType, UserRole


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
# OAuth2 Scheme
# ---------------------------------------------------------------------------
# Pre-wired OAuth2PasswordBearer for token extraction from the
# Authorization header. FastAPI uses this to:
#   1. Extract "Bearer <token>" from the Authorization header.
#   2. Show the Authorize button in Swagger UI.
#   3. Show lock icons on protected endpoints.
#
# auto_error=True: returns 401 if no token (protected endpoints).
# auto_error=False: returns None if no token (optional auth endpoints).

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
)

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


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
        email: Email address (optional, for notifications and OTP).
        name: Display name (optional, for personalized responses).
        is_active: Whether the account is enabled.
    """
    id: str
    role: UserRole
    phone: str
    email: str | None = None
    name: str | None = None
    is_active: bool = True


# ---------------------------------------------------------------------------
# Auth Dependencies
# ---------------------------------------------------------------------------
# These raise UnauthorizedException until the auth module is built.
# When auth is implemented in Phase 3.2:
#   1. Decode the JWT token using decode_token() from security.py.
#   2. Validate the token type is "access" (not "refresh").

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> CurrentUser:
    """
    Extract and validate the current user from the JWT access token.

    Decodes JWT, verifies access token type, retrieves User document,
    sets user_id_var logging context, and returns CurrentUser interface.
    """
    from app.auth.repository import AuthRepository
    from app.core.context import user_id_var
    from app.core.exceptions import TokenInvalidException, UnauthorizedException
    from app.core.security import decode_token

    payload = decode_token(token)

    if payload.type != TokenType.ACCESS.value:
        raise TokenInvalidException(message="Invalid token type. Expected access token.")

    user = await AuthRepository.find_user_by_id(payload.sub)
    if not user:
        raise UnauthorizedException(
            message="User account associated with this token no longer exists",
            error_code="USER_NOT_FOUND",
        )

    # Set logger correlation context
    user_id_var.set(str(user.id))

    return CurrentUser(
        id=str(user.id),
        role=user.role,
        phone=user.phone,
        email=user.email,
        name=user.full_name,
        is_active=user.is_active,
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
# Optional Auth Dependency
# ---------------------------------------------------------------------------

async def get_optional_user(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
) -> CurrentUser | None:
    """
    Optionally extract the current user from the request.

    Returns None if no token is present or if token is invalid.
    """
    if token is None:
        return None
    try:
        return await get_current_user(token)
    except Exception:
        return None


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
OptionalUserDep = Annotated[CurrentUser | None, Depends(get_optional_user)]


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
