"""
Repositories for Trust & Safety Infrastructure following Clean Architecture & Repository Pattern.
"""

from datetime import datetime, timezone
from typing import Any
from beanie.operators import RegEx, In

from app.trust.models import (
    RiskEvent,
    SafetyFlag,
    TrustAuditLog,
    TrustPolicy,
    TrustProfile,
    VerificationHistory,
)
from app.trust.schemas import RiskLevel, ReviewStatus, TrustLevel, TrustVerificationStatus
from app.utils.enums import UserRole


class TrustProfileRepository:
    """Repository for managing TrustProfile database operations."""

    @staticmethod
    async def get_by_user_id(user_id: str) -> TrustProfile | None:
        """Fetch a trust profile by user ID."""
        return await TrustProfile.find_one(TrustProfile.user_id == user_id)

    @staticmethod
    async def create_profile(
        user_id: str,
        role: UserRole,
        trust_score: float = 75.0,
        trust_level: TrustLevel = TrustLevel.STANDARD,
        verification_status: TrustVerificationStatus = TrustVerificationStatus.UNVERIFIED,
        risk_level: RiskLevel = RiskLevel.LOW,
        review_status: ReviewStatus = ReviewStatus.CLEAR,
        safety_flags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TrustProfile:
        """Create and save a new TrustProfile document."""
        profile = TrustProfile(
            user_id=user_id,
            role=role,
            trust_score=trust_score,
            trust_level=trust_level,
            verification_status=verification_status,
            risk_level=risk_level,
            review_status=review_status,
            safety_flags=safety_flags or [],
            metadata=metadata or {},
        )
        await profile.insert()
        return profile

    @staticmethod
    async def update_profile(user_id: str, updates: dict[str, Any]) -> TrustProfile | None:
        """Update fields of an existing trust profile."""
        profile = await TrustProfileRepository.get_by_user_id(user_id)
        if not profile:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)

        await profile.save()
        return profile

    @staticmethod
    async def list_profiles(
        role: UserRole | None = None,
        risk_level: RiskLevel | None = None,
        trust_level: TrustLevel | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[TrustProfile]:
        """List trust profiles with optional filtering."""
        query: dict[str, Any] = {}
        if role:
            query["role"] = role
        if risk_level:
            query["risk_level"] = risk_level
        if trust_level:
            query["trust_level"] = trust_level

        return (
            await TrustProfile.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )


class TrustPolicyRepository:
    """Repository for managing TrustPolicy database operations."""

    @staticmethod
    async def get_by_key(policy_key: str) -> TrustPolicy | None:
        """Fetch policy by unique policy key."""
        return await TrustPolicy.find_one(TrustPolicy.policy_key == policy_key)

    @staticmethod
    async def list_active_policies() -> list[TrustPolicy]:
        """Retrieve all active policies."""
        return await TrustPolicy.find(TrustPolicy.is_active == True).to_list()

    @staticmethod
    async def create_policy(policy_data: dict[str, Any]) -> TrustPolicy:
        """Create a new policy document."""
        policy = TrustPolicy(**policy_data)
        await policy.insert()
        return policy

    @staticmethod
    async def update_policy(policy_key: str, updates: dict[str, Any]) -> TrustPolicy | None:
        """Update an existing policy document."""
        policy = await TrustPolicyRepository.get_by_key(policy_key)
        if not policy:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        if "version" not in updates:
            updates["version"] = policy.version + 1

        for key, value in updates.items():
            if value is not None and hasattr(policy, key):
                setattr(policy, key, value)

        await policy.save()
        return policy


class RiskEventRepository:
    """Repository for managing RiskEvent database operations."""

    @staticmethod
    async def create_risk_event(event_data: dict[str, Any]) -> RiskEvent:
        """Record a new risk event."""
        risk_event = RiskEvent(**event_data)
        await risk_event.insert()
        return risk_event

    @staticmethod
    async def get_risk_events_by_user(user_id: str, limit: int = 50) -> list[RiskEvent]:
        """Fetch recent risk events for a specific user."""
        return (
            await RiskEvent.find(RiskEvent.user_id == user_id)
            .sort("-created_at")
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def list_all_risk_events(skip: int = 0, limit: int = 100) -> list[RiskEvent]:
        """List all risk events for system/admin oversight."""
        return (
            await RiskEvent.find_all()
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )


class TrustAuditLogRepository:
    """
    Repository for managing immutable TrustAuditLog entries.

    Guarantees strict audit log immutability.
    """

    @staticmethod
    async def create_audit_log(audit_data: dict[str, Any]) -> TrustAuditLog:
        """Insert a new immutable audit log entry."""
        audit_log = TrustAuditLog(**audit_data)
        await audit_log.insert()
        return audit_log

    @staticmethod
    async def get_audit_logs_by_user(user_id: str, limit: int = 50) -> list[TrustAuditLog]:
        """Fetch audit logs for a target user."""
        return (
            await TrustAuditLog.find(TrustAuditLog.user_id == user_id)
            .sort("-timestamp")
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def list_audit_logs(skip: int = 0, limit: int = 100) -> list[TrustAuditLog]:
        """List all audit logs."""
        return (
            await TrustAuditLog.find_all()
            .sort("-timestamp")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    def update_audit_log(*args: Any, **kwargs: Any) -> None:
        """Immutability guard: audit logs cannot be modified."""
        raise RuntimeError("Audit logs are immutable and cannot be updated.")

    @staticmethod
    def delete_audit_log(*args: Any, **kwargs: Any) -> None:
        """Immutability guard: audit logs cannot be deleted."""
        raise RuntimeError("Audit logs are immutable and cannot be deleted.")


class SafetyFlagRepository:
    """Repository for managing SafetyFlag database operations."""

    @staticmethod
    async def create_flag(flag_data: dict[str, Any]) -> SafetyFlag:
        """Create a new safety flag."""
        flag = SafetyFlag(**flag_data)
        await flag.insert()
        return flag

    @staticmethod
    async def get_active_flags_for_user(user_id: str) -> list[SafetyFlag]:
        """Fetch active safety flags for a user."""
        return await SafetyFlag.find(
            SafetyFlag.user_id == user_id,
            SafetyFlag.status == "active",
        ).to_list()

    @staticmethod
    async def resolve_flag(flag_id: str) -> SafetyFlag | None:
        """Resolve a safety flag."""
        flag = await SafetyFlag.find_one(SafetyFlag.flag_id == flag_id)
        if not flag:
            return None

        flag.status = "resolved"
        flag.resolved_at = datetime.now(timezone.utc)
        await flag.save()
        return flag


class VerificationHistoryRepository:
    """Repository for managing VerificationHistory database operations."""

    @staticmethod
    async def add_record(record_data: dict[str, Any]) -> VerificationHistory:
        """Create a new verification history entry."""
        record = VerificationHistory(**record_data)
        await record.insert()
        return record

    @staticmethod
    async def get_user_history(user_id: str) -> list[VerificationHistory]:
        """Fetch verification history for a user."""
        return (
            await VerificationHistory.find(VerificationHistory.user_id == user_id)
            .sort("-timestamp")
            .to_list()
        )
