"""
Repositories for Worker Verification & Trust Management following Clean Architecture & Repository Pattern.
"""

from datetime import datetime, timezone
from typing import Any

from app.verification.models import (
    VerificationBadge,
    VerificationDocument,
    VerificationReview,
    WorkerVerification,
)
from app.verification.schemas import (
    TrustBadgeType,
    VerificationStatus,
    VerificationType,
)


class WorkerVerificationRepository:
    """Repository for managing WorkerVerification database operations."""

    @staticmethod
    async def get_by_id(verification_id: str) -> WorkerVerification | None:
        """Fetch verification by unique verification ID."""
        return await WorkerVerification.find_one(WorkerVerification.verification_id == verification_id)

    @staticmethod
    async def get_by_worker_and_type(
        worker_id: str,
        verification_type: VerificationType,
    ) -> WorkerVerification | None:
        """Fetch verification record for a worker and verification type."""
        return await WorkerVerification.find_one(
            WorkerVerification.worker_id == worker_id,
            WorkerVerification.verification_type == verification_type,
        )

    @staticmethod
    async def list_by_worker(worker_id: str) -> list[WorkerVerification]:
        """Fetch all verifications for a worker."""
        return (
            await WorkerVerification.find(WorkerVerification.worker_id == worker_id)
            .sort("-created_at")
            .to_list()
        )

    @staticmethod
    async def list_by_status(
        status: VerificationStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[WorkerVerification]:
        """List verifications filtered by status."""
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        return (
            await WorkerVerification.find(query)
            .sort("-submitted_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def create_verification(data: dict[str, Any]) -> WorkerVerification:
        """Create and save a new WorkerVerification document."""
        verification = WorkerVerification(**data)
        await verification.insert()
        return verification

    @staticmethod
    async def update_verification(
        verification_id: str,
        updates: dict[str, Any],
    ) -> WorkerVerification | None:
        """Update an existing WorkerVerification document."""
        verification = await WorkerVerificationRepository.get_by_id(verification_id)
        if not verification:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(verification, key):
                setattr(verification, key, value)

        await verification.save()
        return verification


class VerificationDocumentRepository:
    """Repository for managing VerificationDocument database operations."""

    @staticmethod
    async def get_by_id(document_id: str) -> VerificationDocument | None:
        """Fetch verification document by ID."""
        return await VerificationDocument.find_one(VerificationDocument.document_id == document_id)

    @staticmethod
    async def list_by_worker(worker_id: str) -> list[VerificationDocument]:
        """Fetch all documents uploaded by a worker."""
        return (
            await VerificationDocument.find(VerificationDocument.worker_id == worker_id)
            .sort("-created_at")
            .to_list()
        )

    @staticmethod
    async def get_active_by_type(worker_id: str, document_type: str) -> VerificationDocument | None:
        """Fetch latest active document for a specific document_type."""
        return await VerificationDocument.find_one(
            VerificationDocument.worker_id == worker_id,
            VerificationDocument.document_type == document_type,
        )

    @staticmethod
    async def create_document(data: dict[str, Any]) -> VerificationDocument:
        """Create and save a new VerificationDocument."""
        doc = VerificationDocument(**data)
        await doc.insert()
        return doc

    @staticmethod
    async def update_document(
        document_id: str,
        updates: dict[str, Any],
    ) -> VerificationDocument | None:
        """Update fields of an existing VerificationDocument."""
        doc = await VerificationDocumentRepository.get_by_id(document_id)
        if not doc:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(doc, key):
                setattr(doc, key, value)

        await doc.save()
        return doc

    @staticmethod
    async def delete_document(document_id: str) -> bool:
        """Delete a document metadata entry."""
        doc = await VerificationDocumentRepository.get_by_id(document_id)
        if not doc:
            return False
        await doc.delete()
        return True


class VerificationReviewRepository:
    """Repository for managing VerificationReview database operations."""

    @staticmethod
    async def create_review(data: dict[str, Any]) -> VerificationReview:
        """Record an admin verification review entry."""
        review = VerificationReview(**data)
        await review.insert()
        return review

    @staticmethod
    async def list_by_verification(verification_id: str) -> list[VerificationReview]:
        """List audit review entries for a verification request."""
        return (
            await VerificationReview.find(VerificationReview.verification_id == verification_id)
            .sort("-reviewed_at")
            .to_list()
        )

    @staticmethod
    async def list_by_worker(worker_id: str) -> list[VerificationReview]:
        """List all audit review entries for a worker."""
        return (
            await VerificationReview.find(VerificationReview.worker_id == worker_id)
            .sort("-reviewed_at")
            .to_list()
        )


class VerificationBadgeRepository:
    """Repository for managing VerificationBadge database operations."""

    @staticmethod
    async def get_badge(worker_id: str, badge_type: TrustBadgeType) -> VerificationBadge | None:
        """Fetch active badge by worker ID and badge type."""
        return await VerificationBadge.find_one(
            VerificationBadge.worker_id == worker_id,
            VerificationBadge.badge_type == badge_type,
            VerificationBadge.is_active == True,
        )

    @staticmethod
    async def list_by_worker(worker_id: str, active_only: bool = True) -> list[VerificationBadge]:
        """List badges earned by a worker."""
        query: dict[str, Any] = {"worker_id": worker_id}
        if active_only:
            query["is_active"] = True
        return await VerificationBadge.find(query).sort("-granted_at").to_list()

    @staticmethod
    async def create_badge(data: dict[str, Any]) -> VerificationBadge:
        """Create and save a new VerificationBadge."""
        badge = VerificationBadge(**data)
        await badge.insert()
        return badge

    @staticmethod
    async def deactivate_badge(badge_id: str) -> VerificationBadge | None:
        """Deactivate a badge."""
        badge = await VerificationBadge.find_one(VerificationBadge.badge_id == badge_id)
        if not badge:
            return None
        badge.is_active = False
        await badge.save()
        return badge
