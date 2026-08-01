"""
Role-Based Access Control (RBAC) & Permissions — KaamSetu Service Marketplace.

Defines granular operational permissions across all 11 feature modules,
maps platform roles (customer/worker/admin) to their allowed action sets,
and provides composable programmatic verification helpers.
"""

from enum import Enum
from typing import Final

from app.auth.exceptions import InsufficientPermissionsError
from app.auth.models import UserRole


# =============================================================================
# Granular Action Permissions
# =============================================================================

class Permission(str, Enum):
    """
    Granular permission tokens representing operations across all feature modules.
    """

    # --- User & Profile ---
    USER_READ_OWN = "user:read:own"
    USER_UPDATE_OWN = "user:update:own"
    USER_DELETE_OWN = "user:delete:own"
    USER_MANAGE_ALL = "user:manage:all"

    # --- Service Requests ---
    SERVICE_REQUEST_CREATE = "service_request:create"
    SERVICE_REQUEST_READ_OWN = "service_request:read:own"
    SERVICE_REQUEST_CANCEL_OWN = "service_request:cancel:own"
    SERVICE_REQUEST_MANAGE_ALL = "service_request:manage:all"

    # --- Inspection Requests ---
    INSPECTION_REQUEST_CREATE = "inspection_request:create"
    INSPECTION_REQUEST_READ_OWN = "inspection_request:read:own"
    INSPECTION_REQUEST_SUBMIT_REPORT = "inspection_request:submit_report"
    INSPECTION_REQUEST_MANAGE_ALL = "inspection_request:manage:all"

    # --- Jobs ---
    JOB_READ_OWN = "job:read:own"
    JOB_ACCEPT = "job:accept"
    JOB_UPDATE_STATUS = "job:update_status"
    JOB_COMPLETE = "job:complete"
    JOB_MANAGE_ALL = "job:manage:all"

    # --- Reviews ---
    REVIEW_CREATE = "review:create"
    REVIEW_READ = "review:read"
    REVIEW_MODERATE_ALL = "review:moderate:all"

    # --- Catalog & Pricing ---
    CATALOG_READ = "catalog:read"
    CATALOG_MANAGE_ALL = "catalog:manage:all"
    PRICING_READ = "pricing:read"
    PRICING_MANAGE_ALL = "pricing:manage:all"

    # --- Admin & System ---
    AUDIT_LOG_READ = "audit_log:read"
    SYSTEM_CONFIG_MANAGE = "system_config:manage"
    WORKER_VERIFICATION_MANAGE = "worker_verification:manage"
    SUPPORT_TICKET_MANAGE = "support_ticket:manage"
    ADMIN_FULL_ACCESS = "admin:full_access"


# =============================================================================
# Role to Permission Mapping Table
# =============================================================================

ROLE_PERMISSIONS: Final[dict[UserRole, set[Permission]]] = {
    UserRole.CUSTOMER: {
        Permission.USER_READ_OWN,
        Permission.USER_UPDATE_OWN,
        Permission.USER_DELETE_OWN,
        Permission.SERVICE_REQUEST_CREATE,
        Permission.SERVICE_REQUEST_READ_OWN,
        Permission.SERVICE_REQUEST_CANCEL_OWN,
        Permission.INSPECTION_REQUEST_CREATE,
        Permission.INSPECTION_REQUEST_READ_OWN,
        Permission.JOB_READ_OWN,
        Permission.REVIEW_CREATE,
        Permission.REVIEW_READ,
        Permission.CATALOG_READ,
        Permission.PRICING_READ,
    },
    UserRole.WORKER: {
        Permission.USER_READ_OWN,
        Permission.USER_UPDATE_OWN,
        Permission.SERVICE_REQUEST_READ_OWN,
        Permission.INSPECTION_REQUEST_READ_OWN,
        Permission.INSPECTION_REQUEST_SUBMIT_REPORT,
        Permission.JOB_READ_OWN,
        Permission.JOB_ACCEPT,
        Permission.JOB_UPDATE_STATUS,
        Permission.JOB_COMPLETE,
        Permission.REVIEW_READ,
        Permission.CATALOG_READ,
        Permission.PRICING_READ,
    },
    UserRole.ADMIN: {permission for permission in Permission},
}


# =============================================================================
# Programmatic Permission Verification Helpers
# =============================================================================

def has_permission(role: UserRole, permission: Permission) -> bool:
    """
    Check if a platform role is granted a specific operational permission.

    Args:
        role: UserRole enum value.
        permission: Permission enum value to verify.

    Returns:
        True if the role possesses the permission or ADMIN_FULL_ACCESS.
    """
    allowed_permissions = ROLE_PERMISSIONS.get(role, set())
    return (
        Permission.ADMIN_FULL_ACCESS in allowed_permissions
        or permission in allowed_permissions
    )


def has_any_permission(role: UserRole, permissions: list[Permission]) -> bool:
    """
    Check if a role possesses at least one permission from a given list.

    Args:
        role: UserRole enum value.
        permissions: List of Permission tokens to evaluate.

    Returns:
        True if at least one permission is granted.
    """
    return any(has_permission(role, permission) for permission in permissions)


def has_all_permissions(role: UserRole, permissions: list[Permission]) -> bool:
    """
    Check if a role possesses every permission in a given list.

    Args:
        role: UserRole enum value.
        permissions: List of Permission tokens to evaluate.

    Returns:
        True if all permissions are granted.
    """
    return all(has_permission(role, permission) for permission in permissions)


def require_permission(role: UserRole, permission: Permission) -> None:
    """
    Enforce that a role possesses a required permission, raising HTTP 403 if denied.

    Args:
        role: UserRole enum value.
        permission: Required Permission token.

    Raises:
        InsufficientPermissionsError: If the role does not have the required permission.
    """
    if not has_permission(role, permission):
        raise InsufficientPermissionsError(
            message=f"Your role ({role.value}) lacks permission: {permission.value}",
            error_code="INSUFFICIENT_PERMISSIONS",
        )
