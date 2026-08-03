"""
Recommendation Engine Configuration — scoring weights and parameters.

Design:
    - Centralized scoring weights.
    - Eliminates hardcoded constants throughout scoring functions.
"""

from pydantic import BaseModel, Field


class RecommendationConfig(BaseModel):
    """
    Configurable scoring weights for deterministic worker marketplace recommendations.
    Sum of weights typically equals 1.0.
    """

    weight_skills: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Weight assigned to skill and service category match",
    )
    weight_distance: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Weight assigned to physical proximity and working radius",
    )
    weight_availability: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight assigned to real-time worker availability status",
    )
    weight_schedule: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Weight assigned to booking schedule window compatibility",
    )


# Singleton default configuration
default_recommendation_config = RecommendationConfig()
