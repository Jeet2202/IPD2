"""
Repository for Trust Intelligence & Risk Assessment following Clean Architecture & Repository Pattern.
"""

from typing import Any
from app.trust_intelligence.models import TrustIntelligenceSnapshot


class TrustIntelligenceRepository:
    """Repository for managing TrustIntelligenceSnapshot database operations."""

    @staticmethod
    async def create_snapshot(data: dict[str, Any]) -> TrustIntelligenceSnapshot:
        """Create and save a new TrustIntelligenceSnapshot."""
        snapshot = TrustIntelligenceSnapshot(**data)
        await snapshot.insert()
        return snapshot

    @staticmethod
    async def list_snapshots(limit: int = 30) -> list[TrustIntelligenceSnapshot]:
        """Fetch historical snapshots ordered by creation date descending."""
        return (
            await TrustIntelligenceSnapshot.find_all()
            .sort("-created_at")
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def get_latest_snapshot() -> TrustIntelligenceSnapshot | None:
        """Fetch the most recent snapshot."""
        snapshots = await TrustIntelligenceRepository.list_snapshots(limit=1)
        return snapshots[0] if snapshots else None
