"""
FastAPI Authentication & Authorization Dependencies — KaamSetu Service Marketplace.

Provides composable, asynchronous dependency guards for JWT validation,
user document resolution, account lifecycle state enforcement, verification
checks, and Role-Based Access Control (RBAC).

Usage in routers:
    from app.auth.dependencies import ActiveUserDep, RequirePermissions
    from app.auth.permissions import Permission

    @router.post("/services", dependencies=[Depends(RequirePermissions(Permission.CATALOG_MANAGE_ALL))])
    async def create_service(user: ActiveUserDep, ...):
        ...
"""

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer

from app.auth.constants import ACCESS_TOKEN_TYPE
from app.auth.exceptions import (
    AccountBlockedError,
    AccountInactiveError,
    AccountPendingVerificationError,
    AuthenticationError,
    EmailNotVerifiedError,
    InsufficientPermissionsError,
    PhoneNotVerifiedError,
    ProfileIncompleteError,
    TokenRevokedError,
)
from app.auth.models import AccountStatus, User, UserRole
from app.auth.permissions import Permission, require_permission
from app.auth.security import TokenPayload, decode_token
from app.auth.utils import extract_bearer_token

# OAuth2 bearer token extractor (auto_error=False to allow custom KaamSetu exception handling)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# =============================================================================
# Token Payload & User Identity Dependencies
# =============================================================================

async def get_token_payload(
    token: str | None = Depends(oauth2_scheme),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> TokenPayload:
    """
    Extract, decode, and verify the Bearer access token from HTTP headers.

    Args:
        token: Token string extracted by OAuth2PasswordBearer.
        authorization: Raw Authorization header fallback.

    Returns:
        Validated TokenPayload Pydantic instance.

    Raises:
        AuthenticationError: If credentials are missing.
        TokenExpiredError: If the token has expired.
        InvalidTokenError: If the token signature is invalid or not an access token.
    """
    token_str = token
    if not token_str:
        if authorization:
            token_str = extract_bearer_token(authorization)
        else:
            raise AuthenticationError(
                message="Authentication credentials were not provided",
                error_code="MISSING_CREDENTIALS",
            )

    return decode_token(token_str, expected_type=ACCESS_TOKEN_TYPE)


async def get_current_user(
    payload: TokenPayload = Depends(get_token_payload),
) -> User:
    """
    Resolve the Beanie User document from the decoded token subject.

    Also checks refresh token version revocation if token payload contains a ver claim.

    Args:
        payload: Validated TokenPayload.

    Returns:
        The database User document.

    Raises:
        AuthenticationError: If the user no longer exists in the database.
        TokenRevokedError: If the refresh token version does not match the database counter.
    """
    user = await User.get(payload.sub)
    if not user:
        raise AuthenticationError(
            message="User account no longer exists",
            error_code="USER_NOT_FOUND",
        )

    if payload.ver is not None and payload.ver != user.refresh_token_version:
        raise TokenRevokedError()

    return user


# =============================================================================
# Account Lifecycle & Verification Dependencies
# =============================================================================

async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the authenticated user account is in an ACTIVE lifecycle state.

    Args:
        user: Authenticated User document.

    Returns:
        The verified active User document.

    Raises:
        AccountInactiveError: If account is voluntarily inactive.
        AccountBlockedError: If account is suspended by admin.
        AccountPendingVerificationError: If verification is incomplete.
    """
    if user.account_status == AccountStatus.INACTIVE:
        raise AccountInactiveError()
    if user.account_status == AccountStatus.BLOCKED:
        raise AccountBlockedError()
    if user.account_status == AccountStatus.PENDING_VERIFICATION:
        raise AccountPendingVerificationError()

    return user


async def get_current_verified_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Ensure the user has verified either their email address or phone number.

    Args:
        user: Active User document.

    Returns:
        The verified User document.

    Raises:
        EmailNotVerifiedError: If neither email nor phone is verified.
    """
    if not user.email_verified and not user.phone_verified:
        raise EmailNotVerifiedError(
            message="You must verify your email or phone number to perform this action",
            error_code="CONTACT_NOT_VERIFIED",
        )
    return user


async def get_email_verified_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user has specifically verified their email address."""
    if not user.email_verified:
        raise EmailNotVerifiedError()
    return user


async def get_phone_verified_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user has specifically verified their phone number."""
    if not user.phone_verified:
        raise PhoneNotVerifiedError()
    return user


async def get_current_profile_completed_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Ensure the user has completed all mandatory onboarding profile fields.

    Args:
        user: Active User document.

    Returns:
        The profile-completed User document.

    Raises:
        ProfileIncompleteError: If profile_completed is False.
    """
    if not user.profile_completed:
        raise ProfileIncompleteError()
    return user


# =============================================================================
# Role-Specific Guard Dependencies
# =============================================================================

async def get_current_customer(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Restrict access to CUSTOMER or ADMIN roles.

    Args:
        user: Active User document.

    Returns:
        The User document if permitted.

    Raises:
        InsufficientPermissionsError: If user is not CUSTOMER or ADMIN.
    """
    if user.role != UserRole.CUSTOMER and user.role != UserRole.ADMIN:
        raise InsufficientPermissionsError(
            message="This endpoint is restricted to customers",
            error_code="CUSTOMER_ROLE_REQUIRED",
        )
    return user


async def get_current_worker(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Restrict access to WORKER or ADMIN roles.

    Args:
        user: Active User document.

    Returns:
        The User document if permitted.

    Raises:
        InsufficientPermissionsError: If user is not WORKER or ADMIN.
    """
    if user.role != UserRole.WORKER and user.role != UserRole.ADMIN:
        raise InsufficientPermissionsError(
            message="This endpoint is restricted to service workers",
            error_code="WORKER_ROLE_REQUIRED",
        )
    return user


async def get_current_admin(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Restrict access strictly to ADMIN role.

    Args:
        user: Active User document.

    Returns:
        The User document if permitted.

    Raises:
        InsufficientPermissionsError: If user is not ADMIN.
    """
    if user.role != UserRole.ADMIN:
        raise InsufficientPermissionsError(
            message="This endpoint is restricted to platform administrators",
            error_code="ADMIN_ROLE_REQUIRED",
        )
    return user


# =============================================================================
# Composable Declarative RBAC Dependency Factories
# =============================================================================

class RequirePermissions:
    """
    Callable dependency class to enforce one or more granular permissions.

    Usage:
        @router.delete("/jobs/{id}", dependencies=[Depends(RequirePermissions(Permission.JOB_MANAGE_ALL))])
    """

    def __init__(self, *permissions: Permission) -> None:
        self.permissions = list(permissions)

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        for permission in self.permissions:
            require_permission(user.role, permission)
        return user


class RequireRole:
    """
    Callable dependency class to restrict access to a specific set of roles.

    Usage:
        @router.post("/payouts", dependencies=[Depends(RequireRole(UserRole.WORKER, UserRole.ADMIN))])
    """

    def __init__(self, *allowed_roles: UserRole) -> None:
        self.allowed_roles = set(allowed_roles)

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if user.role not in self.allowed_roles and user.role != UserRole.ADMIN:
            raise InsufficientPermissionsError(
                message=f"Your role '{user.role.value}' is not permitted for this resource",
                error_code="ROLE_NOT_PERMITTED",
            )
        return user


# =============================================================================
# Type-Annotated Dependency Aliases
# =============================================================================

CurrentUserDep = Annotated[User, Depends(get_current_user)]
ActiveUserDep = Annotated[User, Depends(get_current_active_user)]
VerifiedUserDep = Annotated[User, Depends(get_current_verified_user)]
EmailVerifiedUserDep = Annotated[User, Depends(get_email_verified_user)]
PhoneVerifiedUserDep = Annotated[User, Depends(get_phone_verified_user)]
ProfileCompletedUserDep = Annotated[User, Depends(get_current_profile_completed_user)]
CustomerUserDep = Annotated[User, Depends(get_current_customer)]
WorkerUserDep = Annotated[User, Depends(get_current_worker)]
AdminUserDep = Annotated[User, Depends(get_current_admin)]
