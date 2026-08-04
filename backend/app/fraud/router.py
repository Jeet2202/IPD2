"""
REST API endpoints for Fraud Detection & Abuse Prevention.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep
from app.auth.models import User
from app.fraud.schemas import (
    AbuseReportCreate,
    AbuseReportRead,
    AlertPriority,
    AlertStatus,
    FraudAlertRead,
    FraudAlertResolveRequest,
    FraudAnalysisRequest,
    FraudAnalysisResponse,
    FraudEventRead,
    FraudRuleCreate,
    FraudRuleRead,
    FraudRuleUpdate,
    FraudStatisticsRead,
)
from app.fraud.service import (
    AbuseDetectionService,
    AlertService,
    FraudConfigService,
    FraudDetectionService,
)
from app.utils.enums import UserRole

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. POST /fraud/analyze
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=FraudAnalysisResponse,
    summary="Analyze user activity for fraud & abuse",
    description="Evaluates user activity against active fraud rules, computes explainable risk scores, and executes automated actions.",
)
async def analyze_activity(
    req: FraudAnalysisRequest,
    current_user: ActiveUserDep,
) -> FraudAnalysisResponse:
    """Analyze activity."""
    # Ensure regular users can only analyze their own activity unless Admin
    if current_user.role != UserRole.ADMIN and str(req.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only request fraud analysis for their own activity.",
        )

    return await FraudDetectionService.analyze_activity(req)


# ---------------------------------------------------------------------------
# 2. GET /fraud/events
# ---------------------------------------------------------------------------

@router.get(
    "/events",
    response_model=list[FraudEventRead],
    summary="Get fraud detection events",
    description="Retrieve fraud detection event logs.",
)
async def get_fraud_events(
    current_user: ActiveUserDep,
    target_user_id: str | None = Query(default=None, description="Target user ID"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[FraudEventRead]:
    """Get fraud events."""
    user_id = str(current_user.id)
    if current_user.role == UserRole.ADMIN:
        user_id = str(target_user_id) if target_user_id else None
    else:
        if target_user_id and str(target_user_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only view their own fraud events.",
            )

    events = await FraudDetectionService.get_fraud_events(user_id=user_id, skip=skip, limit=limit)
    return [FraudEventRead.model_validate(e) for e in events]


# ---------------------------------------------------------------------------
# 3. GET /fraud/alerts
# ---------------------------------------------------------------------------

@router.get(
    "/alerts",
    response_model=list[FraudAlertRead],
    summary="Get fraud alerts",
    description="Retrieve administrative fraud alerts (Admin restricted).",
)
async def get_fraud_alerts(
    admin_user: AdminUserDep,
    target_user_id: str | None = Query(default=None, description="Filter by user ID"),
    alert_status: AlertStatus | None = Query(default=None, alias="status"),
    priority: AlertPriority | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[FraudAlertRead]:
    """Get fraud alerts."""
    alerts = await AlertService.list_alerts(
        user_id=str(target_user_id) if target_user_id else None,
        status=alert_status,
        priority=priority,
        skip=skip,
        limit=limit,
    )
    return [FraudAlertRead.model_validate(a) for a in alerts]


# ---------------------------------------------------------------------------
# 4. GET /fraud/rules
# ---------------------------------------------------------------------------

@router.get(
    "/rules",
    response_model=list[FraudRuleRead],
    summary="Get fraud detection rules",
    description="Retrieve system-wide fraud detection rules and threshold configurations.",
)
async def get_fraud_rules(
    current_user: ActiveUserDep,
) -> list[FraudRuleRead]:
    """Get fraud rules."""
    rules = await FraudConfigService.list_active_rules()
    return [FraudRuleRead.model_validate(r) for r in rules]


# ---------------------------------------------------------------------------
# 5. PUT /fraud/rules
# ---------------------------------------------------------------------------

@router.put(
    "/rules",
    response_model=FraudRuleRead,
    summary="Create or update fraud rule",
    description="Create or update a fraud rule definition (Admin restricted).",
)
async def update_fraud_rule(
    rule_key: str = Query(..., description="Unique rule key"),
    rule_update: FraudRuleUpdate = ...,
    admin_user: AdminUserDep = ...,
) -> FraudRuleRead:
    """Update fraud rule."""
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    updated = await FraudConfigService.update_rule(rule_key, rule_update, admin_info)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fraud rule '{rule_key}' not found.",
        )
    return FraudRuleRead.model_validate(updated)


# ---------------------------------------------------------------------------
# 6. POST /fraud/resolve
# ---------------------------------------------------------------------------

@router.post(
    "/resolve",
    response_model=FraudAlertRead,
    summary="Resolve fraud alert",
    description="Resolve or dismiss an administrative fraud alert (Admin restricted).",
)
async def resolve_fraud_alert(
    resolve_in: FraudAlertResolveRequest,
    admin_user: AdminUserDep,
) -> FraudAlertRead:
    """Resolve fraud alert."""
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    resolved = await AlertService.resolve_alert(
        alert_id=resolve_in.target_id,
        action=resolve_in.action,
        resolution_notes=resolve_in.notes,
        reviewer=admin_info,
    )
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fraud alert '{resolve_in.target_id}' not found.",
        )
    return FraudAlertRead.model_validate(resolved)


# ---------------------------------------------------------------------------
# 7. GET /fraud/statistics
# ---------------------------------------------------------------------------

@router.get(
    "/statistics",
    response_model=FraudStatisticsRead,
    summary="Get fraud detection statistics",
    description="Retrieve platform fraud detection & risk metrics summary (Admin restricted).",
)
async def get_fraud_statistics(
    admin_user: AdminUserDep,
) -> FraudStatisticsRead:
    """Get fraud statistics."""
    return await FraudDetectionService.get_statistics()


# ---------------------------------------------------------------------------
# 8. POST /fraud/report
# ---------------------------------------------------------------------------

@router.post(
    "/report",
    response_model=AbuseReportRead,
    summary="Submit abuse report",
    description="Submit a report for spam, fake profile, or review manipulation.",
)
async def submit_abuse_report(
    req: AbuseReportCreate,
    current_user: ActiveUserDep,
) -> AbuseReportRead:
    """Submit abuse report."""
    report = await AbuseDetectionService.create_abuse_report(
        reporter_id=str(current_user.id),
        req=req,
    )
    return AbuseReportRead.model_validate(report)
