"""
Role and permission system — defines what each role can do.

Architecture:
    - Permission enum: granular actions (CREATE_JOB, MANAGE_WORKERS, etc.)
    - ROLE_PERMISSIONS: maps each UserRole to its allowed permissions.
    - has_permission() / require_permission(): check/enforce access.

Design decisions:
    - Permissions are code-defined, not database-driven. With 3 roles
      and <30 permissions, a dict lookup is simpler and faster than a
      database table. If per-user permissions are needed later, the
      has_permission() interface stays the same — just change the source.
    - Permission names follow VERB_NOUN convention for clarity:
      CREATE_JOB, VIEW_WORKERS, MANAGE_PRICING.
    - Each feature module defines its own permissions here as the
      feature is built. This file grows incrementally.
"""

from enum import Enum

from app.core.dependencies import UserRole
from app.core.exceptions import ForbiddenException


# ---------------------------------------------------------------------------
# Permission Definitions
# ---------------------------------------------------------------------------

class Permission(str, Enum):
    """
    Granular permissions for the marketplace.

    Convention: VERB_NOUN in UPPER_SNAKE_CASE.
    Grouped by feature module for readability.
    Add new permissions here as features are built.
    """

    # --- Jobs ---
    CREATE_JOB = "create_job"
    VIEW_JOBS = "view_jobs"
    UPDATE_OWN_JOB = "update_own_job"
    CANCEL_OWN_JOB = "cancel_own_job"
    ACCEPT_JOB = "accept_job"            # Workers accept available jobs

    # --- Workers ---
    VIEW_WORKERS = "view_workers"
    UPDATE_OWN_PROFILE = "update_own_profile"

    # --- Customers ---
    VIEW_OWN_BOOKINGS = "view_own_bookings"

    # --- Reviews ---
    CREATE_REVIEW = "create_review"
    VIEW_REVIEWS = "view_reviews"

    # --- Uploads ---
    UPLOAD_FILES = "upload_files"

    # --- Pricing ---
    VIEW_PRICING = "view_pricing"

    # --- Notifications ---
    VIEW_OWN_NOTIFICATIONS = "view_own_notifications"

    # --- Inspection ---
    CREATE_INSPECTION = "create_inspection"
    VIEW_INSPECTIONS = "view_inspections"

    # --- Admin ---
    MANAGE_USERS = "manage_users"
    MANAGE_WORKERS = "manage_workers"
    MANAGE_JOBS = "manage_jobs"
    MANAGE_PRICING = "manage_pricing"
    MANAGE_REVIEWS = "manage_reviews"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_INSPECTIONS = "manage_inspections"


# ---------------------------------------------------------------------------
# Role → Permission Mapping
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.CUSTOMER: {
        Permission.CREATE_JOB,
        Permission.VIEW_JOBS,
        Permission.UPDATE_OWN_JOB,
        Permission.CANCEL_OWN_JOB,
        Permission.VIEW_WORKERS,
        Permission.VIEW_OWN_BOOKINGS,
        Permission.CREATE_REVIEW,
        Permission.VIEW_REVIEWS,
        Permission.UPLOAD_FILES,
        Permission.VIEW_PRICING,
        Permission.VIEW_OWN_NOTIFICATIONS,
        Permission.CREATE_INSPECTION,
    },

    UserRole.WORKER: {
        Permission.VIEW_JOBS,
        Permission.ACCEPT_JOB,
        Permission.UPDATE_OWN_PROFILE,
        Permission.VIEW_REVIEWS,
        Permission.UPLOAD_FILES,
        Permission.VIEW_PRICING,
        Permission.VIEW_OWN_NOTIFICATIONS,
        Permission.VIEW_INSPECTIONS,
    },

    UserRole.ADMIN: set(Permission),  # Admins have ALL permissions
}


# ---------------------------------------------------------------------------
# Permission Checking Utilities
# ---------------------------------------------------------------------------

def has_permission(role: UserRole, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    O(1) set lookup — no database query needed.

    Args:
        role: The user's role.
        permission: The permission to check.

    Returns:
        True if the role has the permission.
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return permission in role_perms


def require_permission(role: UserRole, permission: Permission) -> None:
    """
    Enforce that a role has a specific permission.

    Raises ForbiddenException if the role lacks the permission.
    Use in service layer functions for fine-grained access control
    beyond role-based route guards.

    Usage:
        from app.core.permissions import require_permission, Permission

        async def assign_worker(user: CurrentUser, job_id: str):
            require_permission(user.role, Permission.MANAGE_JOBS)
            # ... proceed with assignment

    Args:
        role: The user's role.
        permission: The required permission.

    Raises:
        ForbiddenException: If the role lacks the permission.
    """
    if not has_permission(role, permission):
        raise ForbiddenException(
            message=f"Permission denied: {permission.value}",
            error_code="PERMISSION_DENIED",
            details=[{"required_permission": permission.value, "role": role.value}],
        )
