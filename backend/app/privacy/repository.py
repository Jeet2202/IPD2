"""
Repositories for Privacy, Compliance & Data Protection following Clean Architecture & Repository Pattern.
"""

from datetime import datetime, timezone
from typing import Any

from app.privacy.models import (
    ComplianceRecord,
    DataExport,
    PrivacyRequest,
    RetentionPolicy,
    UserConsent,
)
from app.privacy.schemas import (
    ConsentType,
    PrivacyRequestStatus,
    PrivacyRequestType,
)


class UserConsentRepository:
    """Repository for managing UserConsent database operations."""

    @staticmethod
    async def get_consent(user_id: str, consent_type: ConsentType) -> UserConsent | None:
        """Fetch consent setting for a user and consent category."""
        return await UserConsent.find_one(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == consent_type,
        )

    @staticmethod
    async def list_user_consents(user_id: str) -> list[UserConsent]:
        """List all active consents for a user."""
        return (
            await UserConsent.find(UserConsent.user_id == user_id)
            .sort("-updated_at")
            .to_list()
        )

    @staticmethod
    async def upsert_consent(
        user_id: str,
        consent_type: ConsentType,
        is_granted: bool,
        version: str = "1.0",
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> UserConsent:
        """Update or insert a consent choice."""
        existing = await UserConsentRepository.get_consent(user_id, consent_type)
        now = datetime.now(timezone.utc)

        if existing:
            existing.is_granted = is_granted
            existing.policy_version = version
            existing.updated_at = now
            if ip_address:
                existing.ip_address = ip_address
            if user_agent:
                existing.user_agent = user_agent
            await existing.save()
            return existing

        consent = UserConsent(
            user_id=user_id,
            consent_type=consent_type,
            is_granted=is_granted,
            policy_version=version,
            ip_address=ip_address,
            user_agent=user_agent,
            updated_at=now,
        )
        await consent.insert()
        return consent


class PrivacyRequestRepository:
    """Repository for managing PrivacyRequest database operations."""

    @staticmethod
    async def get_by_id(request_id: str) -> PrivacyRequest | None:
        """Fetch request by request_id."""
        return await PrivacyRequest.find_one(PrivacyRequest.request_id == request_id)

    @staticmethod
    async def get_active_deletion_request(user_id: str) -> PrivacyRequest | None:
        """Fetch active pending account deletion request for user."""
        return await PrivacyRequest.find_one(
            PrivacyRequest.user_id == user_id,
            PrivacyRequest.request_type == PrivacyRequestType.ACCOUNT_DELETION,
            PrivacyRequest.status == PrivacyRequestStatus.PENDING_GRACE_PERIOD,
        )

    @staticmethod
    async def create_request(data: dict[str, Any]) -> PrivacyRequest:
        """Create a new privacy request."""
        req = PrivacyRequest(**data)
        await req.insert()
        return req

    @staticmethod
    async def list_by_user(user_id: str) -> list[PrivacyRequest]:
        """List privacy requests for a user."""
        return (
            await PrivacyRequest.find(PrivacyRequest.user_id == user_id)
            .sort("-created_at")
            .to_list()
        )

    @staticmethod
    async def update_request(request_id: str, updates: dict[str, Any]) -> PrivacyRequest | None:
        """Update privacy request fields."""
        req = await PrivacyRequestRepository.get_by_id(request_id)
        if not req:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(req, key):
                setattr(req, key, value)

        await req.save()
        return req


class DataExportRepository:
    """Repository for managing DataExport database operations."""

    @staticmethod
    async def create_export(data: dict[str, Any]) -> DataExport:
        """Save new data export record."""
        export_doc = DataExport(**data)
        await export_doc.insert()
        return export_doc

    @staticmethod
    async def list_by_user(user_id: str) -> list[DataExport]:
        """List data exports for a user."""
        return (
            await DataExport.find(DataExport.user_id == user_id)
            .sort("-created_at")
            .to_list()
        )


class RetentionPolicyRepository:
    """Repository for managing RetentionPolicy database operations."""

    @staticmethod
    async def get_by_key(policy_key: str) -> RetentionPolicy | None:
        """Fetch policy by key."""
        return await RetentionPolicy.find_one(RetentionPolicy.policy_key == policy_key)

    @staticmethod
    async def list_active_policies() -> list[RetentionPolicy]:
        """Fetch all active retention policies."""
        return await RetentionPolicy.find(RetentionPolicy.is_active == True).to_list()

    @staticmethod
    async def create_policy(data: dict[str, Any]) -> RetentionPolicy:
        """Create a retention policy."""
        policy = RetentionPolicy(**data)
        await policy.insert()
        return policy


class ComplianceRecordRepository:
    """Repository for managing ComplianceRecord database operations."""

    @staticmethod
    async def create_record(data: dict[str, Any]) -> ComplianceRecord:
        """Record an immutable compliance audit event."""
        record = ComplianceRecord(**data)
        await record.insert()
        return record

    @staticmethod
    async def list_by_user(user_id: str) -> list[ComplianceRecord]:
        """List compliance audit records for a user."""
        return (
            await ComplianceRecord.find(ComplianceRecord.user_id == user_id)
            .sort("-created_at")
            .to_list()
        )
