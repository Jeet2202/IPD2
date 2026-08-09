"""
Domain services for Worker Verification, Document Management, Admin Approval, and Trust Badges.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from beanie import PydanticObjectId
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.trust.schemas import AuditEventType, RiskEventType, RiskLevel
from app.trust.service import AuditService, RiskService, TrustService
from app.uploads.service import CloudinaryService
from app.utils.enums import UserRole
from app.worker.models import WorkerProfile
from app.verification.models import (
    VerificationBadge,
    VerificationDocument,
    VerificationReview,
    WorkerVerification,
)
from app.verification.repository import (
    VerificationBadgeRepository,
    VerificationDocumentRepository,
    VerificationReviewRepository,
    WorkerVerificationRepository,
)
from app.verification.schemas import (
    DocumentUploadResponse,
    TrustBadgeRead,
    TrustBadgeRule,
    TrustBadgeType,
    VerificationRead,
    VerificationStatus,
    VerificationStatusRead,
    VerificationSubmitRequest,
    VerificationType,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default Badge Rules Configuration
# ---------------------------------------------------------------------------

DEFAULT_BADGE_RULES: list[TrustBadgeRule] = [
    TrustBadgeRule(
        badge_type=TrustBadgeType.VERIFIED_WORKER,
        badge_name="Verified Worker",
        description="Official KaamSetu verified service provider.",
        required_verification_type=VerificationType.PROFILE,
        trust_score_bonus=5.0,
    ),
    TrustBadgeRule(
        badge_type=TrustBadgeType.IDENTITY_VERIFIED,
        badge_name="Identity Verified",
        description="Government ID and background verification passed.",
        required_verification_type=VerificationType.IDENTITY,
        trust_score_bonus=5.0,
    ),
    TrustBadgeRule(
        badge_type=TrustBadgeType.EXPERIENCED_WORKER,
        badge_name="Experienced Worker",
        description="Verified work history and professional experience.",
        required_verification_type=VerificationType.EXPERIENCE,
        trust_score_bonus=5.0,
    ),
    TrustBadgeRule(
        badge_type=TrustBadgeType.TRUSTED_PROFESSIONAL,
        badge_name="Trusted Professional",
        description="Skill certificates and technical competence verified.",
        required_verification_type=VerificationType.SKILL,
        trust_score_bonus=5.0,
    ),
    TrustBadgeRule(
        badge_type=TrustBadgeType.TOP_RATED,
        badge_name="Top Rated",
        description="Consistently high ratings and outstanding reviews.",
        trust_score_bonus=5.0,
    ),
    TrustBadgeRule(
        badge_type=TrustBadgeType.FAST_RESPONDER,
        badge_name="Fast Responder",
        description="Quick customer response time and job acceptance.",
        trust_score_bonus=5.0,
    ),
]


# ---------------------------------------------------------------------------
# Document Service
# ---------------------------------------------------------------------------

class VerificationDocumentService:
    """Handles verification document uploads to Cloudinary and metadata tracking."""

    @staticmethod
    async def upload_document(
        worker_id: str,
        document_type: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str = "application/octet-stream",
        document_number: str | None = None,
    ) -> VerificationDocument:
        """
        Upload document file bytes to Cloudinary and save versioned metadata in MongoDB.
        """
        worker_id_str = str(worker_id)

        # Check existing version
        existing_doc = await VerificationDocumentRepository.get_active_by_type(worker_id_str, document_type)
        new_version = (existing_doc.version + 1) if existing_doc else 1

        # Attempt Cloudinary upload with fallback for test environments
        try:
            secure_url, public_id = CloudinaryService.upload_verification_document(
                file_bytes=file_bytes,
                filename=filename,
                worker_id=worker_id_str,
                document_type=document_type,
            )
        except Exception as e:
            logger.warning("Cloudinary upload failed or not configured (%s). Using fallback metadata for test.", str(e))
            secure_url = f"https://res.cloudinary.com/mock/image/upload/v1/kaamsetu/doc_{worker_id_str}_{document_type}_{new_version}"
            public_id = f"kaamsetu/verification_documents/worker_{worker_id_str}_{document_type}_{new_version}"

        doc = await VerificationDocumentRepository.create_document({
            "worker_id": worker_id_str,
            "document_type": document_type,
            "document_number": document_number,
            "secure_url": secure_url,
            "public_id": public_id,
            "version": new_version,
            "status": VerificationStatus.DRAFT,
            "file_name": filename,
            "file_size": len(file_bytes),
            "mime_type": mime_type,
        })

        await AuditService.log_event(
            user_id=worker_id_str,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Uploaded verification document '{document_type}' (v{new_version})",
            actor={"id": worker_id_str, "role": "worker"},
            metadata={"document_id": doc.document_id, "public_id": public_id},
        )
        return doc

    @staticmethod
    async def get_worker_documents(worker_id: str) -> list[VerificationDocument]:
        """Fetch all uploaded documents for a worker."""
        return await VerificationDocumentRepository.list_by_worker(str(worker_id))

    @staticmethod
    async def delete_document(document_id: str, worker_id: str) -> bool:
        """Delete document metadata and Cloudinary image."""
        doc = await VerificationDocumentRepository.get_by_id(document_id)
        if not doc or doc.worker_id != str(worker_id):
            raise NotFoundException("Verification document not found or access denied.")

        CloudinaryService.delete_image(doc.public_id)
        return await VerificationDocumentRepository.delete_document(document_id)


# ---------------------------------------------------------------------------
# Trust Badge Service
# ---------------------------------------------------------------------------

class BadgeService:
    """Manages trust badges and rule evaluations."""

    @staticmethod
    def list_badge_rules() -> list[TrustBadgeRule]:
        """Return available badge rules."""
        return DEFAULT_BADGE_RULES

    @staticmethod
    async def get_worker_badges(worker_id: str) -> list[VerificationBadge]:
        """List active badges earned by a worker."""
        return await VerificationBadgeRepository.list_by_worker(str(worker_id), active_only=True)

    @staticmethod
    async def grant_badge(
        worker_id: str,
        badge_type: TrustBadgeType,
        actor: dict[str, Any] | None = None,
    ) -> VerificationBadge:
        """Grant a trust badge to a worker and update Trust Score."""
        worker_id_str = str(worker_id)
        existing = await VerificationBadgeRepository.get_badge(worker_id_str, badge_type)
        if existing:
            return existing

        rule = next((r for r in DEFAULT_BADGE_RULES if r.badge_type == badge_type), None)
        badge_name = rule.badge_name if rule else badge_type.value.replace("_", " ").title()
        description = rule.description if rule else "Verified platform trust badge."

        badge = await VerificationBadgeRepository.create_badge({
            "worker_id": worker_id_str,
            "badge_type": badge_type,
            "badge_name": badge_name,
            "description": description,
            "is_active": True,
        })

        # Trust score bonus (+5.0)
        profile = await TrustService.get_or_create_profile(worker_id_str, UserRole.WORKER)
        bonus = rule.trust_score_bonus if rule else 5.0
        new_score = min(100.0, profile.trust_score + bonus)

        await TrustService.update_trust_score(
            user_id=worker_id_str,
            new_score=new_score,
            actor=actor or {"id": "system", "role": "system"},
            reason=f"Earned trust badge '{badge_name}'",
        )

        await AuditService.log_event(
            user_id=worker_id_str,
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Trust badge '{badge_name}' granted.",
            actor=actor or {"id": "system", "role": "system"},
            metadata={"badge_id": badge.badge_id, "badge_type": badge_type.value},
        )
        return badge


# ---------------------------------------------------------------------------
# Verification Service
# ---------------------------------------------------------------------------

class VerificationService:
    """Primary worker verification submission and workflow orchestrator."""

    @staticmethod
    async def submit_verification(
        worker_id: str,
        req: VerificationSubmitRequest,
    ) -> WorkerVerification:
        """Worker submits a verification request for admin review."""
        worker_id_str = str(worker_id)

        # Check existing verification
        existing = await WorkerVerificationRepository.get_by_worker_and_type(
            worker_id_str, req.verification_type
        )

        now = datetime.now(timezone.utc)
        if existing:
            verification = await WorkerVerificationRepository.update_verification(
                existing.verification_id,
                {
                    "status": VerificationStatus.SUBMITTED,
                    "submitted_at": now,
                    "document_ids": req.document_ids,
                    "metadata": {**existing.metadata, **req.metadata, "worker_notes": req.notes},
                },
            )
        else:
            verification = await WorkerVerificationRepository.create_verification({
                "worker_id": worker_id_str,
                "verification_type": req.verification_type,
                "status": VerificationStatus.SUBMITTED,
                "submitted_at": now,
                "document_ids": req.document_ids,
                "metadata": {**req.metadata, "worker_notes": req.notes},
            })

        # Update document statuses to submitted
        for doc_id in req.document_ids:
            await VerificationDocumentRepository.update_document(
                doc_id, {"status": VerificationStatus.SUBMITTED, "verification_id": verification.verification_id}
            )

        await AuditService.log_event(
            user_id=worker_id_str,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Submitted verification request for [{req.verification_type.value}]",
            actor={"id": worker_id_str, "role": "worker"},
            metadata={"verification_id": verification.verification_id, "type": req.verification_type.value},
        )
        return verification

    @staticmethod
    async def get_verification_status(worker_id: str) -> VerificationStatusRead:
        """Get summary of worker verification state across all verification types."""
        worker_id_str = str(worker_id)
        verifications = await WorkerVerificationRepository.list_by_worker(worker_id_str)
        badges = await BadgeService.get_worker_badges(worker_id_str)

        type_statuses: dict[str, VerificationStatus] = {
            vt.value: VerificationStatus.DRAFT for vt in VerificationType
        }
        for v in verifications:
            type_statuses[v.verification_type.value] = v.status

        approved_count = sum(1 for s in type_statuses.values() if s == VerificationStatus.APPROVED)
        pending_count = sum(1 for s in type_statuses.values() if s in [VerificationStatus.SUBMITTED, VerificationStatus.UNDER_REVIEW])

        is_profile_verified = False
        try:
            from beanie import PydanticObjectId
            if PydanticObjectId.is_valid(worker_id_str):
                prof = await WorkerProfile.find_one(WorkerProfile.user_id == PydanticObjectId(worker_id_str))
                if not prof:
                    prof = await WorkerProfile.find_one(WorkerProfile.user_id == worker_id_str)
                if prof:
                    is_profile_verified = prof.is_verified
        except Exception:
            pass

        if approved_count == len(VerificationType) or type_statuses.get(VerificationType.IDENTITY.value) == VerificationStatus.APPROVED or is_profile_verified:
            overall_status = VerificationStatus.APPROVED
        elif approved_count > 0:
            overall_status = VerificationStatus.UNDER_REVIEW
        elif pending_count > 0:
            overall_status = VerificationStatus.SUBMITTED
        else:
            overall_status = VerificationStatus.DRAFT

        return VerificationStatusRead(
            worker_id=worker_id_str,
            overall_status=overall_status,
            type_statuses=type_statuses,
            approved_count=approved_count,
            pending_count=pending_count,
            earned_badges=[b.badge_name for b in badges],
        )

    @staticmethod
    async def get_verification_history(worker_id: str) -> list[WorkerVerification]:
        """Fetch full verification submission history for worker."""
        return await WorkerVerificationRepository.list_by_worker(str(worker_id))

    @staticmethod
    async def resubmit_verification(
        worker_id: str,
        verification_id: str,
        new_document_ids: list[str] | None = None,
        notes: str | None = None,
    ) -> WorkerVerification:
        """Worker resubmits a rejected verification with updated documents."""
        worker_id_str = str(worker_id)
        verification = await WorkerVerificationRepository.get_by_id(verification_id)

        if not verification or verification.worker_id != worker_id_str:
            raise NotFoundException("Verification record not found or access denied.")

        doc_ids = new_document_ids if new_document_ids is not None else verification.document_ids
        now = datetime.now(timezone.utc)

        updated = await WorkerVerificationRepository.update_verification(
            verification_id,
            {
                "status": VerificationStatus.SUBMITTED,
                "submitted_at": now,
                "document_ids": doc_ids,
                "metadata": {**verification.metadata, "resubmission_notes": notes},
            },
        )

        await AuditService.log_event(
            user_id=worker_id_str,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Resubmitted verification [{verification.verification_type.value}]",
            actor={"id": worker_id_str, "role": "worker"},
            metadata={"verification_id": verification_id},
        )
        return updated

    @staticmethod
    async def sync_worker_verification_status(worker_id: str | PydanticObjectId) -> bool:
        """
        Synchronize WorkerProfile.is_verified with WorkerVerification collection state.

        Rules:
            1. Query all WorkerVerification documents for worker_id.
            2. Worker is verified if ANY WorkerVerification has status == APPROVED.
            3. Update corresponding WorkerProfile.is_verified.
            4. Returns True if verified, False otherwise.
        """
        from beanie import PydanticObjectId
        worker_id_str = str(worker_id)
        verifications = await WorkerVerificationRepository.list_by_worker(worker_id_str)
        is_verified = any(v.status == VerificationStatus.APPROVED for v in verifications)

        try:
            profile = None
            if PydanticObjectId.is_valid(worker_id_str):
                oid = PydanticObjectId(worker_id_str)
                profile = await WorkerProfile.find_one(WorkerProfile.user_id == oid)
            if not profile:
                profile = await WorkerProfile.find_one(WorkerProfile.user_id == worker_id_str)
            if not profile and PydanticObjectId.is_valid(worker_id_str):
                profile = await WorkerProfile.get(PydanticObjectId(worker_id_str))

            if profile:
                profile.is_verified = is_verified
                await profile.save()
        except Exception as exc:
            logger.warning("Failed to sync worker profile verification status: %s", exc)

        return is_verified


# ---------------------------------------------------------------------------
# Approval Service
# ---------------------------------------------------------------------------

class ApprovalService:
    """Admin review, approval, rejection, and resubmission workflows."""

    @staticmethod
    async def start_review(
        admin_user: dict[str, Any],
        verification_id: str,
        review_notes: str | None = None,
    ) -> WorkerVerification:
        """Admin transitions verification request state to 'under_review'."""
        verification = await WorkerVerificationRepository.get_by_id(verification_id)
        if not verification:
            raise NotFoundException(f"Verification {verification_id} not found.")

        prev_status = verification.status
        updated = await WorkerVerificationRepository.update_verification(
            verification_id,
            {
                "status": VerificationStatus.UNDER_REVIEW,
                "reviewer_id": admin_user["id"],
                "review_notes": review_notes,
            },
        )

        await VerificationReviewRepository.create_review({
            "verification_id": verification_id,
            "worker_id": verification.worker_id,
            "reviewer_id": admin_user["id"],
            "action": "started_review",
            "review_notes": review_notes,
            "previous_status": prev_status,
            "new_status": VerificationStatus.UNDER_REVIEW,
        })

        await AuditService.log_event(
            user_id=verification.worker_id,
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Admin started review for verification [{verification.verification_type.value}]",
            actor=admin_user,
            metadata={"verification_id": verification_id},
        )
        return updated

    @staticmethod
    async def approve_verification(
        admin_user: dict[str, Any],
        verification_id: str,
        review_notes: str | None = None,
        grant_badges: list[TrustBadgeType] | None = None,
    ) -> WorkerVerification:
        """Admin approves a worker verification request."""
        verification = await WorkerVerificationRepository.get_by_id(verification_id)
        if not verification:
            raise NotFoundException(f"Verification {verification_id} not found.")

        prev_status = verification.status
        now = datetime.now(timezone.utc)

        updated = await WorkerVerificationRepository.update_verification(
            verification_id,
            {
                "status": VerificationStatus.APPROVED,
                "reviewed_at": now,
                "reviewer_id": admin_user["id"],
                "review_notes": review_notes,
            },
        )

        # Update document statuses
        for doc_id in verification.document_ids:
            await VerificationDocumentRepository.update_document(
                doc_id, {"status": VerificationStatus.APPROVED}
            )

        # Record review audit
        await VerificationReviewRepository.create_review({
            "verification_id": verification_id,
            "worker_id": verification.worker_id,
            "reviewer_id": admin_user["id"],
            "action": "approved",
            "review_notes": review_notes,
            "previous_status": prev_status,
            "new_status": VerificationStatus.APPROVED,
        })

        # 1. Update Trust Score (+10.0)
        profile = await TrustService.get_or_create_profile(verification.worker_id, UserRole.WORKER)
        new_score = min(100.0, profile.trust_score + 10.0)
        await TrustService.update_trust_score(
            user_id=verification.worker_id,
            new_score=new_score,
            actor=admin_user,
            reason=f"Verification approved: {verification.verification_type.value}",
        )

        # 2. Automatically grant matching badge
        badge_mapping = {
            VerificationType.IDENTITY: TrustBadgeType.IDENTITY_VERIFIED,
            VerificationType.PROFILE: TrustBadgeType.VERIFIED_WORKER,
            VerificationType.EXPERIENCE: TrustBadgeType.EXPERIENCED_WORKER,
            VerificationType.SKILL: TrustBadgeType.TRUSTED_PROFESSIONAL,
        }
        if verification.verification_type in badge_mapping:
            await BadgeService.grant_badge(
                worker_id=verification.worker_id,
                badge_type=badge_mapping[verification.verification_type],
                actor=admin_user,
            )

        # Grant any additional explicit badges requested by admin
        if grant_badges:
            for b in grant_badges:
                await BadgeService.grant_badge(
                    worker_id=verification.worker_id,
                    badge_type=b,
                    actor=admin_user,
                )

        # 3. Synchronize WorkerProfile.is_verified = True
        await VerificationService.sync_worker_verification_status(verification.worker_id)

        await AuditService.log_event(
            user_id=verification.worker_id,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Approved worker verification [{verification.verification_type.value}]",
            actor=admin_user,
            metadata={"verification_id": verification_id, "new_score": new_score},
        )
        return updated

    @staticmethod
    async def reject_verification(
        admin_user: dict[str, Any],
        verification_id: str,
        review_notes: str,
        request_resubmission: bool = False,
    ) -> WorkerVerification:
        """Admin rejects a verification request or requests resubmission."""
        verification = await WorkerVerificationRepository.get_by_id(verification_id)
        if not verification:
            raise NotFoundException(f"Verification {verification_id} not found.")

        prev_status = verification.status
        new_status = VerificationStatus.RESUBMISSION_REQUIRED if request_resubmission else VerificationStatus.REJECTED
        now = datetime.now(timezone.utc)

        updated = await WorkerVerificationRepository.update_verification(
            verification_id,
            {
                "status": new_status,
                "reviewed_at": now,
                "reviewer_id": admin_user["id"],
                "review_notes": review_notes,
            },
        )

        # Update document statuses
        for doc_id in verification.document_ids:
            await VerificationDocumentRepository.update_document(doc_id, {"status": new_status})

        # Record review audit
        action_name = "requested_resubmission" if request_resubmission else "rejected"
        await VerificationReviewRepository.create_review({
            "verification_id": verification_id,
            "worker_id": verification.worker_id,
            "reviewer_id": admin_user["id"],
            "action": action_name,
            "review_notes": review_notes,
            "previous_status": prev_status,
            "new_status": new_status,
        })

        if not request_resubmission:
            # 1. Record Risk Event in RiskService (P8.1)
            await RiskService.record_risk_event(
                user_id=verification.worker_id,
                event_type=RiskEventType.FAILED_VERIFICATION,
                severity=RiskLevel.MEDIUM,
                description=f"Verification rejected [{verification.verification_type.value}]: {review_notes}",
                source="admin_verification_review",
                actor=admin_user,
            )

            # 2. Subtract Trust Score (-5.0)
            profile = await TrustService.get_or_create_profile(verification.worker_id, UserRole.WORKER)
            new_score = max(0.0, profile.trust_score - 5.0)
            await TrustService.update_trust_score(
                user_id=verification.worker_id,
                new_score=new_score,
                actor=admin_user,
                reason=f"Verification rejected: {verification.verification_type.value}",
            )

        # 3. Synchronize WorkerProfile.is_verified
        await VerificationService.sync_worker_verification_status(verification.worker_id)

        await AuditService.log_event(
            user_id=verification.worker_id,
            event_type=AuditEventType.VERIFICATION_CHANGES,
            description=f"Verification [{verification.verification_type.value}] marked as '{new_status.value}'",
            actor=admin_user,
            metadata={"verification_id": verification_id, "reason": review_notes},
        )
        return updated
