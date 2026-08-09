"""
Worker Dashboard Pydantic Schemas — request/response DTOs for worker dashboard hub.
"""

from pydantic import BaseModel, Field

from app.marketplace.schemas import MarketplaceBookingItemResponse
from app.utils.enums import WorkerAvailability


class MarketplaceStatsDTO(BaseModel):
    """Lightweight marketplace metrics for worker dashboard."""

    available_jobs: int = Field(default=0, description="Total open marketplace bookings")
    recommended_jobs: int = Field(default=0, description="Count of recommended jobs for current worker")
    active_applications: int = Field(default=0, description="Count of pending job applications")


class ApplicationsSummaryDTO(BaseModel):
    """Summary of worker job application counts by status."""

    total: int = Field(default=0, description="Total applications submitted")
    pending: int = Field(default=0, description="Pending applications count")
    accepted: int = Field(default=0, description="Accepted applications count")
    rejected: int = Field(default=0, description="Rejected applications count")


class WorkerDashboardResponse(BaseModel):
    """
    Aggregated payload for Worker Dashboard primary landing screen.
    """

    worker_id: str = Field(..., description="Worker user ObjectId string")
    worker_name: str = Field(..., description="Worker full name")
    availability: WorkerAvailability = Field(..., description="Current real-time availability")
    working_radius_km: float = Field(..., description="Current service radius in km")
    profile_completed: bool = Field(..., description="True if profile completion threshold met")
    is_verified: bool = Field(default=False, description="True if worker verification is approved")

    stats: MarketplaceStatsDTO = Field(..., description="Marketplace statistics")
    applications_summary: ApplicationsSummaryDTO = Field(..., description="Applications summary breakdown")

    recommended_jobs: list[MarketplaceBookingItemResponse] = Field(
        default_factory=list, description="Top 3 recommended marketplace jobs"
    )
    recent_jobs: list[MarketplaceBookingItemResponse] = Field(
        default_factory=list, description="Top 5 recent open marketplace jobs"
    )
