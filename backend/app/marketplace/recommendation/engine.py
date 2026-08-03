"""
Deterministic Worker Recommendation Engine — Phase 4.5.3.

Rules:
    - Pure deterministic scoring logic.
    - Calculates GeoJSON Haversine distance in kilometers.
    - Excludes or penalizes jobs exceeding worker.working_radius_km.
    - Uses configurable RecommendationConfig weights.
"""

import math
from typing import Any

from app.booking.models import Booking
from app.marketplace.recommendation.config import (
    RecommendationConfig,
    default_recommendation_config,
)
from app.utils.enums import WorkerAvailability
from app.worker.models import WorkerProfile


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth in kilometers.
    """
    radius = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(radius * c, 2)


class RecommendationEngine:
    """Deterministic recommendation engine for ranking marketplace bookings."""

    def __init__(
        self, config: RecommendationConfig = default_recommendation_config
    ) -> None:
        self.config = config

    def score_booking(
        self, booking: Booking, worker: WorkerProfile | None
    ) -> tuple[float, float | None, bool]:
        """
        Compute deterministic recommendation score and physical distance for a booking.

        Returns:
            Tuple of (total_score: float, distance_km: float | None, is_recommended: bool)
        """
        if not worker:
            return 0.5, None, False

        # 1. Distance & Proximity Sub-score
        distance_km: float | None = None
        distance_score: float = 0.5  # Neutral default when location is unavailable

        w_loc = worker.current_location
        b_loc = booking.service_location or booking.address_snapshot.location

        if w_loc and w_loc.coordinates and b_loc and b_loc.coordinates:
            w_lng, w_lat = w_loc.longitude, w_loc.latitude
            b_lng, b_lat = b_loc.longitude, b_loc.latitude
            distance_km = calculate_haversine_distance(w_lat, w_lng, b_lat, b_lng)

            radius = max(1.0, worker.working_radius_km)
            if distance_km > radius:
                distance_score = 0.0  # Outside working radius
            else:
                distance_score = max(0.0, 1.0 - (distance_km / radius))

        # 2. Skill & Category Match Sub-score
        worker_skills = [s.lower().strip() for s in worker.skills if s.strip()]
        booking_text = f"{booking.service_snapshot.name} {booking.service_snapshot.category_slug} {booking.problem_description or ''}".lower()

        if not worker_skills:
            skills_score = 0.5
        else:
            matches = sum(1 for skill in worker_skills if skill in booking_text)
            if matches > 0:
                skills_score = min(1.0, 0.7 + (0.3 * (matches / len(worker_skills))))
            else:
                skills_score = 0.1

        # 3. Availability Sub-score
        if worker.availability == WorkerAvailability.AVAILABLE:
            availability_score = 1.0
        elif worker.availability == WorkerAvailability.BUSY:
            availability_score = 0.4
        else:
            availability_score = 0.0

        # 4. Schedule Sub-score
        schedule_score = 1.0 if booking.scheduled_date is not None else 0.8

        # Weighted Sum
        total_score = (
            (self.config.weight_skills * skills_score)
            + (self.config.weight_distance * distance_score)
            + (self.config.weight_availability * availability_score)
            + (self.config.weight_schedule * schedule_score)
        )

        # Recommendation Threshold: score >= 0.6 and distance within working radius (if distance is known)
        is_within_radius = (
            distance_km is None or distance_km <= worker.working_radius_km
        )
        is_recommended = (
            total_score >= 0.60
            and is_within_radius
            and worker.availability == WorkerAvailability.AVAILABLE
        )

        return round(total_score, 4), distance_km, is_recommended
