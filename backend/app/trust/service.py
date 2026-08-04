"""
Domain services and Trust Score Engine for Trust & Safety Infrastructure.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from app.trust.models import (
    RiskEvent,
    SafetyFlag,
    TrustAuditLog,
    TrustPolicy,
    TrustProfile,
    VerificationHistory,
)
from app.trust.repository import (
    RiskEventRepository,
    SafetyFlagRepository,
    TrustAuditLogRepository,
    TrustPolicyRepository,
    TrustProfileRepository,
    VerificationHistoryRepository,
)
from app.trust.schemas import (
    AuditEventType,
    AuditLogCreate,
    RiskEventCreate,
    RiskEventType,
    RiskLevel,
    ReviewStatus,
    SafetyFlagCreate,
    TrustLevel,
    TrustPolicyCreate,
    TrustPolicyUpdate,
    TrustProfileUpdate,
    TrustReviewResponse,
    TrustStatusRead,
    TrustVerificationStatus,
    VerificationHistoryCreate,
)
from app.utils.enums import UserRole

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default Configuration Constants
# ---------------------------------------------------------------------------

DEFAULT_SCORE_THRESHOLDS: dict[str, float] = {
    "excellent": 90.0,
    "trusted": 75.0,
    "standard": 50.0,
    "watchlist": 30.0,
    "high_risk": 15.0,
}

DEFAULT_POLICY_KEY = "trust_score_thresholds_v1"


# ---------------------------------------------------------------------------
# Trust Score Engine
# ---------------------------------------------------------------------------

class TrustScoreEngine:
    """Calculates Trust Levels based on configurable score thresholds."""

    @staticmethod
    def calculate_trust_level(score: float, thresholds: dict[str, float] | None = None) -> TrustLevel:
        """
        Evaluate Trust Level for a given numerical trust score (0 - 100).
        """
        t = thresholds or DEFAULT_SCORE_THRESHOLDS
        s = max(0.0, min(100.0, score))

        if s >= t.get("excellent", 90.0):
            return TrustLevel.EXCELLENT
        if s >= t.get("trusted", 75.0):
            return TrustLevel.TRUSTED
        if s >= t.get("standard", 50.0):
            return TrustLevel.STANDARD
        if s >= t.get("watchlist", 30.0):
            return TrustLevel.WATCHLIST
        if s >= t.get("high_risk", 15.0):
            return TrustLevel.HIGH_RISK
        return TrustLevel.RESTRICTED


# ---------------------------------------------------------------------------
# Configuration Service
# ---------------------------------------------------------------------------

class ConfigService:
    """Manages policy thresholds and system-wide Trust & Safety configurations."""

    @staticmethod
    async def get_score_thresholds() -> dict[str, float]:
        """Fetch score thresholds from DB policy, or return defaults."""
        policy = await TrustPolicyRepository.get_by_key(DEFAULT_POLICY_KEY)
        if policy and policy.is_active and "thresholds" in policy.rules:
            return {k: float(v) for k, v in policy.rules["thresholds"].items()}
        return DEFAULT_SCORE_THRESHOLDS

    @staticmethod
    async def initialize_default_policies() -> None:
        """Ensure default trust policies exist in the database."""
        existing = await TrustPolicyRepository.get_by_key(DEFAULT_POLICY_KEY)
        if not existing:
            await TrustPolicyRepository.create_policy({
                "policy_key": DEFAULT_POLICY_KEY,
                "name": "Standard Trust Score Thresholds",
                "category": "score_thresholds",
                "rules": {"thresholds": DEFAULT_SCORE_THRESHOLDS},
                "is_active": True,
                "version": 1,
            })
            logger.info("Initialized default Trust & Safety policies in database.")


# ---------------------------------------------------------------------------
# Audit Logging Service
# ---------------------------------------------------------------------------

class AuditService:
    """Service for managing immutable audit records."""

    @staticmethod
    async def log_event(
        user_id: str,
        event_type: AuditEventType,
        description: str,
        actor: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> TrustAuditLog:
        """Create and store an immutable audit log entry."""
        audit_data = {
            "user_id": user_id,
            "event_type": event_type,
            "description": description,
            "actor": actor,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc),
        }
        log_entry = await TrustAuditLogRepository.create_audit_log(audit_data)
        logger.info(
            "Audit event recorded: user_id=%s, type=%s, event_id=%s",
            user_id,
            event_type.value,
            log_entry.event_id,
        )
        return log_entry

    @staticmethod
    async def get_user_audit_logs(user_id: str, limit: int = 50) -> list[TrustAuditLog]:
        """Fetch audit log history for a specific user."""
        return await TrustAuditLogRepository.get_audit_logs_by_user(user_id, limit=limit)

    @staticmethod
    async def list_all_audit_logs(skip: int = 0, limit: int = 100) -> list[TrustAuditLog]:
        """List all audit logs across the platform."""
        return await TrustAuditLogRepository.list_audit_logs(skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# Policy Management Service
# ---------------------------------------------------------------------------

class PolicyService:
    """Service for managing safety policies and thresholds."""

    @staticmethod
    async def get_policy(policy_key: str) -> TrustPolicy | None:
        """Retrieve policy by policy key."""
        return await TrustPolicyRepository.get_by_key(policy_key)

    @staticmethod
    async def list_active_policies() -> list[TrustPolicy]:
        """List all active policies."""
        return await TrustPolicyRepository.list_active_policies()

    @staticmethod
    async def create_policy(policy_in: TrustPolicyCreate, actor: dict[str, Any]) -> TrustPolicy:
        """Create a new policy and record an audit log."""
        policy = await TrustPolicyRepository.create_policy(policy_in.model_dump())
        await AuditService.log_event(
            user_id="system",
            event_type=AuditEventType.POLICY_CHANGES,
            description=f"Created policy '{policy.name}' ({policy.policy_key})",
            actor=actor,
            metadata={"policy_key": policy.policy_key, "version": policy.version},
        )
        return policy

    @staticmethod
    async def update_policy(
        policy_key: str,
        policy_in: TrustPolicyUpdate,
        actor: dict[str, Any],
    ) -> TrustPolicy | None:
        """Update an existing policy and record an audit log."""
        updates = policy_in.model_dump(exclude_unset=True)
        if not updates:
            return await PolicyService.get_policy(policy_key)

        updated_policy = await TrustPolicyRepository.update_policy(policy_key, updates)
        if updated_policy:
            await AuditService.log_event(
                user_id="system",
                event_type=AuditEventType.POLICY_CHANGES,
                description=f"Updated policy '{updated_policy.name}' ({policy_key})",
                actor=actor,
                metadata={"policy_key": policy_key, "version": updated_policy.version, "updates": list(updates.keys())},
            )
        return updated_policy


# ---------------------------------------------------------------------------
# Risk Service
# ---------------------------------------------------------------------------

class RiskService:
    """Service for managing risk events and evaluating risk levels."""

    @staticmethod
    async def record_risk_event(
        user_id: str,
        event_type: RiskEventType,
        severity: RiskLevel,
        description: str,
        source: str = "system",
        metadata: dict[str, Any] | None = None,
        actor: dict[str, Any] | None = None,
    ) -> RiskEvent:
        """Record a new risk event and trigger risk level evaluation."""
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "source": source,
            "metadata": metadata or {},
        }
        risk_event = await RiskEventRepository.create_risk_event(event_data)
        logger.warning(
            "Risk event recorded: user_id=%s, type=%s, severity=%s",
            user_id,
            event_type.value,
            severity.value,
        )

        # Audit log integration
        await AuditService.log_event(
            user_id=user_id,
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Risk event [{event_type.value}]: {description}",
            actor=actor or {"id": "system", "role": "system"},
            metadata={"risk_event_id": risk_event.event_id, "severity": severity.value},
        )

        # Recalculate user risk level
        await RiskService.evaluate_user_risk_level(user_id)
        return risk_event

    @staticmethod
    async def get_user_risk_events(user_id: str, limit: int = 50) -> list[RiskEvent]:
        """Fetch risk events for a specific user."""
        return await RiskEventRepository.get_risk_events_by_user(user_id, limit=limit)

    @staticmethod
    async def list_all_risk_events(skip: int = 0, limit: int = 100) -> list[RiskEvent]:
        """List all risk events."""
        return await RiskEventRepository.list_all_risk_events(skip=skip, limit=limit)

    @staticmethod
    async def evaluate_user_risk_level(user_id: str) -> RiskLevel:
        """
        Evaluate and update user risk level based on recorded risk events.
        """
        profile = await TrustProfileRepository.get_by_user_id(user_id)
        if not profile:
            return RiskLevel.LOW

        events = await RiskEventRepository.get_risk_events_by_user(user_id, limit=20)
        if not events:
            new_risk = RiskLevel.LOW
        else:
            severities = [e.severity for e in events]
            if RiskLevel.CRITICAL in severities:
                new_risk = RiskLevel.CRITICAL
            elif severities.count(RiskLevel.HIGH) >= 2 or RiskLevel.HIGH in severities:
                new_risk = RiskLevel.HIGH
            elif severities.count(RiskLevel.MEDIUM) >= 3 or RiskLevel.MEDIUM in severities:
                new_risk = RiskLevel.MEDIUM
            else:
                new_risk = RiskLevel.LOW

        if profile.risk_level != new_risk:
            await TrustProfileRepository.update_profile(user_id, {"risk_level": new_risk})

        return new_risk


# ---------------------------------------------------------------------------
# Safety Event Manager
# ---------------------------------------------------------------------------

class SafetyEventManager:
    """Manages safety flags and verification history records."""

    @staticmethod
    async def raise_safety_flag(
        user_id: str,
        flag_type: str,
        reason: str,
        severity: RiskLevel = RiskLevel.MEDIUM,
        actor: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SafetyFlag:
        """Create a new active safety flag for a user."""
        flag_data = {
            "user_id": user_id,
            "flag_type": flag_type,
            "reason": reason,
            "severity": severity,
            "status": "active",
            "metadata": metadata or {},
        }
        flag = await SafetyFlagRepository.create_flag(flag_data)

        # Update user profile safety flags
        profile = await TrustProfileRepository.get_by_user_id(user_id)
        if profile:
            current_flags = set(profile.safety_flags)
            current_flags.add(flag.flag_id)
            await TrustProfileRepository.update_profile(user_id, {
                "safety_flags": list(current_flags),
                "review_status": ReviewStatus.FLAGGED if profile.review_status == ReviewStatus.CLEAR else profile.review_status,
            })

        await AuditService.log_event(
            user_id=user_id,
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Safety flag raised: {flag_type} - {reason}",
            actor=actor or {"id": "system", "role": "system"},
            metadata={"flag_id": flag.flag_id, "severity": severity.value},
        )
        return flag

    @staticmethod
    async def resolve_safety_flag(
        flag_id: str,
        actor: dict[str, Any],
    ) -> SafetyFlag | None:
        """Resolve an active safety flag."""
        flag = await SafetyFlagRepository.resolve_flag(flag_id)
        if flag:
            profile = await TrustProfileRepository.get_by_user_id(flag.user_id)
            if profile and flag_id in profile.safety_flags:
                updated_flags = [f for f in profile.safety_flags if f != flag_id]
                new_review_status = ReviewStatus.CLEAR if not updated_flags else profile.review_status
                await TrustProfileRepository.update_profile(flag.user_id, {
                    "safety_flags": updated_flags,
                    "review_status": new_review_status,
                })

            await AuditService.log_event(
                user_id=flag.user_id,
                event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
                description=f"Safety flag resolved: {flag.flag_id}",
                actor=actor,
                metadata={"flag_id": flag_id},
            )
        return flag

    @staticmethod
    async def record_verification_history(
        user_id: str,
        verification_type: str,
        status: str,
        details: dict[str, Any] | None = None,
        actor: dict[str, Any] | None = None,
    ) -> VerificationHistory:
        """Record verification history event and update profile state."""
        rec = await VerificationHistoryRepository.add_record({
            "user_id": user_id,
            "verification_type": verification_type,
            "status": status,
            "details": details or {},
        })

        await AuditService.log_event(
            user_id=user_id,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Verification [{verification_type}] status updated to '{status}'",
            actor=actor or {"id": "system", "role": "system"},
            metadata={"history_id": rec.history_id, "verification_type": verification_type, "status": status},
        )
        return rec


# ---------------------------------------------------------------------------
# Trust Service
# ---------------------------------------------------------------------------

class TrustService:
    """Primary orchestrator service for user Trust Profiles & Statuses."""

    @staticmethod
    async def get_or_create_profile(user_id: str | Any, role: UserRole) -> TrustProfile:
        """Retrieve user trust profile or initialize a new standard profile."""
        user_id_str = str(user_id)
        profile = await TrustProfileRepository.get_by_user_id(user_id_str)
        if not profile:
            thresholds = await ConfigService.get_score_thresholds()
            initial_score = 75.0
            initial_level = TrustScoreEngine.calculate_trust_level(initial_score, thresholds)
            profile = await TrustProfileRepository.create_profile(
                user_id=user_id_str,
                role=role,
                trust_score=initial_score,
                trust_level=initial_level,
                verification_status=TrustVerificationStatus.UNVERIFIED,
                risk_level=RiskLevel.LOW,
                review_status=ReviewStatus.CLEAR,
            )
            await AuditService.log_event(
                user_id=user_id_str,
                event_type=AuditEventType.REGISTRATION,
                description="Initial trust profile created.",
                actor={"id": user_id_str, "role": role.value},
            )
        return profile

    @staticmethod
    async def get_trust_status(user_id: str | Any, role: UserRole) -> TrustStatusRead:
        """Get high-level trust status summary for a user."""
        user_id_str = str(user_id)
        profile = await TrustService.get_or_create_profile(user_id_str, role)
        active_flags = await SafetyFlagRepository.get_active_flags_for_user(user_id_str)

        is_restricted = (
            profile.trust_level == TrustLevel.RESTRICTED
            or profile.risk_level == RiskLevel.CRITICAL
            or profile.review_status == ReviewStatus.RESTRICTED
        )

        return TrustStatusRead(
            user_id=profile.user_id,
            role=profile.role,
            trust_score=profile.trust_score,
            trust_level=profile.trust_level,
            risk_level=profile.risk_level,
            review_status=profile.review_status,
            verification_status=profile.verification_status,
            active_flags_count=len(active_flags),
            is_restricted=is_restricted,
            last_updated=profile.updated_at,
        )

    @staticmethod
    async def update_trust_score(
        user_id: str,
        new_score: float,
        actor: dict[str, Any],
        reason: str,
    ) -> TrustProfile:
        """Update user trust score and recalculate trust level."""
        profile = await TrustProfileRepository.get_by_user_id(user_id)
        if not profile:
            raise ValueError(f"Trust profile for user {user_id} not found.")

        old_score = profile.trust_score
        old_level = profile.trust_level

        thresholds = await ConfigService.get_score_thresholds()
        new_level = TrustScoreEngine.calculate_trust_level(new_score, thresholds)

        updated_profile = await TrustProfileRepository.update_profile(
            user_id,
            {
                "trust_score": new_score,
                "trust_level": new_level,
            },
        )

        await AuditService.log_event(
            user_id=user_id,
            event_type=AuditEventType.TRUST_SCORE_CHANGES,
            description=f"Trust score updated from {old_score} to {new_score} ({reason})",
            actor=actor,
            metadata={
                "old_score": old_score,
                "new_score": new_score,
                "old_level": old_level.value,
                "new_level": new_level.value,
            },
        )
        return updated_profile

    @staticmethod
    async def update_profile(
        user_id: str,
        update_in: TrustProfileUpdate,
        actor: dict[str, Any],
    ) -> TrustProfile | None:
        """Update profile fields and log changes."""
        updates = update_in.model_dump(exclude_unset=True)
        if not updates:
            return await TrustProfileRepository.get_by_user_id(user_id)

        # Recalculate level if score is being updated
        if "trust_score" in updates:
            thresholds = await ConfigService.get_score_thresholds()
            updates["trust_level"] = TrustScoreEngine.calculate_trust_level(
                updates["trust_score"], thresholds
            )

        updated = await TrustProfileRepository.update_profile(user_id, updates)
        if updated:
            await AuditService.log_event(
                user_id=user_id,
                event_type=AuditEventType.PROFILE_UPDATES,
                description=f"Trust profile updated fields: {list(updates.keys())}",
                actor=actor,
                metadata={"updated_fields": list(updates.keys())},
            )
        return updated

    @staticmethod
    async def review_user_trust(
        target_user_id: str,
        action: str,
        reason: str,
        reviewer: dict[str, Any],
        new_risk_level: RiskLevel | None = None,
        notes: str | None = None,
    ) -> TrustReviewResponse:
        """Process administrative trust review on a user profile."""
        profile = await TrustProfileRepository.get_by_user_id(target_user_id)
        if not profile:
            raise ValueError(f"User {target_user_id} trust profile does not exist.")

        prev_review_status = profile.review_status
        prev_risk_level = profile.risk_level

        # Action mapping logic
        act_lower = action.lower()
        if act_lower in ["flag", "flagged"]:
            target_review_status = ReviewStatus.FLAGGED
        elif act_lower in ["restrict", "restricted"]:
            target_review_status = ReviewStatus.RESTRICTED
        elif act_lower in ["under_review", "review"]:
            target_review_status = ReviewStatus.UNDER_REVIEW
        elif act_lower in ["clear", "cleared"]:
            target_review_status = ReviewStatus.CLEAR
        else:
            target_review_status = ReviewStatus(action)

        updates: dict[str, Any] = {"review_status": target_review_status}
        if new_risk_level:
            updates["risk_level"] = new_risk_level

        await TrustProfileRepository.update_profile(target_user_id, updates)

        await AuditService.log_event(
            user_id=target_user_id,
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Manual Trust Review [{action}]: {reason}",
            actor=reviewer,
            metadata={
                "action": action,
                "reason": reason,
                "notes": notes,
                "previous_review_status": prev_review_status.value,
                "new_review_status": target_review_status.value,
            },
        )

        return TrustReviewResponse(
            target_user_id=target_user_id,
            action=action,
            previous_review_status=prev_review_status,
            new_review_status=target_review_status,
            previous_risk_level=prev_risk_level,
            new_risk_level=new_risk_level or prev_risk_level,
            reviewed_at=datetime.now(timezone.utc),
            reviewer_id=reviewer.get("id", "admin"),
        )
