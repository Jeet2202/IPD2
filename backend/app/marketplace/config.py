"""
Marketplace Configuration — centralized settings for worker marketplace domain.
"""

from pydantic import BaseModel, Field


class MarketplaceConfig(BaseModel):
    """
    Centralized marketplace domain configuration.
    Avoids hardcoded thresholds across service layers.
    """

    max_applications_per_worker: int = Field(
        default=50,
        description="Maximum active applications allowed per worker",
    )
    refresh_interval_seconds: int = Field(
        default=15,
        description="Suggested client polling/refresh interval in seconds",
    )
    application_expiry_days: int = Field(
        default=7,
        description="Automatic application expiry duration in days",
    )
    default_working_radius_km: float = Field(
        default=15.0,
        description="Default working radius cutoff for workers in km",
    )


marketplace_config = MarketplaceConfig()
