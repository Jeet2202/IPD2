"""
Repositories for Fraud Detection & Abuse Prevention following Clean Architecture & Repository Pattern.
"""

from datetime import datetime, timezone
from typing import Any

from app.fraud.models import (
    AbuseReport,
    FraudAlert,
    FraudEvent,
    FraudRule,
)
from app.fraud.schemas import (
    AlertPriority,
    AlertStatus,
    FraudRuleType,
)
from app.trust.schemas import RiskLevel


class FraudEventRepository:
    """Repository for managing FraudEvent database operations."""

    @staticmethod
    async def create_event(data: dict[str, Any]) -> FraudEvent:
        """Create and save a new FraudEvent document."""
        event = FraudEvent(**data)
        await event.insert()
        return event

    @staticmethod
    async def get_by_user(user_id: str, limit: int = 50) -> list[FraudEvent]:
        """Fetch recent fraud events for a user."""
        return (
            await FraudEvent.find(FraudEvent.user_id == user_id)
            .sort("-created_at")
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def list_all(
        skip: int = 0,
        limit: int = 100,
        risk_level: RiskLevel | None = None,
    ) -> list[FraudEvent]:
        """List fraud events with optional risk level filter."""
        query: dict[str, Any] = {}
        if risk_level:
            query["risk_level"] = risk_level
        return (
            await FraudEvent.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_by_risk_level(risk_level: RiskLevel) -> int:
        """Count fraud events matching a specific risk level."""
        return await FraudEvent.find(FraudEvent.risk_level == risk_level).count()

    @staticmethod
    async def total_count() -> int:
        """Count total fraud analysis events."""
        return await FraudEvent.find_all().count()


class FraudRuleRepository:
    """Repository for managing FraudRule database operations."""

    @staticmethod
    async def get_by_key(rule_key: str) -> FraudRule | None:
        """Fetch fraud rule by unique key."""
        return await FraudRule.find_one(FraudRule.rule_key == rule_key)

    @staticmethod
    async def list_active_rules() -> list[FraudRule]:
        """Fetch all active fraud rules."""
        return await FraudRule.find(FraudRule.is_active == True).to_list()

    @staticmethod
    async def list_all_rules() -> list[FraudRule]:
        """List all rules (active and inactive)."""
        return await FraudRule.find_all().to_list()

    @staticmethod
    async def create_rule(data: dict[str, Any]) -> FraudRule:
        """Create a new FraudRule."""
        rule = FraudRule(**data)
        await rule.insert()
        return rule

    @staticmethod
    async def update_rule(rule_key: str, updates: dict[str, Any]) -> FraudRule | None:
        """Update an existing FraudRule."""
        rule = await FraudRuleRepository.get_by_key(rule_key)
        if not rule:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        if "version" not in updates:
            updates["version"] = rule.version + 1

        for key, value in updates.items():
            if value is not None and hasattr(rule, key):
                setattr(rule, key, value)

        await rule.save()
        return rule


class FraudAlertRepository:
    """Repository for managing FraudAlert database operations."""

    @staticmethod
    async def get_by_id(alert_id: str) -> FraudAlert | None:
        """Fetch alert by alert ID."""
        return await FraudAlert.find_one(FraudAlert.alert_id == alert_id)

    @staticmethod
    async def create_alert(data: dict[str, Any]) -> FraudAlert:
        """Create and save a new FraudAlert."""
        alert = FraudAlert(**data)
        await alert.insert()
        return alert

    @staticmethod
    async def list_alerts(
        user_id: str | None = None,
        status: AlertStatus | None = None,
        priority: AlertPriority | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[FraudAlert]:
        """Query fraud alerts with optional filtering."""
        query: dict[str, Any] = {}
        if user_id:
            query["user_id"] = user_id
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority

        return (
            await FraudAlert.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def resolve_alert(
        alert_id: str,
        action: str,
        resolution_notes: str,
        reviewer_id: str | None = None,
    ) -> FraudAlert | None:
        """Resolve or dismiss an alert."""
        alert = await FraudAlertRepository.get_by_id(alert_id)
        if not alert:
            return None

        target_status = AlertStatus.RESOLVED if action.lower() == "resolved" else AlertStatus.DISMISSED
        alert.status = target_status
        alert.resolution_notes = resolution_notes
        alert.resolved_at = datetime.now(timezone.utc)
        if reviewer_id:
            alert.assigned_reviewer_id = reviewer_id

        await alert.save()
        return alert

    @staticmethod
    async def count_by_status(status: AlertStatus) -> int:
        """Count alerts matching a specific status."""
        return await FraudAlert.find(FraudAlert.status == status).count()


class AbuseReportRepository:
    """Repository for managing AbuseReport database operations."""

    @staticmethod
    async def get_by_id(report_id: str) -> AbuseReport | None:
        """Fetch report by report ID."""
        return await AbuseReport.find_one(AbuseReport.report_id == report_id)

    @staticmethod
    async def create_report(data: dict[str, Any]) -> AbuseReport:
        """Create and save a new AbuseReport."""
        report = AbuseReport(**data)
        await report.insert()
        return report

    @staticmethod
    async def list_by_target(target_user_id: str) -> list[AbuseReport]:
        """List reports targeting a specific user."""
        return (
            await AbuseReport.find(AbuseReport.target_user_id == target_user_id)
            .sort("-created_at")
            .to_list()
        )

    @staticmethod
    async def list_all(skip: int = 0, limit: int = 50) -> list[AbuseReport]:
        """List all abuse reports for admin oversight."""
        return (
            await AbuseReport.find_all()
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def resolve_report(
        report_id: str,
        action: str,
        resolution_notes: str,
    ) -> AbuseReport | None:
        """Resolve or dismiss an abuse report."""
        report = await AbuseReportRepository.get_by_id(report_id)
        if not report:
            return None

        target_status = "resolved" if action.lower() == "resolved" else "dismissed"
        report.status = target_status
        report.resolution_notes = resolution_notes
        report.resolved_at = datetime.now(timezone.utc)
        await report.save()
        return report

    @staticmethod
    async def count_pending() -> int:
        """Count pending abuse reports."""
        return await AbuseReport.find(AbuseReport.status == "pending").count()
