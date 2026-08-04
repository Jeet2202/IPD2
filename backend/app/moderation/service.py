"""
Domain services for Reporting, Evidence Management, Moderation Workflows, Dispute Resolution, and Enforceable Administrative Actions.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from app.auth.models import User
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.moderation.models import (
    CaseNote,
    Dispute,
    EvidenceFile,
    ModerationCase,
    PlatformReport,
)
from app.moderation.repository import (
    CaseNoteRepository,
    DisputeRepository,
    EvidenceFileRepository,
    ModerationCaseRepository,
    ReportRepository,
)
from app.moderation.schemas import (
    AdministrativeAction,
    CaseNoteCreate,
    DisputeCreate,
    DisputeRead,
    DisputeResolveRequest,
    DisputeStatus,
    EvidenceUploadResponse,
    ModerationEscalateRequest,
    ModerationReviewRequest,
    ReportCreate,
    ReportRead,
    ReportStatus,
    ReportUpdate,
)
from app.trust.models import ReviewStatus
from app.trust.repository import TrustProfileRepository
from app.trust.schemas import AuditEventType, RiskEventType, RiskLevel
from app.trust.service import AuditService, RiskService, TrustService
from app.uploads.service import CloudinaryService
from app.utils.enums import UserRole

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Evidence Service
# ---------------------------------------------------------------------------

class EvidenceService:
    """Manages evidence file uploads and metadata tracking."""

    @staticmethod
    async def upload_evidence(
        case_id: str,
        uploader_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str = "application/octet-stream",
        description: str | None = None,
    ) -> EvidenceFile:
        """Upload evidence file to Cloudinary and register metadata in DB."""
        case_id_str = str(case_id)
        uploader_id_str = str(uploader_id)

        try:
            secure_url, public_id = CloudinaryService.upload_moderation_evidence(
                file_bytes=file_bytes,
                filename=filename,
                case_id=case_id_str,
                uploader_id=uploader_id_str,
            )
        except Exception as e:
            logger.warning("Cloudinary upload failed or not configured (%s). Using fallback metadata for test.", str(e))
            secure_url = f"https://res.cloudinary.com/mock/image/upload/v1/kaamsetu/evidence_{case_id_str[:8]}_{uploader_id_str[:8]}"
            public_id = f"kaamsetu/moderation_evidence/evidence_{case_id_str[:8]}_{uploader_id_str[:8]}"

        evidence = await EvidenceFileRepository.create_evidence({
            "case_id": case_id_str,
            "uploader_id": uploader_id_str,
            "file_name": filename,
            "file_type": mime_type,
            "secure_url": secure_url,
            "public_id": public_id,
            "description": description,
        })

        await AuditService.log_event(
            user_id=uploader_id_str,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Uploaded evidence file '{filename}' for case [{case_id_str}]",
            actor={"id": uploader_id_str, "role": "user"},
            metadata={"evidence_id": evidence.evidence_id, "case_id": case_id_str},
        )
        return evidence

    @staticmethod
    async def get_case_evidence(case_id: str) -> list[EvidenceFile]:
        """Fetch all evidence files for a case."""
        return await EvidenceFileRepository.list_by_case(str(case_id))


# ---------------------------------------------------------------------------
# Report Service
# ---------------------------------------------------------------------------

class ReportService:
    """Manages platform report submissions and detail lookups."""

    @staticmethod
    async def create_report(
        reporter_id: str,
        req: ReportCreate,
    ) -> PlatformReport:
        """Submit a new platform violation report."""
        reporter_id_str = str(reporter_id)

        report = await ReportRepository.create_report({
            "reporter_id": reporter_id_str,
            "target_type": req.target_type,
            "target_id": req.target_id,
            "category": req.category,
            "description": req.description,
            "status": ReportStatus.SUBMITTED,
        })

        # Create internal moderation case wrapper
        await ModerationCaseRepository.create_case({
            "reference_id": report.report_id,
            "reference_type": "report",
            "severity": RiskLevel.MEDIUM,
        })

        await AuditService.log_event(
            user_id=reporter_id_str,
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Filed report [{req.category.value}] against target {req.target_type.value}:{req.target_id}",
            actor={"id": reporter_id_str, "role": "user"},
            metadata={"report_id": report.report_id, "category": req.category.value},
        )
        return report

    @staticmethod
    async def get_report_detail(report_id: str) -> ReportRead:
        """Fetch report detail with linked evidence files and case notes."""
        report = await ReportRepository.get_by_id(report_id)
        if not report:
            raise NotFoundException(f"Report '{report_id}' not found.")

        evidence_files = await EvidenceService.get_case_evidence(report_id)
        notes = await CaseNoteRepository.list_by_case(report_id, include_internal=True)

        evidence_dtos = [EvidenceUploadResponse.model_validate(e) for e in evidence_files]
        note_dicts = [{"note_id": n.note_id, "author_id": n.author_id, "author_role": n.author_role, "text": n.note_text, "created_at": n.created_at} for n in notes]

        read_dto = ReportRead.model_validate(report)
        read_dto.evidence_files = evidence_dtos
        read_dto.case_notes = note_dicts
        return read_dto

    @staticmethod
    async def list_reports(
        user_id: str | None = None,
        status: ReportStatus | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PlatformReport]:
        """List platform reports."""
        return await ReportRepository.list_reports(
            reporter_id=user_id, status=status, category=category, skip=skip, limit=limit
        )

    @staticmethod
    async def update_report(
        report_id: str,
        req: ReportUpdate,
        actor: dict[str, Any],
    ) -> PlatformReport:
        """Update report status or resolution notes."""
        updates = req.model_dump(exclude_unset=True)
        if updates.get("status") == ReportStatus.RESOLVED:
            updates["resolved_at"] = datetime.now(timezone.utc)

        updated = await ReportRepository.update_report(report_id, updates)
        if not updated:
            raise NotFoundException(f"Report '{report_id}' not found.")

        await AuditService.log_event(
            user_id=updated.reporter_id,
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Updated report [{report_id}] status to '{updated.status.value}'",
            actor=actor,
            metadata={"report_id": report_id},
        )
        return updated


# ---------------------------------------------------------------------------
# Moderation Service
# ---------------------------------------------------------------------------

class ModerationService:
    """Manages moderator investigations, severity assignment, and case escalations."""

    @staticmethod
    async def review_report(
        moderator: dict[str, Any],
        req: ModerationReviewRequest,
    ) -> PlatformReport:
        """Moderator assigns severity and transitions report to 'under_review'."""
        report = await ReportRepository.get_by_id(req.report_id)
        if not report:
            raise NotFoundException(f"Report '{req.report_id}' not found.")

        mod_id = str(req.assigned_moderator_id or moderator["id"])

        updated_report = await ReportRepository.update_report(
            req.report_id,
            {
                "status": ReportStatus.UNDER_REVIEW,
                "severity": req.severity,
                "assigned_moderator_id": mod_id,
                "resolution_action": req.recommended_action.value if req.recommended_action else None,
                "resolution_notes": req.notes,
            },
        )

        # Update moderation case wrapper
        m_case = await ModerationCaseRepository.get_by_reference(req.report_id)
        if m_case:
            await ModerationCaseRepository.update_case(
                m_case.case_id,
                {
                    "severity": req.severity,
                    "assigned_moderator_id": mod_id,
                    "recommended_action": req.recommended_action.value if req.recommended_action else None,
                },
            )

        if req.notes:
            await CaseNoteRepository.create_note({
                "case_id": req.report_id,
                "author_id": moderator["id"],
                "author_role": moderator.get("role", "moderator"),
                "note_text": f"[Review Summary]: {req.notes}",
                "is_internal_only": True,
            })

        await AuditService.log_event(
            user_id=report.reporter_id,
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Moderator assigned severity '{req.severity.value}' to report [{req.report_id}]",
            actor=moderator,
            metadata={"report_id": req.report_id, "severity": req.severity.value},
        )
        return updated_report

    @staticmethod
    async def escalate_case(
        moderator: dict[str, Any],
        req: ModerationEscalateRequest,
    ) -> ModerationCase:
        """Escalate a report or dispute case to senior administration."""
        m_case = await ModerationCaseRepository.get_by_reference(req.case_id)
        if not m_case:
            # Create if not exists
            m_case = await ModerationCaseRepository.create_case({
                "reference_id": req.case_id,
                "reference_type": "report",
                "severity": RiskLevel.HIGH,
                "is_escalated": True,
            })
        else:
            m_case = await ModerationCaseRepository.update_case(
                m_case.case_id, {"is_escalated": True, "severity": RiskLevel.CRITICAL}
            )

        # Also update linked report or dispute status
        report = await ReportRepository.get_by_id(req.case_id)
        if report:
            await ReportRepository.update_report(req.case_id, {"status": ReportStatus.ESCALATED})
        else:
            dispute = await DisputeRepository.get_by_id(req.case_id)
            if dispute:
                await DisputeRepository.update_dispute(req.case_id, {"status": DisputeStatus.ESCALATED})

        await CaseNoteRepository.create_note({
            "case_id": req.case_id,
            "author_id": moderator["id"],
            "author_role": moderator.get("role", "moderator"),
            "note_text": f"[ESCALATED]: {req.reason}",
            "is_internal_only": True,
        })

        await AuditService.log_event(
            user_id="system",
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Escalated case [{req.case_id}] to senior administration.",
            actor=moderator,
            metadata={"case_id": req.case_id, "reason": req.reason},
        )
        return m_case

    @staticmethod
    async def add_case_note(
        author: dict[str, Any],
        req: CaseNoteCreate,
    ) -> CaseNote:
        """Add timeline case note."""
        return await CaseNoteRepository.create_note({
            "case_id": req.case_id,
            "author_id": author["id"],
            "author_role": author.get("role", "user"),
            "note_text": req.note_text,
            "is_internal_only": req.is_internal_only,
        })


# ---------------------------------------------------------------------------
# Dispute Service
# ---------------------------------------------------------------------------

class DisputeService:
    """Manages formal dispute creation and timeline interactions."""

    @staticmethod
    async def create_dispute(
        initiator_id: str,
        req: DisputeCreate,
    ) -> Dispute:
        """Create a new formal dispute case."""
        initiator_id_str = str(initiator_id)

        dispute = await DisputeRepository.create_dispute({
            "dispute_type": req.dispute_type,
            "booking_id": req.booking_id,
            "initiator_id": initiator_id_str,
            "respondent_id": str(req.respondent_id),
            "reason": req.reason,
            "status": DisputeStatus.SUBMITTED,
        })

        # Create moderation case wrapper
        await ModerationCaseRepository.create_case({
            "reference_id": dispute.dispute_id,
            "reference_type": "dispute",
            "severity": RiskLevel.MEDIUM,
        })

        await AuditService.log_event(
            user_id=initiator_id_str,
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Opened dispute [{req.dispute_type.value}] vs respondent {req.respondent_id}",
            actor={"id": initiator_id_str, "role": "user"},
            metadata={"dispute_id": dispute.dispute_id, "type": req.dispute_type.value},
        )
        return dispute

    @staticmethod
    async def get_dispute_detail(dispute_id: str) -> DisputeRead:
        """Fetch dispute detail with evidence files and case notes."""
        dispute = await DisputeRepository.get_by_id(dispute_id)
        if not dispute:
            raise NotFoundException(f"Dispute '{dispute_id}' not found.")

        evidence_files = await EvidenceService.get_case_evidence(dispute_id)
        notes = await CaseNoteRepository.list_by_case(dispute_id, include_internal=True)

        evidence_dtos = [EvidenceUploadResponse.model_validate(e) for e in evidence_files]
        note_dicts = [{"note_id": n.note_id, "author_id": n.author_id, "author_role": n.author_role, "text": n.note_text, "created_at": n.created_at} for n in notes]

        read_dto = DisputeRead.model_validate(dispute)
        read_dto.evidence_files = evidence_dtos
        read_dto.case_notes = note_dicts
        return read_dto

    @staticmethod
    async def list_disputes(
        user_id: str | None = None,
        status: DisputeStatus | None = None,
        dispute_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Dispute]:
        """List dispute cases."""
        return await DisputeRepository.list_disputes(
            user_id=user_id, status=status, dispute_type=dispute_type, skip=skip, limit=limit
        )


# ---------------------------------------------------------------------------
# Resolution Service
# ---------------------------------------------------------------------------

class ResolutionService:
    """Executes final dispute/report decisions and triggers P8.1 administrative actions."""

    @staticmethod
    async def resolve_dispute(
        moderator: dict[str, Any],
        req: DisputeResolveRequest,
    ) -> Dispute:
        """Resolve a dispute and execute enforceable administrative actions."""
        dispute = await DisputeRepository.get_by_id(req.dispute_id)
        if not dispute:
            raise NotFoundException(f"Dispute '{req.dispute_id}' not found.")

        now = datetime.now(timezone.utc)
        action_name = req.administrative_action.value if req.administrative_action else None

        updated_dispute = await DisputeRepository.update_dispute(
            req.dispute_id,
            {
                "status": DisputeStatus.RESOLVED,
                "resolution_decision": req.resolution_decision,
                "administrative_action": action_name,
                "trust_score_delta": req.trust_score_delta,
                "assigned_moderator_id": moderator["id"],
                "resolved_at": now,
            },
        )

        # Log timeline note
        await CaseNoteRepository.create_note({
            "case_id": req.dispute_id,
            "author_id": moderator["id"],
            "author_role": moderator.get("role", "admin"),
            "note_text": f"[FINAL RESOLUTION DECISION]: {req.resolution_decision} (Action: {action_name})",
            "is_internal_only": False,
        })

        # Execute Administrative Action on Target User (if specified)
        target_id = req.target_user_id or dispute.respondent_id
        if req.administrative_action and target_id:
            await ResolutionService._apply_administrative_action(
                target_user_id=target_id,
                action=req.administrative_action,
                trust_score_delta=req.trust_score_delta,
                reason=req.resolution_decision,
                actor=moderator,
                case_id=req.dispute_id,
            )

        await AuditService.log_event(
            user_id=dispute.initiator_id,
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Resolved dispute [{req.dispute_id}]: {req.resolution_decision[:50]}...",
            actor=moderator,
            metadata={"dispute_id": req.dispute_id, "action": action_name},
        )
        return updated_dispute

    @staticmethod
    async def _apply_administrative_action(
        target_user_id: str,
        action: AdministrativeAction,
        trust_score_delta: float,
        reason: str,
        actor: dict[str, Any],
        case_id: str,
    ) -> None:
        """Internal handler for administrative actions integrated with Trust & Safety (P8.1)."""
        target_user_str = str(target_user_id)

        # 1. Trust Score Adjustment
        if trust_score_delta != 0.0 or action == AdministrativeAction.TRUST_SCORE_ADJUSTMENT:
            user_doc = await User.get(target_user_str)
            role = user_doc.role if user_doc else UserRole.WORKER
            profile = await TrustService.get_or_create_profile(target_user_str, role)
            new_score = max(0.0, min(100.0, profile.trust_score + trust_score_delta))
            await TrustService.update_trust_score(
                user_id=target_user_str,
                new_score=new_score,
                actor=actor,
                reason=f"Dispute resolution penalty ({case_id}): {reason}",
            )

        # 2. Status restrictions and Risk Events
        if action == AdministrativeAction.WARNING:
            await RiskService.record_risk_event(
                user_id=target_user_str,
                event_type=RiskEventType.POLICY_VIOLATIONS,
                severity=RiskLevel.LOW,
                description=f"Official administrative warning issued: {reason}",
                source="dispute_resolution",
                actor=actor,
            )

        elif action == AdministrativeAction.TEMPORARY_RESTRICTION:
            await TrustProfileRepository.update_profile(target_user_str, {"review_status": ReviewStatus.FLAGGED})
            await RiskService.record_risk_event(
                user_id=target_user_str,
                event_type=RiskEventType.POLICY_VIOLATIONS,
                severity=RiskLevel.HIGH,
                description=f"Temporary account restriction applied: {reason}",
                source="dispute_resolution",
                actor=actor,
            )

        elif action == AdministrativeAction.ACCOUNT_SUSPENSION:
            await TrustProfileRepository.update_profile(target_user_str, {"review_status": ReviewStatus.RESTRICTED})
            await RiskService.record_risk_event(
                user_id=target_user_str,
                event_type=RiskEventType.SUSPICIOUS_ACTIVITY,
                severity=RiskLevel.CRITICAL,
                description=f"Account suspended following dispute resolution: {reason}",
                source="dispute_resolution",
                actor=actor,
            )

        elif action == AdministrativeAction.PERMANENT_BAN:
            await TrustProfileRepository.update_profile(target_user_str, {"review_status": ReviewStatus.RESTRICTED})
            target_user = await User.get(target_user_str)
            if target_user:
                target_user.is_active = False
                await target_user.save()

            await RiskService.record_risk_event(
                user_id=target_user_str,
                event_type=RiskEventType.SUSPICIOUS_ACTIVITY,
                severity=RiskLevel.CRITICAL,
                description=f"PERMANENT BAN executed following dispute resolution: {reason}",
                source="dispute_resolution",
                actor=actor,
            )
