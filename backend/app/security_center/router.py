"""
REST API endpoints for Security Monitoring & Audit Center.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep
from app.auth.models import User
from app.security_center.schemas import (
    APIHealthRead,
    LoginHistoryRead,
    SecurityAlertAcknowledgeRequest,
    SecurityAlertPriority,
    SecurityAlertRead,
    SecurityAlertStatus,
    SecurityDashboardRead,
    SecurityEventRead,
    SecurityEventType,
    SecurityStatisticsRead,
)
from app.security_center.service import (
    APIMonitoringService,
    AuthMonitoringService,
    SecurityAlertService,
    SecurityDashboardService,
    SecurityEventService,
)
from app.trust.schemas import RiskLevel
from app.utils.enums import UserRole

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. GET /security/events
# ---------------------------------------------------------------------------

@router.get(
    "/events",
    response_model=list[SecurityEventRead],
    summary="Get centralized security events",
    description="Retrieve platform security event logs (Admin restricted).",
)
async def get_security_events(
    admin_user: AdminUserDep,
    target_user_id: str | None = Query(default=None, description="Filter by user ID"),
    event_type: SecurityEventType | None = Query(default=None),
    severity: RiskLevel | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[SecurityEventRead]:
    """Get security events."""
    events = await SecurityEventService.list_security_events(
        user_id=target_user_id, event_type=event_type, severity=severity, skip=skip, limit=limit
    )
    return [SecurityEventRead.model_validate(e) for e in events]


# ---------------------------------------------------------------------------
# 2. GET /security/alerts
# ---------------------------------------------------------------------------

@router.get(
    "/alerts",
    response_model=list[SecurityAlertRead],
    summary="Get security alerts",
    description="Retrieve active and historical administrative security alerts (Admin restricted).",
)
async def get_security_alerts(
    admin_user: AdminUserDep,
    alert_status: SecurityAlertStatus | None = Query(default=None, alias="status"),
    priority: SecurityAlertPriority | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[SecurityAlertRead]:
    """Get security alerts."""
    alerts = await SecurityAlertService.list_alerts(
        status=alert_status, priority=priority, skip=skip, limit=limit
    )
    return [SecurityAlertRead.model_validate(a) for a in alerts]


# ---------------------------------------------------------------------------
# 3. GET /security/dashboard
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    response_model=SecurityDashboardRead,
    summary="Get security dashboard overview",
    description="Retrieve aggregated backend security status, health metrics, and alert summaries (Admin restricted).",
)
async def get_security_dashboard(
    admin_user: AdminUserDep,
) -> SecurityDashboardRead:
    """Get security dashboard."""
    return await SecurityDashboardService.get_security_dashboard()


# ---------------------------------------------------------------------------
# 4. GET /security/login-history
# ---------------------------------------------------------------------------

@router.get(
    "/login-history",
    response_model=list[LoginHistoryRead],
    summary="Get user login history",
    description="Retrieve authentication session and login history records.",
)
async def get_login_history(
    current_user: ActiveUserDep,
    target_user_id: str | None = Query(default=None, description="Target user ID (Admin only)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[LoginHistoryRead]:
    """Get login history."""
    user_id = str(current_user.id)
    if target_user_id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can access login history of other users.",
            )
        user_id = str(target_user_id)

    history = await AuthMonitoringService.get_user_login_history(user_id=user_id, skip=skip, limit=limit)
    return [LoginHistoryRead.model_validate(h) for h in history]


# ---------------------------------------------------------------------------
# 5. GET /security/api-health
# ---------------------------------------------------------------------------

@router.get(
    "/api-health",
    response_model=APIHealthRead,
    summary="Get API traffic and error health metrics",
    description="Retrieve API invocation counts, latency averages, and error percentages (Admin restricted).",
)
async def get_api_health(
    admin_user: AdminUserDep,
    hours: int = Query(default=24, ge=1, le=168),
) -> APIHealthRead:
    """Get API health."""
    return await APIMonitoringService.get_api_health(hours=hours)


# ---------------------------------------------------------------------------
# 6. POST /security/alerts/acknowledge
# ---------------------------------------------------------------------------

@router.post(
    "/alerts/acknowledge",
    response_model=SecurityAlertRead,
    summary="Acknowledge or resolve security alert",
    description="Acknowledge, resolve, or dismiss an administrative security alert (Admin restricted).",
)
async def acknowledge_security_alert(
    req: SecurityAlertAcknowledgeRequest,
    admin_user: AdminUserDep,
) -> SecurityAlertRead:
    """Acknowledge security alert."""
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    updated = await SecurityAlertService.acknowledge_alert(req, admin_info)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security alert '{req.alert_id}' not found.",
        )
    return SecurityAlertRead.model_validate(updated)


# ---------------------------------------------------------------------------
# 7. GET /security/statistics
# ---------------------------------------------------------------------------

@router.get(
    "/statistics",
    response_model=SecurityStatisticsRead,
    summary="Get platform security statistics",
    description="Retrieve platform-wide security statistics summary (Admin restricted).",
)
async def get_security_statistics(
    admin_user: AdminUserDep,
) -> SecurityStatisticsRead:
    """Get security statistics."""
    return await SecurityDashboardService.get_security_statistics()
