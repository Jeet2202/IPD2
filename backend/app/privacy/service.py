"""
Domain services for Consent Management, Data Access, JSON/CSV Exports, Grace Period Deletion, and Retention Policies.
"""

from datetime import datetime, timedelta, timezone
import csv
import io
import json
import logging
from typing import Any

from app.address.models import Address
from app.auth.models import User
from app.booking.models import Booking
from app.core.exceptions import BadRequestException, NotFoundException
from app.customer.models import CustomerProfile
from app.privacy.models import (
    ComplianceRecord,
    DataExport,
    PrivacyRequest,
    RetentionPolicy,
    UserConsent,
)
from app.privacy.repository import (
    ComplianceRecordRepository,
    DataExportRepository,
    PrivacyRequestRepository,
    RetentionPolicyRepository,
    UserConsentRepository,
)
from app.privacy.schemas import (
    ConsentItem,
    ConsentRead,
    ConsentType,
    ConsentUpdateRequest,
    DataExportRead,
    ExportFormat,
    PrivacyProfileRead,
    PrivacyRequestRead,
    PrivacyRequestStatus,
    PrivacyRequestType,
)
from app.review.models import Review
from app.trust.schemas import AuditEventType
from app.trust.service import AuditService
from app.worker.models import WorkerProfile

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default Retention Policies Catalog Definitions
# ---------------------------------------------------------------------------

DEFAULT_RETENTION_POLICIES = [
    {
        "policy_key": "audit_logs",
        "category_name": "Audit & Compliance Logs",
        "retention_days": 365,
        "description": "Retention window for security and compliance audit logs.",
    },
    {
        "policy_key": "reports",
        "category_name": "Platform Reports & Moderation",
        "retention_days": 180,
        "description": "Retention window for closed platform violation reports.",
    },
    {
        "policy_key": "verification_records",
        "category_name": "Worker Verification Records",
        "retention_days": 730,
        "description": "Retention window for identity and qualification documents.",
    },
    {
        "policy_key": "notifications",
        "category_name": "User Notifications",
        "retention_days": 90,
        "description": "Retention window for expired in-app notification logs.",
    },
    {
        "policy_key": "search_history",
        "category_name": "Marketplace Search History",
        "retention_days": 30,
        "description": "Retention window for anonymous user search logs.",
    },
    {
        "policy_key": "ai_conversations",
        "category_name": "AI Platform Interaction Logs",
        "retention_days": 60,
        "description": "Retention window for AI assistant conversation logs.",
    },
]


# ---------------------------------------------------------------------------
# Compliance Service
# ---------------------------------------------------------------------------

class ComplianceService:
    """Manages compliance records and audit trail logs."""

    @staticmethod
    async def log_compliance_event(
        user_id: str,
        event_type: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> ComplianceRecord:
        """Log immutable compliance record in DB."""
        user_id_str = str(user_id)
        record = await ComplianceRecordRepository.create_record({
            "user_id": user_id_str,
            "event_type": event_type,
            "description": description,
            "metadata": metadata or {},
        })

        await AuditService.log_event(
            user_id=user_id_str,
            event_type=AuditEventType.POLICY_CHANGES,
            description=f"Compliance Event [{event_type}]: {description}",
            actor={"id": user_id_str, "role": "user"},
            metadata=metadata or {},
        )
        return record


# ---------------------------------------------------------------------------
# Consent Service
# ---------------------------------------------------------------------------

class ConsentService:
    """Manages user consents and policy acceptance history."""

    @staticmethod
    async def initialize_default_consents(user_id: str) -> list[UserConsent]:
        """Ensure all default consent categories exist for user."""
        user_id_str = str(user_id)
        consents: list[UserConsent] = []
        for ct in ConsentType:
            existing = await UserConsentRepository.get_consent(user_id_str, ct)
            if not existing:
                # Default mandatory policy consents to True, marketing to False
                granted = ct in [ConsentType.TERMS_AND_CONDITIONS, ConsentType.PRIVACY_POLICY, ConsentType.NOTIFICATION, ConsentType.AI_FEATURES]
                c = await UserConsentRepository.upsert_consent(user_id_str, ct, is_granted=granted, version="1.0")
                consents.append(c)
            else:
                consents.append(existing)
        return consents

    @staticmethod
    async def get_user_consents(user_id: str) -> list[UserConsent]:
        """Fetch all consent settings for user."""
        user_id_str = str(user_id)
        consents = await UserConsentRepository.list_user_consents(user_id_str)
        if not consents:
            return await ConsentService.initialize_default_consents(user_id_str)
        return consents

    @staticmethod
    async def update_user_consents(
        user_id: str,
        req: ConsentUpdateRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> list[UserConsent]:
        """Update multiple user consent settings."""
        user_id_str = str(user_id)
        updated_list: list[UserConsent] = []

        for item in req.consents:
            c = await UserConsentRepository.upsert_consent(
                user_id=user_id_str,
                consent_type=item.consent_type,
                is_granted=item.is_granted,
                version=item.policy_version,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            updated_list.append(c)

        await ComplianceService.log_compliance_event(
            user_id=user_id_str,
            event_type="consent_update",
            description=f"User updated {len(req.consents)} consent preference(s).",
            metadata={"updated_types": [item.consent_type.value for item in req.consents]},
        )
        return updated_list


# ---------------------------------------------------------------------------
# Data Access & Export Service
# ---------------------------------------------------------------------------

class DataAccessService:
    """Aggregates user personal profile data for access and export."""

    @staticmethod
    async def get_user_privacy_profile(user_id: str) -> PrivacyProfileRead:
        """Fetch user personal privacy overview."""
        user_id_str = str(user_id)
        user = await User.get(user_id_str)
        if not user:
            raise NotFoundException(f"User '{user_id}' not found.")

        consents = await ConsentService.get_user_consents(user_id_str)
        active_deletion = await PrivacyRequestRepository.get_active_deletion_request(user_id_str)
        user_requests = await PrivacyRequestRepository.list_by_user(user_id_str)

        deletion_status = "pending_deletion" if active_deletion else "active"
        scheduled_del_at = active_deletion.scheduled_deletion_at if active_deletion else None

        return PrivacyProfileRead(
            user_id=user_id_str,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            deletion_status=deletion_status,
            scheduled_deletion_at=scheduled_del_at,
            consents=[ConsentRead.model_validate(c) for c in consents],
            active_requests_count=len(user_requests),
        )

    @staticmethod
    async def get_aggregated_personal_data(user_id: str) -> dict[str, Any]:
        """Aggregate personal profile data belonging to the authenticated user."""
        user_id_str = str(user_id)
        user = await User.get(user_id_str)
        if not user:
            raise NotFoundException(f"User '{user_id}' not found.")

        user_data = {
            "user_id": user_id_str,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if hasattr(user, "created_at") and user.created_at else None,
        }

        # Customer / Worker profile
        from beanie import PydanticObjectId
        try:
            obj_id = PydanticObjectId(user_id_str)
            customer_prof = await CustomerProfile.find_one(CustomerProfile.user_id == obj_id)
            worker_prof = await WorkerProfile.find_one(WorkerProfile.user_id == obj_id)
        except Exception:
            customer_prof = None
            worker_prof = None

        addresses = []
        try:
            addresses = await Address.find(Address.customer_id == obj_id, Address.is_deleted == False).to_list()
        except Exception:
            pass
        consents = await ConsentService.get_user_consents(user_id_str)
        bookings = await Booking.find({"$or": [{"customer_id": user_id_str}, {"worker_id": user_id_str}]}).to_list()
        reviews = await Review.find({"$or": [{"reviewer_id": user_id_str}, {"target_id": user_id_str}]}).to_list()

        return {
            "personal_info": user_data,
            "customer_profile": customer_prof.model_dump(mode="json") if customer_prof else None,
            "worker_profile": worker_prof.model_dump(mode="json") if worker_prof else None,
            "addresses": [a.model_dump(mode="json") for a in addresses],
            "consents": [c.model_dump(mode="json") for c in consents],
            "booking_history_count": len(bookings),
            "review_history_count": len(reviews),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }


class DataExportService:
    """Generates downloadable JSON or CSV data exports."""

    @staticmethod
    async def generate_data_export(user_id: str, format_type: ExportFormat) -> DataExportRead:
        """Generate formatted personal data export."""
        user_id_str = str(user_id)
        aggregated_data = await DataAccessService.get_aggregated_personal_data(user_id_str)

        if format_type == ExportFormat.CSV:
            # Flatten top-level attributes to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Field", "Value"])
            p_info = aggregated_data.get("personal_info", {})
            for k, v in p_info.items():
                writer.writerow([k, str(v)])
            writer.writerow(["booking_history_count", aggregated_data.get("booking_history_count", 0)])
            writer.writerow(["review_history_count", aggregated_data.get("review_history_count", 0)])
            file_content = output.getvalue()
        else:
            file_content = json.dumps(aggregated_data, indent=2, default=str)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)

        export_doc = await DataExportRepository.create_export({
            "user_id": user_id_str,
            "format": format_type,
            "export_data_summary": {
                "user_id": user_id_str,
                "record_counts": {
                    "addresses": len(aggregated_data.get("addresses", [])),
                    "consents": len(aggregated_data.get("consents", [])),
                    "bookings": aggregated_data.get("booking_history_count", 0),
                },
            },
            "file_content": file_content,
            "status": "ready",
            "created_at": now,
            "expires_at": expires_at,
        })

        await ComplianceService.log_compliance_event(
            user_id=user_id_str,
            event_type="data_export",
            description=f"Generated personal data export in {format_type.value.upper()} format.",
            metadata={"export_id": export_doc.export_id, "format": format_type.value},
        )
        return DataExportRead.model_validate(export_doc)


# ---------------------------------------------------------------------------
# Data Retention Service
# ---------------------------------------------------------------------------

class DataRetentionService:
    """Manages configurable data retention policies."""

    @staticmethod
    async def initialize_default_policies() -> None:
        """Ensure default data retention policies exist in DB."""
        for p_def in DEFAULT_RETENTION_POLICIES:
            existing = await RetentionPolicyRepository.get_by_key(p_def["policy_key"])
            if not existing:
                await RetentionPolicyRepository.create_policy(p_def)
                logger.info("Initialized retention policy in DB: %s", p_def["policy_key"])

    @staticmethod
    async def list_retention_policies() -> list[RetentionPolicy]:
        """Fetch all active data retention policies."""
        return await RetentionPolicyRepository.list_active_policies()


# ---------------------------------------------------------------------------
# Privacy Service
# ---------------------------------------------------------------------------

class PrivacyService:
    """Orchestrates account deletion grace period and privacy request workflows."""

    @staticmethod
    async def request_account_deletion(
        user_id: str,
        reason: str | None = None,
    ) -> PrivacyRequest:
        """Submit account deletion request with 30-day grace period."""
        user_id_str = str(user_id)

        # Check existing active request
        existing = await PrivacyRequestRepository.get_active_deletion_request(user_id_str)
        if existing:
            return existing

        now = datetime.now(timezone.utc)
        scheduled_del_at = now + timedelta(days=30)

        req = await PrivacyRequestRepository.create_request({
            "user_id": user_id_str,
            "request_type": PrivacyRequestType.ACCOUNT_DELETION,
            "status": PrivacyRequestStatus.PENDING_GRACE_PERIOD,
            "grace_period_days": 30,
            "scheduled_deletion_at": scheduled_del_at,
            "completion_notes": f"Account deletion requested. Grace period ends on {scheduled_del_at.isoformat()}. Reason: {reason or 'User requested'}",
        })

        await ComplianceService.log_compliance_event(
            user_id=user_id_str,
            event_type="account_deletion_requested",
            description="Account deletion requested with 30-day grace period.",
            metadata={"request_id": req.request_id, "scheduled_deletion_at": scheduled_del_at.isoformat()},
        )
        return req

    @staticmethod
    async def cancel_account_deletion(user_id: str) -> PrivacyRequest:
        """Cancel pending account deletion request during grace period."""
        user_id_str = str(user_id)
        existing = await PrivacyRequestRepository.get_active_deletion_request(user_id_str)

        if not existing:
            raise NotFoundException("No pending account deletion request found to cancel.")

        now = datetime.now(timezone.utc)
        updated = await PrivacyRequestRepository.update_request(
            existing.request_id,
            {
                "status": PrivacyRequestStatus.CANCELLED,
                "completion_notes": "Account deletion request cancelled by user during grace period.",
                "completed_at": now,
            },
        )

        await ComplianceService.log_compliance_event(
            user_id=user_id_str,
            event_type="account_deletion_cancelled",
            description="Account deletion request cancelled during grace period.",
            metadata={"request_id": existing.request_id},
        )
        return updated

    @staticmethod
    async def get_user_privacy_requests(user_id: str) -> list[PrivacyRequest]:
        """Fetch privacy requests filed by user."""
        return await PrivacyRequestRepository.list_by_user(str(user_id))
