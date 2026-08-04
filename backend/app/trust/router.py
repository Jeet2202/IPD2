"""
REST API endpoints for Trust & Safety Infrastructure.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep
from app.auth.models import User
from app.trust.schemas import (
    AuditLogRead,
    RiskEventRead,
    RiskEventType,
    RiskLevel,
    TrustPolicyCreate,
    TrustPolicyRead,
    TrustPolicyUpdate,
    TrustProfileRead,
    TrustProfileUpdate,
    TrustReviewCreate,
    TrustReviewResponse,
    TrustStatusRead,
)
from app.trust.service import (
    AuditService,
    PolicyService,
    RiskService,
    TrustService,
)
from app.utils.enums import UserRole

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. GET /trust/profile
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=TrustProfileRead,
    summary="Get trust profile",
    description="Retrieve trust profile for current user or target user (admin only).",
)
async def get_trust_profile(
    current_user: ActiveUserDep,
    target_user_id: str | None = Query(default=None, description="Target user ID (Admin only)"),
) -> TrustProfileRead:
    """Get trust profile."""
    user_id = str(current_user.id)
    if target_user_id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can request trust profiles of other users.",
            )
        user_id = str(target_user_id)

    profile = await TrustService.get_or_create_profile(user_id, current_user.role)
    return TrustProfileRead.model_validate(profile)


# ---------------------------------------------------------------------------
# 2. GET /trust/status
# ---------------------------------------------------------------------------

@router.get(
    "/status",
    response_model=TrustStatusRead,
    summary="Get trust status summary",
    description="Retrieve high-level trust status summary for current user or target user (admin only).",
)
async def get_trust_status(
    current_user: ActiveUserDep,
    target_user_id: str | None = Query(default=None, description="Target user ID (Admin only)"),
) -> TrustStatusRead:
    """Get trust status summary."""
    user_id = str(current_user.id)
    user_role = current_user.role

    if target_user_id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can request trust status of other users.",
            )
        user_id = str(target_user_id)
        # Fetch target user role if available
        target_user = await User.get(target_user_id)
        if target_user:
            user_role = target_user.role

    return await TrustService.get_trust_status(user_id, user_role)


# ---------------------------------------------------------------------------
# 3. GET /trust/risk
# ---------------------------------------------------------------------------

@router.get(
    "/risk",
    response_model=list[RiskEventRead],
    summary="Get risk events",
    description="Retrieve risk events for current user or platform risk logs (admin only).",
)
async def get_risk_events(
    current_user: ActiveUserDep,
    target_user_id: str | None = Query(default=None, description="Target user ID"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[RiskEventRead]:
    """Get risk events."""
    current_user_id = str(current_user.id)
    if current_user.role == UserRole.ADMIN:
        if target_user_id:
            events = await RiskService.get_user_risk_events(str(target_user_id), limit=limit)
        else:
            events = await RiskService.list_all_risk_events(skip=skip, limit=limit)
    else:
        if target_user_id and str(target_user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only access their own risk event logs.",
            )
        events = await RiskService.get_user_risk_events(current_user_id, limit=limit)

    return [RiskEventRead.model_validate(e) for e in events]


# ---------------------------------------------------------------------------
# 4. GET /trust/policies
# ---------------------------------------------------------------------------

@router.get(
    "/policies",
    response_model=list[TrustPolicyRead],
    summary="Get active trust policies",
    description="Retrieve system-wide active trust policies and score thresholds.",
)
async def get_policies(
    current_user: ActiveUserDep,
) -> list[TrustPolicyRead]:
    """Get active trust policies."""
    policies = await PolicyService.list_active_policies()
    return [TrustPolicyRead.model_validate(p) for p in policies]


# ---------------------------------------------------------------------------
# 5. GET /trust/audit
# ---------------------------------------------------------------------------

@router.get(
    "/audit",
    response_model=list[AuditLogRead],
    summary="Get audit logs",
    description="Retrieve immutable audit log history.",
)
async def get_audit_logs(
    current_user: ActiveUserDep,
    target_user_id: str | None = Query(default=None, description="Target user ID (Admin only)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[AuditLogRead]:
    """Get audit logs."""
    current_user_id = str(current_user.id)
    if current_user.role == UserRole.ADMIN:
        if target_user_id:
            logs = await AuditService.get_user_audit_logs(str(target_user_id), limit=limit)
        else:
            logs = await AuditService.list_all_audit_logs(skip=skip, limit=limit)
    else:
        if target_user_id and str(target_user_id) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only access their own audit logs.",
            )
        logs = await AuditService.get_user_audit_logs(current_user_id, limit=limit)

    return [AuditLogRead.model_validate(l) for l in logs]


# ---------------------------------------------------------------------------
# 6. POST /trust/review
# ---------------------------------------------------------------------------

@router.post(
    "/review",
    response_model=TrustReviewResponse,
    summary="Submit manual trust review",
    description="Submit an administrative trust review for a user account (Admin restricted).",
)
async def submit_trust_review(
    review_in: TrustReviewCreate,
    admin_user: AdminUserDep,
) -> TrustReviewResponse:
    """Submit manual trust review."""
    reviewer_info = {
        "id": str(admin_user.id),
        "role": admin_user.role.value,
        "email": admin_user.email,
    }
    try:
        return await TrustService.review_user_trust(
            target_user_id=str(review_in.target_user_id),
            action=review_in.action,
            reason=review_in.reason,
            reviewer=reviewer_info,
            new_risk_level=review_in.new_risk_level,
            notes=review_in.notes,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


# ---------------------------------------------------------------------------
# 7. PUT /trust/profile
# ---------------------------------------------------------------------------

@router.put(
    "/profile",
    response_model=TrustProfileRead,
    summary="Update trust profile",
    description="Update profile attributes or trust flags (Admin restricted).",
)
async def update_trust_profile(
    update_in: TrustProfileUpdate,
    admin_user: AdminUserDep,
    target_user_id: str = Query(..., description="Target user ID to update"),
) -> TrustProfileRead:
    """Update trust profile."""
    actor_info = {
        "id": str(admin_user.id),
        "role": admin_user.role.value,
        "email": admin_user.email,
    }
    updated_profile = await TrustService.update_profile(
        user_id=str(target_user_id),
        update_in=update_in,
        actor=actor_info,
    )
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trust profile for user {target_user_id} not found.",
        )

    return TrustProfileRead.model_validate(updated_profile)
