"""
JobApplication Repository — pure database access layer for job applications.
"""

from typing import Any
from beanie import PydanticObjectId

from app.application.models import JobApplication
from app.utils.enums import ApplicationStatus


class JobApplicationRepository:
    """Encapsulates Beanie database queries for worker job applications."""

    @staticmethod
    async def create_application(application: JobApplication) -> JobApplication:
        """Insert a new job application document."""
        return await application.insert()

    @staticmethod
    async def find_application_by_booking_and_worker(
        booking_id: PydanticObjectId, worker_id: PydanticObjectId
    ) -> JobApplication | None:
        """Find an existing application by booking and worker ID."""
        return await JobApplication.find_one(
            {"booking_id": booking_id, "worker_id": worker_id}
        )

    @staticmethod
    async def list_applications_by_worker(
        worker_id: PydanticObjectId,
        status: ApplicationStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[JobApplication], int]:
        """
        List applications submitted by a specific worker with optional status filter.
        """
        filters: dict[str, Any] = {"worker_id": worker_id}
        if status:
            filters["application_status"] = status.value

        query = JobApplication.find(filters)
        total = await query.count()
        items = (
            await query
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return items, total

    @staticmethod
    async def get_application_by_id(
        application_id: str | PydanticObjectId,
    ) -> JobApplication | None:
        """Find a job application by ID."""
        if isinstance(application_id, str):
            if not PydanticObjectId.is_valid(application_id):
                return None
            application_id = PydanticObjectId(application_id)
        return await JobApplication.get(application_id)

    @staticmethod
    async def find_active_applications_for_worker(
        worker_id: PydanticObjectId,
    ) -> list[JobApplication]:
        """
        Return all job applications for a worker that are active (not rejected or withdrawn).

        "Active" means application_status is PENDING or ACCEPTED — i.e. the worker
        has expressed interest and has not been released from this booking.

        Used by the scheduling conflict check to build the worker's current time commitments.
        Rejected and withdrawn applications free the slot and are excluded.
        """
        excluded_statuses = ["rejected", "withdrawn"]
        return await JobApplication.find(
            {
                "worker_id": worker_id,
                "application_status": {"$nin": excluded_statuses},
            }
        ).to_list()

