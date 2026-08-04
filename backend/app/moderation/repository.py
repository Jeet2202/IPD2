"""
Repositories for Reporting, Moderation & Dispute Resolution following Clean Architecture & Repository Pattern.
"""

from datetime import datetime, timezone
from typing import Any

from app.moderation.models import (
    CaseNote,
    Dispute,
    EvidenceFile,
    ModerationCase,
    PlatformReport,
)
from app.moderation.schemas import (
    DisputeStatus,
    DisputeType,
    ReportCategory,
    ReportStatus,
)


class ReportRepository:
    """Repository for managing PlatformReport database operations."""

    @staticmethod
    async def get_by_id(report_id: str) -> PlatformReport | None:
        """Fetch report by unique report_id."""
        return await PlatformReport.find_one(PlatformReport.report_id == report_id)

    @staticmethod
    async def create_report(data: dict[str, Any]) -> PlatformReport:
        """Create and save a new PlatformReport."""
        report = PlatformReport(**data)
        await report.insert()
        return report

    @staticmethod
    async def list_reports(
        reporter_id: str | None = None,
        target_id: str | None = None,
        status: ReportStatus | None = None,
        category: ReportCategory | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PlatformReport]:
        """Query platform reports with optional filtering."""
        query: dict[str, Any] = {}
        if reporter_id:
            query["reporter_id"] = reporter_id
        if target_id:
            query["target_id"] = target_id
        if status:
            query["status"] = status
        if category:
            query["category"] = category

        return (
            await PlatformReport.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def update_report(report_id: str, updates: dict[str, Any]) -> PlatformReport | None:
        """Update fields of an existing report."""
        report = await ReportRepository.get_by_id(report_id)
        if not report:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(report, key):
                setattr(report, key, value)

        await report.save()
        return report


class DisputeRepository:
    """Repository for managing Dispute database operations."""

    @staticmethod
    async def get_by_id(dispute_id: str) -> Dispute | None:
        """Fetch dispute by unique dispute_id."""
        return await Dispute.find_one(Dispute.dispute_id == dispute_id)

    @staticmethod
    async def create_dispute(data: dict[str, Any]) -> Dispute:
        """Create and save a new Dispute."""
        dispute = Dispute(**data)
        await dispute.insert()
        return dispute

    @staticmethod
    async def list_disputes(
        user_id: str | None = None,
        status: DisputeStatus | None = None,
        dispute_type: DisputeType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Dispute]:
        """Query disputes where user is initiator or respondent, or general filter."""
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if dispute_type:
            query["dispute_type"] = dispute_type

        if user_id:
            return (
                await Dispute.find(
                    {"$or": [{"initiator_id": user_id}, {"respondent_id": user_id}], **query}
                )
                .sort("-created_at")
                .skip(skip)
                .limit(limit)
                .to_list()
            )

        return (
            await Dispute.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def update_dispute(dispute_id: str, updates: dict[str, Any]) -> Dispute | None:
        """Update fields of an existing dispute."""
        dispute = await DisputeRepository.get_by_id(dispute_id)
        if not dispute:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(dispute, key):
                setattr(dispute, key, value)

        await dispute.save()
        return dispute


class ModerationCaseRepository:
    """Repository for managing ModerationCase database operations."""

    @staticmethod
    async def get_by_reference(reference_id: str) -> ModerationCase | None:
        """Fetch moderation case by reference ID (report_id or dispute_id)."""
        return await ModerationCase.find_one(ModerationCase.reference_id == reference_id)

    @staticmethod
    async def create_case(data: dict[str, Any]) -> ModerationCase:
        """Create and save a ModerationCase."""
        m_case = ModerationCase(**data)
        await m_case.insert()
        return m_case

    @staticmethod
    async def update_case(case_id: str, updates: dict[str, Any]) -> ModerationCase | None:
        """Update a moderation case."""
        m_case = await ModerationCase.find_one(ModerationCase.case_id == case_id)
        if not m_case:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        for key, value in updates.items():
            if value is not None and hasattr(m_case, key):
                setattr(m_case, key, value)

        await m_case.save()
        return m_case


class EvidenceFileRepository:
    """Repository for managing EvidenceFile database operations."""

    @staticmethod
    async def create_evidence(data: dict[str, Any]) -> EvidenceFile:
        """Save evidence file metadata."""
        evidence = EvidenceFile(**data)
        await evidence.insert()
        return evidence

    @staticmethod
    async def list_by_case(case_id: str) -> list[EvidenceFile]:
        """Fetch evidence files linked to a report_id or dispute_id."""
        return (
            await EvidenceFile.find(EvidenceFile.case_id == case_id)
            .sort("-uploaded_at")
            .to_list()
        )


class CaseNoteRepository:
    """Repository for managing CaseNote database operations."""

    @staticmethod
    async def create_note(data: dict[str, Any]) -> CaseNote:
        """Log a timeline note on a case."""
        note = CaseNote(**data)
        await note.insert()
        return note

    @staticmethod
    async def list_by_case(case_id: str, include_internal: bool = True) -> list[CaseNote]:
        """Fetch notes for a case."""
        if include_internal:
            return (
                await CaseNote.find(CaseNote.case_id == case_id)
                .sort("created_at")
                .to_list()
            )
        return (
            await CaseNote.find(CaseNote.case_id == case_id, CaseNote.is_internal_only == False)
            .sort("created_at")
            .to_list()
        )
