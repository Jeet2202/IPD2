"""
Beanie document models for Trust Intelligence & Risk Assessment database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.trust_intelligence.schemas import RiskLevelGrade


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class TrustIntelligenceSnapshot(Document):
    """
    Historical snapshot document for risk score trends and recommendation logs.

    Collection: trust_intelligence_snapshots
    """
    snapshot_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    overall_risk_score: float = 0.0
    overall_grade: RiskLevelGrade = RiskLevelGrade.LOW
    department_scores: dict[str, float] = Field(default_factory=dict)
    platform_health: str = "healthy"
    recommendations_count: int = 0
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "trust_intelligence_snapshots"
        indexes = [
            "created_at",
        ]
