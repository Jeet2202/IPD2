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
