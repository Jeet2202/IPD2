"""
REST API endpoints for Trust Intelligence & Risk Assessment.
"""

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import AdminUserDep
from app.trust_intelligence.schemas import (
    ComplianceIntelligenceRead,
    FraudIntelligenceRead,
    MetricRecommendation,
    ModerationIntelligenceRead,
    RiskAssessmentRead,
    RiskTrendRead,
    SecurityIntelligenceRead,
    TrustOverviewRead,
)
from app.trust_intelligence.service import (
    RiskAssessmentService,
    RiskTrendService,
    TrustRecommendationService,
    TrustSummaryService,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. GET /trust/intelligence/overview
# ---------------------------------------------------------------------------

@router.get(
    "/overview",
    response_model=TrustOverviewRead,
    summary="Get platform trust overview",
    description="Retrieve average trust scores, score distributions, and worker verification status (Admin restricted).",
)
async def get_trust_overview(
    admin_user: AdminUserDep,
) -> TrustOverviewRead:
    """Get trust overview."""
    return await TrustSummaryService.get_trust_overview()


# ---------------------------------------------------------------------------
# 2. GET /trust/intelligence/fraud
# ---------------------------------------------------------------------------

@router.get(
    "/fraud",
    response_model=FraudIntelligenceRead,
    summary="Get fraud intelligence summary",
    description="Retrieve active fraud cases, rule trigger stats, and fraud resolution rates (Admin restricted).",
)
async def get_fraud_intelligence(
    admin_user: AdminUserDep,
) -> FraudIntelligenceRead:
    """Get fraud intelligence."""
    return await TrustSummaryService.get_fraud_intelligence()


# ---------------------------------------------------------------------------
# 3. GET /trust/intelligence/moderation
# ---------------------------------------------------------------------------

@router.get(
    "/moderation",
    response_model=ModerationIntelligenceRead,
    summary="Get moderation intelligence summary",
    description="Retrieve pending report counts, escalated cases, and open dispute stats (Admin restricted).",
)
async def get_moderation_intelligence(
    admin_user: AdminUserDep,
) -> ModerationIntelligenceRead:
    """Get moderation intelligence."""
    return await TrustSummaryService.get_moderation_intelligence()


# ---------------------------------------------------------------------------
# 4. GET /trust/intelligence/compliance
# ---------------------------------------------------------------------------

@router.get(
    "/compliance",
    response_model=ComplianceIntelligenceRead,
    summary="Get compliance intelligence summary",
    description="Retrieve privacy request counts, export statistics, and user consent opt-in rates (Admin restricted).",
)
async def get_compliance_intelligence(
    admin_user: AdminUserDep,
) -> ComplianceIntelligenceRead:
    """Get compliance intelligence."""
    return await TrustSummaryService.get_compliance_intelligence()


# ---------------------------------------------------------------------------
# 5. GET /trust/intelligence/security
# ---------------------------------------------------------------------------

@router.get(
    "/security",
    response_model=SecurityIntelligenceRead,
    summary="Get security intelligence summary",
    description="Retrieve failed logins, auth failures, active security alerts, and critical events (Admin restricted).",
)
async def get_security_intelligence(
    admin_user: AdminUserDep,
) -> SecurityIntelligenceRead:
    """Get security intelligence."""
    return await TrustSummaryService.get_security_intelligence()


# ---------------------------------------------------------------------------
# 6. GET /trust/intelligence/recommendations
# ---------------------------------------------------------------------------

@router.get(
    "/recommendations",
    response_model=list[MetricRecommendation],
    summary="Get metric-referenced admin recommendations",
    description="Retrieve actionable admin recommendations referencing live platform metrics (Admin restricted).",
)
async def get_recommendations(
    admin_user: AdminUserDep,
) -> list[MetricRecommendation]:
    """Get recommendations."""
    return await TrustRecommendationService.get_recommendations()


# ---------------------------------------------------------------------------
# 7. GET /trust/intelligence/trends
# ---------------------------------------------------------------------------

@router.get(
    "/trends",
    response_model=RiskTrendRead,
    summary="Get risk trends analytics",
    description="Retrieve historical risk event counts and alert trends over 7d/30d windows (Admin restricted).",
)
async def get_risk_trends(
    admin_user: AdminUserDep,
    window_days: int = Query(default=7, ge=1, le=90),
) -> RiskTrendRead:
    """Get risk trends."""
    return await RiskTrendService.get_risk_trends(window_days=window_days)
