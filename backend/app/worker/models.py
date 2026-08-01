"""
Worker Profile document model — domain-specific data for service workers.

Architecture:
    - Separates worker-specific data from auth identity (User collection).
    - One User → One WorkerProfile (enforced by unique index on user_id).
    - Skills are EMBEDDED (not a separate collection) for atomic reads.
    - Current location stored in GeoJSON for MongoDB 2dsphere queries.

Why skills are embedded (not a separate collection):
    - A worker typically has 3-10 skills — small, bounded list.
    - Every profile read needs skills — embedding avoids $lookup joins.
    - Skill data is never queried independently across workers at scale;
      queries like "find workers with skill X" use $elemMatch on the
      embedded array, which is covered by the skills.skill_name index.
    - Atomic updates: adding/removing skills is a single document write.
    - 10 skills with full fields ≈ 5 KB — no risk of 16 MB limit.

Why user_id is a string reference (not Beanie Link):
    - Avoids implicit lazy loading and hidden database fetches.
    - String reference with unique index gives O(1) lookup.
    - The service layer handles cross-collection queries explicitly.
    - Eliminates circular import risk between auth and worker modules.

Why GeoJSON for current_location:
    - MongoDB's 2dsphere index requires GeoJSON format.
    - Enables $near queries for "nearby workers" with distance sorting.
    - Enables $geoWithin queries for service area coverage.
    - Compatible with Google Maps API responses (lat/lng → GeoJSON).
    - RFC 7946 compliant: [longitude, latitude] coordinate order.

Why service_categories is a list of strings (not references):
    - Service categories are a controlled vocabulary managed by admins.
    - String list avoids $lookup joins on every worker search.
    - When a dedicated ServiceCategory collection is built later,
      the strings can serve as slugs that map to full category documents.
    - Indexed for efficient filtering: "all plumbers", "all electricians".

Scalability:
    - user_id unique index ensures O(1) profile lookup from JWT subject.
    - Job counters are denormalized (completed/cancelled) to avoid
      counting queries on the jobs collection for every profile view.
    - acceptance_rate and response_time_minutes are denormalized for
      sorting workers by reliability without aggregation.
    - metadata dict handles unforeseen future fields without migration.

Index strategy:
    - user_id (unique): Profile lookup by authenticated user. One-to-one.
    - current_location (2dsphere): Nearby worker search, geo queries.
    - verification_status + availability_status (compound): Worker
      search filters — "all verified online workers".
    - average_rating (descending): Sort workers by rating.
    - skills.skill_name: Filter workers by skill name.
    - service_categories: Filter workers by service type.
    - experience_years (descending): Sort by experience.
    - created_at (descending): Admin dashboard pagination.

Collection name: "worker_profiles" (explicit, lowercase, plural).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, GEOSPHERE, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AvailabilityStatus(str, Enum):
    """
    Real-time worker availability state.

    - ONLINE: Available and accepting new job requests.
    - OFFLINE: Not working (app closed or off-shift).
    - BUSY: Online but temporarily unavailable (on break, commuting).
    - ON_JOB: Currently performing a job. Auto-set by the jobs module.
    - ON_LEAVE: Extended absence (vacation, sick leave). Set manually.
    """

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ON_JOB = "on_job"
    ON_LEAVE = "on_leave"


class VerificationStatus(str, Enum):
    """
    Worker identity and background verification lifecycle.

    - PENDING: Documents submitted, awaiting admin review.
    - UNDER_REVIEW: Admin has started reviewing documents.
    - VERIFIED: All checks passed. Worker can accept jobs.
    - REJECTED: Verification failed. Worker must resubmit.
    - SUSPENDED: Previously verified but suspended (policy violation).
    """

    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class GovernmentIdType(str, Enum):
    """
    Government-issued identity document types (India).

    Used for KYC verification and background checks.
    """

    AADHAR = "aadhar"
    PAN = "pan"
    DRIVING_LICENSE = "driving_license"
    PASSPORT = "passport"
    VOTER_ID = "voter_id"


class ProficiencyLevel(str, Enum):
    """
    Skill proficiency level for worker matching and pricing.

    - BEGINNER: < 1 year experience, basic jobs only.
    - INTERMEDIATE: 1-3 years, standard jobs.
    - ADVANCED: 3-7 years, complex jobs with quality guarantee.
    - EXPERT: 7+ years, specialist work, premium pricing eligible.
    """

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# ---------------------------------------------------------------------------
# Embedded Models
# ---------------------------------------------------------------------------

class GeoLocation(BaseModel):
    """
    GeoJSON Point for MongoDB 2dsphere queries.

    Stored in GeoJSON format per MongoDB specification:
        { "type": "Point", "coordinates": [longitude, latitude] }

    Note: MongoDB GeoJSON uses [longitude, latitude] order (not lat/lng).
    This matches the GeoJSON RFC 7946 standard.

    Attributes:
        type: Locked to "Point" via Literal — prevents invalid geometry types.
        coordinates: [longitude, latitude] pair. Required, exactly 2 elements.
    """

    type: Literal["Point"] = Field(
        default="Point",
        description="GeoJSON geometry type (locked to 'Point')",
    )
    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude] in GeoJSON order",
        examples=[[72.8777, 19.0760]],
    )


class Skill(BaseModel):
    """
    Embedded skill model — stored inside WorkerProfile.skills.

    Each skill has a UUID for targeted updates and deletion via array
    filters without loading the entire profile document.

    Attributes:
        id: UUID4 string — unique identifier within the skills array.
            Generated server-side, not by the client.
        skill_name: Normalized skill name (lowercase, stripped).
                    Examples: "plumbing", "electrical wiring", "painting".
                    Indexed for worker search by skill.
        experience_years: Years of experience in this specific skill.
                          Used for AI matching and search ranking.
        proficiency_level: Self-declared proficiency. Combined with
                           experience_years and ratings for AI matching.
        certified: True if the worker holds a formal certification
                   for this skill (e.g., ITI diploma, trade certificate).
        certificate_url: URL to the uploaded certificate image/PDF
                         (Cloudinary/S3). None if not certified or not
                         yet uploaded. Reviewed during verification.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique skill identifier (UUID4)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    skill_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Skill name (lowercase, e.g., 'plumbing')",
        examples=["plumbing"],
    )
    experience_years: float = Field(
        default=0.0,
        ge=0.0,
        le=50.0,
        description="Years of experience in this skill",
    )
    proficiency_level: ProficiencyLevel = Field(
        default=ProficiencyLevel.BEGINNER,
        description="Self-declared proficiency level",
    )
    certified: bool = Field(
        default=False,
        description="True if worker holds a formal certification",
    )
    certificate_url: str | None = Field(
        default=None,
        max_length=512,
        description="URL to certificate image/PDF (Cloudinary/S3)",
        examples=["https://res.cloudinary.com/kaamsetu/image/upload/v1/certs/abc.pdf"],
    )


# ---------------------------------------------------------------------------
# Worker Profile Document
# ---------------------------------------------------------------------------

class WorkerProfile(Document):
    """
    Domain-specific profile for platform service workers.

    Stores professional information, skills, availability, location,
    verification status, financial data, and performance metrics.
    Authentication data (email, password, phone) stays in the User
    collection — this profile references User via user_id.

    One User → One WorkerProfile (enforced by unique index on user_id).

    Attributes:
        user_id: Reference to the User document's ObjectId. Unique —
                 prevents duplicate profiles. Indexed for O(1) lookup
                 from JWT subject during auth flow.

        --- Professional ---
        bio: Short professional description shown on the worker card.
             Used in search results and AI-generated recommendations.
        profile_photo: URL to worker's profile photo (Cloudinary/S3).
        experience_years: Total years of professional experience across
                          all skills. Used for search ranking and pricing.

        --- Availability ---
        availability_status: Real-time availability state. Updated by the
                             worker (ONLINE/OFFLINE) or system (ON_JOB).
        is_available: Master toggle. When False, worker won't appear in
                      search results regardless of availability_status.
        is_featured: Admin-set flag for promoted worker cards in the app.
        service_radius_km: Maximum distance (km) the worker is willing
                           to travel for a job. Used in geo queries.
        current_location: GeoJSON Point for real-time position. Updated
                          by the mobile app. Indexed with 2dsphere for
                          $near queries ("workers within 5 km").

        --- Skills & Services ---
        skills: Embedded array of Skill objects (3-10 typical).
        service_categories: List of service category slugs the worker
                            offers (e.g., ["plumbing", "electrical"]).
                            Indexed for search filtering.
        languages: ISO 639-1 language codes the worker speaks.
                   Used for customer-worker matching.

        --- Pricing ---
        hourly_rate: Worker's base hourly rate in INR. Used as the
                     starting point for dynamic pricing calculations.

        --- Performance (Denormalized) ---
        average_rating: Mean rating from customer reviews (0.0-5.0).
                        Updated by the reviews module via $set.
        total_reviews: Number of reviews received. Used with
                       average_rating for weighted ranking.
        completed_jobs: Denormalized counter. Avoids COUNT queries.
        cancelled_jobs: Denormalized counter. High ratio triggers alerts.
        acceptance_rate: Percentage of job requests accepted (0.0-100.0).
                         Denormalized for sorting without aggregation.
        response_time_minutes: Average time to respond to job requests.
                               Used for AI matching and search ranking.

        --- Financial ---
        wallet_balance: In-app wallet balance in INR. Updated by the
                        payments module via atomic $inc operations.
        upi_id: Worker's UPI ID for direct payouts (e.g., name@upi).
        bank_verified: True after bank account verification via penny
                       drop or UPI verification.

        --- Verification ---
        verification_status: KYC and background check status.
        government_id_type: Type of government ID submitted for KYC.
        government_id_number: ID number (masked in API responses).
        government_id_document: URL to uploaded ID document image.
        police_verification: True after police verification is completed.

        --- Extensibility ---
        metadata: Flexible key-value store for future features:
                  - ai_match_vector: list[float] (AI matching embeddings)
                  - dynamic_pricing_factor: float (surge pricing)
                  - live_tracking_enabled: bool
                  - fcm_token: str (Firebase push notifications)
                  - analytics_dashboard_enabled: bool

        --- Timestamps ---
        created_at: Profile creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC). Auto-updated.
    """

    # --- User Reference ---
    user_id: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Reference to User document ObjectId (unique, one-to-one)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )

    # --- Professional Information ---
    bio: str | None = Field(
        default=None,
        max_length=1000,
        description="Short professional description for worker card",
        examples=["Experienced plumber with 8+ years in residential plumbing."],
    )
    profile_photo: str | None = Field(
        default=None,
        max_length=512,
        description="URL to profile photo (Cloudinary/S3)",
        examples=["https://res.cloudinary.com/kaamsetu/image/upload/v1/workers/abc123.jpg"],
    )
    experience_years: float = Field(
        default=0.0,
        ge=0.0,
        le=50.0,
        description="Total years of professional experience",
    )

    # --- Availability ---
    availability_status: AvailabilityStatus = Field(
        default=AvailabilityStatus.OFFLINE,
        description="Real-time availability state",
    )
    is_available: bool = Field(
        default=True,
        description="Master toggle — False hides worker from search",
    )
    is_featured: bool = Field(
        default=False,
        description="Admin-set flag for promoted worker cards",
    )
    service_radius_km: float = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        description="Maximum travel distance for jobs (km)",
    )
    current_location: GeoLocation | None = Field(
        default=None,
        description="GeoJSON Point for real-time worker position",
    )

    # --- Skills & Services ---
    skills: list[Skill] = Field(
        default_factory=list,
        max_length=20,
        description="Embedded array of professional skills (max 20)",
    )
    service_categories: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Service category slugs (e.g., 'plumbing', 'electrical')",
        examples=[["plumbing", "electrical"]],
    )
    languages: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="ISO 639-1 language codes the worker speaks",
        examples=[["hi", "en", "mr"]],
    )

    # --- Pricing ---
    hourly_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=50000.0,
        description="Base hourly rate in INR",
    )

    # --- Performance (Denormalized) ---
    average_rating: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="Mean customer rating (0.0-5.0)",
    )
    total_reviews: int = Field(
        default=0,
        ge=0,
        description="Total number of customer reviews",
    )
    completed_jobs: int = Field(
        default=0,
        ge=0,
        description="Successfully completed jobs (denormalized)",
    )
    cancelled_jobs: int = Field(
        default=0,
        ge=0,
        description="Jobs cancelled by worker (denormalized)",
    )
    acceptance_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Job request acceptance rate percentage",
    )
    response_time_minutes: float = Field(
        default=0.0,
        ge=0.0,
        description="Average response time to job requests (minutes)",
    )

    # --- Financial ---
    wallet_balance: float = Field(
        default=0.0,
        ge=0.0,
        description="In-app wallet balance in INR",
    )
    upi_id: str | None = Field(
        default=None,
        max_length=100,
        description="UPI ID for payouts (e.g., name@upi)",
        examples=["rajesh.kumar@paytm"],
    )
    bank_verified: bool = Field(
        default=False,
        description="True after bank account verification",
    )

    # --- Verification ---
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.PENDING,
        description="KYC and background verification status",
    )
    government_id_type: GovernmentIdType | None = Field(
        default=None,
        description="Type of government ID submitted",
    )
    government_id_number: str | None = Field(
        default=None,
        max_length=50,
        description="Government ID number (masked in responses)",
        examples=["XXXX-XXXX-1234"],
    )
    government_id_document: str | None = Field(
        default=None,
        max_length=512,
        description="URL to uploaded ID document (Cloudinary/S3)",
    )
    police_verification: bool = Field(
        default=False,
        description="True after police verification is completed",
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Profile creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp (UTC, auto-updated)",
    )

    # ------------------------------------------------------------------
    # Beanie Event Hooks
    # ------------------------------------------------------------------

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        """Auto-update `updated_at` on every write operation."""
        self.updated_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Beanie Settings
    # ------------------------------------------------------------------

    class Settings:
        """
        Beanie collection configuration.

        - name: Explicit collection name (lowercase, plural).
        - indexes: Optimized for worker search, geo queries, and sorting.
        - use_state_management: Enables Beanie's change tracking for
          efficient partial updates (only modified fields sent to MongoDB).
        """

        name = "worker_profiles"
        use_state_management = True

        indexes = [
            # 2dsphere index on current_location for nearby worker search.
            # Enables $near (sorted by distance) and $geoWithin queries.
            # Sparse: only indexes documents with location data.
            IndexModel(
                [("current_location", GEOSPHERE)],
                name="idx_location_2dsphere",
                sparse=True,
            ),
            # Compound: worker search filtering by verification + availability.
            # Covers "all verified online workers" — the most common query.
            IndexModel(
                [("verification_status", ASCENDING), ("availability_status", ASCENDING)],
                name="idx_verification_availability",
            ),
            # Descending sort on average_rating for "top rated workers".
            IndexModel(
                [("average_rating", DESCENDING)],
                name="idx_average_rating_desc",
            ),
            # Skill name index for "find workers with skill X" queries.
            # Uses dot notation to index into the embedded skills array.
            IndexModel(
                [("skills.skill_name", ASCENDING)],
                name="idx_skills_name",
            ),
            # Service categories for "find all plumbers" queries.
            # MongoDB multikey index handles array fields automatically.
            IndexModel(
                [("service_categories", ASCENDING)],
                name="idx_service_categories",
            ),
            # Descending sort on experience_years for ranking.
            IndexModel(
                [("experience_years", DESCENDING)],
                name="idx_experience_desc",
            ),
            # Descending sort on created_at for admin dashboard pagination.
            IndexModel(
                [("created_at", DESCENDING)],
                name="idx_created_at_desc",
            ),
        ]

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @property
    def skill_count(self) -> int:
        """Number of registered skills."""
        return len(self.skills)

    @property
    def job_completion_ratio(self) -> float:
        """
        Job completion rate as a percentage (0.0 - 100.0).

        Based on completed_jobs vs total jobs (completed + cancelled).
        Returns 0.0 if no jobs exist (avoids ZeroDivisionError).
        """
        total = self.completed_jobs + self.cancelled_jobs
        if total == 0:
            return 0.0
        return round((self.completed_jobs / total) * 100, 2)

    @property
    def is_verified(self) -> bool:
        """True when verification status is VERIFIED."""
        return self.verification_status == VerificationStatus.VERIFIED

    @property
    def is_searchable(self) -> bool:
        """
        True when the worker should appear in search results.

        Requires: verified, available toggle on, and not offline/on_leave.
        """
        return (
            self.is_verified
            and self.is_available
            and self.availability_status
            not in (AvailabilityStatus.OFFLINE, AvailabilityStatus.ON_LEAVE)
        )

    def get_skill_by_id(self, skill_id: str) -> Skill | None:
        """Look up a skill by its UUID within the embedded array."""
        for skill in self.skills:
            if skill.id == skill_id:
                return skill
        return None

    def get_skill_by_name(self, skill_name: str) -> Skill | None:
        """Look up a skill by name (case-insensitive)."""
        normalized = skill_name.strip().lower()
        for skill in self.skills:
            if skill.skill_name.lower() == normalized:
                return skill
        return None

    @property
    def masked_government_id(self) -> str | None:
        """
        Return masked government ID for safe display.

        Shows only the last 4 characters: "XXXX-XXXX-1234".
        Returns None if no ID is stored.
        """
        if not self.government_id_number:
            return None
        if len(self.government_id_number) <= 4:
            return "X" * len(self.government_id_number)
        visible = self.government_id_number[-4:]
        masked = "X" * (len(self.government_id_number) - 4)
        return f"{masked}{visible}"

    def __repr__(self) -> str:
        return (
            f"<WorkerProfile user_id={self.user_id} "
            f"verification={self.verification_status.value} "
            f"availability={self.availability_status.value} "
            f"skills={self.skill_count} "
            f"rating={self.average_rating}>"
        )
