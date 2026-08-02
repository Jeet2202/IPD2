"""
Request/response schemas for the worker profile module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict input validation (UPI ID, government ID, coordinates, language).
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.
    - Government ID number is masked in responses (only last 4 visible).
    - Wallet balance is excluded from update schemas (managed by payments).

Design decisions:
    - Skill schemas are separate (SkillCreateRequest, SkillUpdateRequest)
      because skills are managed via dedicated endpoints.
    - UPI ID validation uses regex for the standard format (name@provider).
    - Government ID validation is format-aware per ID type (Aadhar = 12
      digits, PAN = AAAAA0000A, etc.).
    - latitude/longitude are accepted as separate fields in requests and
      converted to GeoJSON by the service layer for storage.
    - WorkerProfileResponse masks government_id_number and excludes
      wallet_balance for non-owner views (owner check in service layer).
"""

import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.worker.models import (
    AvailabilityStatus,
    GovernmentIdType,
    ProficiencyLevel,
    VerificationStatus,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# UPI ID format: alphanumeric/dot/hyphen @ provider.
# Examples: rajesh.kumar@paytm, user123@ybl, worker-1@upi
_UPI_REGEX = re.compile(r"^[a-zA-Z0-9.\-_]{3,50}@[a-zA-Z]{2,20}$")

# ISO 639-1 language codes: 2-3 lowercase letters.
_LANGUAGE_REGEX = re.compile(r"^[a-z]{2,3}$")

# Aadhar: exactly 12 digits.
_AADHAR_REGEX = re.compile(r"^\d{12}$")

# PAN: 5 uppercase letters + 4 digits + 1 uppercase letter.
_PAN_REGEX = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")

# Driving License: 2 uppercase letters + 13 digits (standard Indian format).
_DL_REGEX = re.compile(r"^[A-Z]{2}\d{13}$")

# Passport: 1 uppercase letter + 7 digits.
_PASSPORT_REGEX = re.compile(r"^[A-Z]\d{7}$")

# Voter ID: 3 uppercase letters + 7 digits.
_VOTER_REGEX = re.compile(r"^[A-Z]{3}\d{7}$")

# Government ID regex map by type.
_GOV_ID_PATTERNS: dict[GovernmentIdType, re.Pattern] = {
    GovernmentIdType.AADHAR: _AADHAR_REGEX,
    GovernmentIdType.PAN: _PAN_REGEX,
    GovernmentIdType.DRIVING_LICENSE: _DL_REGEX,
    GovernmentIdType.PASSPORT: _PASSPORT_REGEX,
    GovernmentIdType.VOTER_ID: _VOTER_REGEX,
}

# Maximum skills per worker profile.
_MAX_SKILLS = 20

# Maximum service categories per worker.
_MAX_SERVICE_CATEGORIES = 10

# Maximum languages per worker.
_MAX_LANGUAGES = 10


# ---------------------------------------------------------------------------
# Shared Validators
# ---------------------------------------------------------------------------

def _validate_upi_id(value: str) -> str:
    """
    Validate UPI ID format.

    Standard UPI format: name@provider.
    Examples: rajesh.kumar@paytm, user123@ybl, worker@upi.
    """
    stripped = value.strip()
    if not _UPI_REGEX.match(stripped):
        raise ValueError(
            "UPI ID must be in format name@provider (e.g., rajesh@paytm)"
        )
    return stripped


def _validate_language(value: str) -> str:
    """
    Validate ISO 639-1 language code.

    Accepts 2-3 lowercase letter codes (e.g., 'hi', 'en', 'ta', 'mr').
    """
    stripped = value.strip().lower()
    if not _LANGUAGE_REGEX.match(stripped):
        raise ValueError(
            "Language must be a valid ISO 639-1 code (e.g., 'hi', 'en')"
        )
    return stripped


def _validate_government_id(
    id_type: GovernmentIdType | None,
    id_number: str | None,
) -> None:
    """
    Validate government ID number format against the declared type.

    Ensures the number matches the expected pattern for the given ID type.
    Both type and number must be provided together.
    """
    if id_type is None and id_number is None:
        return
    if (id_type is None) != (id_number is None):
        raise ValueError(
            "Both government_id_type and government_id_number must be "
            "provided together, or neither"
        )
    # At this point both are non-None
    assert id_type is not None and id_number is not None
    pattern = _GOV_ID_PATTERNS.get(id_type)
    if pattern and not pattern.match(id_number.strip()):
        raise ValueError(
            f"Invalid {id_type.value} number format"
        )


def _validate_service_category(value: str) -> str:
    """
    Normalize service category slug.

    Strips whitespace, converts to lowercase, replaces spaces with hyphens.
    Examples: "Plumbing" → "plumbing", "AC Repair" → "ac-repair".
    """
    normalized = value.strip().lower().replace(" ", "-")
    if not normalized:
        raise ValueError("Service category cannot be empty")
    if len(normalized) > 100:
        raise ValueError("Service category must be at most 100 characters")
    return normalized


# ---------------------------------------------------------------------------
# Skill Schemas
# ---------------------------------------------------------------------------

class SkillCreateRequest(BaseModel):
    """
    Create a new skill in the worker's skills array.

    The service layer should:
        1. Validate the worker has < 20 skills.
        2. Check for duplicate skill_name (case-insensitive).
        3. Generate the skill ID (UUID4) server-side.
        4. Normalize skill_name to lowercase.

    Attributes:
        skill_name: Name of the skill (normalized to lowercase).
        experience_years: Years of experience (0-50).
        proficiency_level: Self-declared proficiency.
        certified: Whether the worker holds a formal certification.
        certificate_url: URL to the certificate document.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    skill_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Skill name (e.g., 'plumbing', 'electrical wiring')",
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
        description="Holds a formal certification",
    )
    certificate_url: str | None = Field(
        default=None,
        max_length=512,
        description="URL to certificate document",
    )

    @field_validator("skill_name")
    @classmethod
    def normalize_skill_name(cls, value: str) -> str:
        """Normalize to lowercase for consistent storage and search."""
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Skill name cannot be empty")
        return normalized

    @model_validator(mode="after")
    def validate_certificate_consistency(self) -> "SkillCreateRequest":
        """
        If certified is True, certificate_url should ideally be provided.
        If certified is False, certificate_url should be None.
        """
        if not self.certified and self.certificate_url:
            raise ValueError(
                "certificate_url should only be provided when certified is True"
            )
        return self


class SkillUpdateRequest(BaseModel):
    """
    Partial update for an existing skill.

    All fields optional. At least one must be provided.
    The service layer locates the skill by ID within the embedded array.

    Attributes:
        skill_name: Updated skill name.
        experience_years: Updated experience.
        proficiency_level: Updated proficiency.
        certified: Updated certification status.
        certificate_url: Updated certificate URL.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    skill_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated skill name",
    )
    experience_years: float | None = Field(
        default=None,
        ge=0.0,
        le=50.0,
        description="Updated experience years",
    )
    proficiency_level: ProficiencyLevel | None = Field(
        default=None,
        description="Updated proficiency level",
    )
    certified: bool | None = Field(
        default=None,
        description="Updated certification status",
    )
    certificate_url: str | None = Field(
        default=None,
        max_length=512,
        description="Updated certificate URL",
    )

    @field_validator("skill_name")
    @classmethod
    def normalize_skill_name(cls, value: str | None) -> str | None:
        if value is not None:
            normalized = value.strip().lower()
            if not normalized:
                raise ValueError("Skill name cannot be empty")
            return normalized
        return value

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "SkillUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Worker Profile Schemas
# ---------------------------------------------------------------------------

class WorkerProfileCreateRequest(BaseModel):
    """
    Create a new worker profile.

    Called after user registration when role=WORKER. The service layer
    should:
        1. Verify the User exists and has role=WORKER.
        2. Verify no WorkerProfile exists for this user_id.
        3. Create the profile with defaults for unset fields.

    Most fields are optional — allows fast onboarding. Profile can be
    completed gradually. Verification documents can be submitted later.

    Attributes:
        bio: Short professional description.
        profile_photo: Profile photo URL.
        experience_years: Total professional experience.
        service_radius_km: Maximum travel distance for jobs.
        latitude: Current latitude (provided with longitude).
        longitude: Current longitude (provided with latitude).
        skills: Initial skills (optional, can be added later).
        service_categories: Service types offered.
        languages: Languages spoken.
        hourly_rate: Base hourly rate in INR.
        upi_id: UPI ID for payouts.
        government_id_type: Type of government ID for KYC.
        government_id_number: Government ID number.
        government_id_document: URL to uploaded ID document.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    bio: str | None = Field(
        default=None,
        max_length=1000,
        description="Short professional description",
        examples=["Experienced plumber with 8+ years."],
    )
    profile_photo: str | None = Field(
        default=None,
        max_length=512,
        description="Profile photo URL",
    )
    experience_years: float = Field(
        default=0.0,
        ge=0.0,
        le=50.0,
        description="Total professional experience (years)",
    )
    service_radius_km: float = Field(
        default=10.0,
        ge=1.0,
        le=100.0,
        description="Maximum travel distance (km)",
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="Current latitude (WGS84)",
        examples=[19.0760],
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="Current longitude (WGS84)",
        examples=[72.8777],
    )
    skills: list[SkillCreateRequest] = Field(
        default_factory=list,
        max_length=_MAX_SKILLS,
        description="Initial skills (can be added later)",
    )
    service_categories: list[str] = Field(
        default_factory=list,
        max_length=_MAX_SERVICE_CATEGORIES,
        description="Service category slugs",
        examples=[["plumbing", "electrical"]],
    )
    languages: list[str] = Field(
        default_factory=list,
        max_length=_MAX_LANGUAGES,
        description="ISO 639-1 language codes",
        examples=[["hi", "en"]],
    )
    hourly_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=50000.0,
        description="Base hourly rate in INR",
    )
    upi_id: str | None = Field(
        default=None,
        max_length=100,
        description="UPI ID for payouts",
        examples=["rajesh@paytm"],
    )
    government_id_type: GovernmentIdType | None = Field(
        default=None,
        description="Government ID type for KYC",
    )
    government_id_number: str | None = Field(
        default=None,
        max_length=50,
        description="Government ID number",
    )
    government_id_document: str | None = Field(
        default=None,
        max_length=512,
        description="URL to uploaded ID document",
    )

    # --- Validators ---

    @field_validator("upi_id")
    @classmethod
    def validate_upi_id(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_upi_id(value)
        return value

    @field_validator("service_categories")
    @classmethod
    def normalize_service_categories(cls, value: list[str]) -> list[str]:
        """Normalize and deduplicate service categories."""
        normalized = [_validate_service_category(cat) for cat in value]
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for cat in normalized:
            if cat not in seen:
                seen.add(cat)
                unique.append(cat)
        return unique

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, value: list[str]) -> list[str]:
        """Validate and deduplicate language codes."""
        validated = [_validate_language(lang) for lang in value]
        return list(dict.fromkeys(validated))  # Deduplicate, preserve order

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> "WorkerProfileCreateRequest":
        """Ensure latitude and longitude are provided together."""
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None
        if has_lat != has_lng:
            raise ValueError(
                "Both latitude and longitude must be provided together, or neither"
            )
        return self

    @model_validator(mode="after")
    def validate_government_id_pair(self) -> "WorkerProfileCreateRequest":
        """Ensure government ID type and number are provided together."""
        _validate_government_id(self.government_id_type, self.government_id_number)
        return self


class WorkerProfileUpdateRequest(BaseModel):
    """
    Partial update for an existing worker profile.

    All fields optional. At least one must be provided.
    The service layer should validate:
        - Workers can update their own profile fields.
        - Only admins can change verification_status and is_featured.
        - wallet_balance is NOT updatable here (managed by payments).

    Attributes:
        bio: Updated professional description.
        profile_photo: Updated photo URL.
        experience_years: Updated experience.
        availability_status: Updated availability state.
        is_available: Updated master toggle.
        service_radius_km: Updated travel distance.
        latitude: Updated latitude (with longitude).
        longitude: Updated longitude (with latitude).
        service_categories: Updated service types.
        languages: Updated spoken languages.
        hourly_rate: Updated base rate.
        upi_id: Updated UPI ID.
        verification_status: Status change (admin-only).
        is_featured: Featured flag (admin-only).
        government_id_type: Updated ID type (triggers re-verification).
        government_id_number: Updated ID number (triggers re-verification).
        government_id_document: Updated ID document URL.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    bio: str | None = Field(
        default=None,
        max_length=1000,
        description="Professional description",
    )
    profile_photo: str | None = Field(
        default=None,
        max_length=512,
        description="Profile photo URL",
    )
    experience_years: float | None = Field(
        default=None,
        ge=0.0,
        le=50.0,
        description="Total experience (years)",
    )
    availability_status: AvailabilityStatus | None = Field(
        default=None,
        description="Availability state",
    )
    is_available: bool | None = Field(
        default=None,
        description="Master availability toggle",
    )
    service_radius_km: float | None = Field(
        default=None,
        ge=1.0,
        le=100.0,
        description="Travel distance (km)",
    )
    latitude: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="Current latitude",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="Current longitude",
    )
    service_categories: list[str] | None = Field(
        default=None,
        max_length=_MAX_SERVICE_CATEGORIES,
        description="Service category slugs",
    )
    languages: list[str] | None = Field(
        default=None,
        max_length=_MAX_LANGUAGES,
        description="ISO 639-1 language codes",
    )
    hourly_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=50000.0,
        description="Base hourly rate (INR)",
    )
    upi_id: str | None = Field(
        default=None,
        max_length=100,
        description="UPI ID for payouts",
    )
    verification_status: VerificationStatus | None = Field(
        default=None,
        description="Verification status (admin-only)",
    )
    is_featured: bool | None = Field(
        default=None,
        description="Featured flag (admin-only)",
    )
    government_id_type: GovernmentIdType | None = Field(
        default=None,
        description="Government ID type",
    )
    government_id_number: str | None = Field(
        default=None,
        max_length=50,
        description="Government ID number",
    )
    government_id_document: str | None = Field(
        default=None,
        max_length=512,
        description="URL to ID document",
    )

    # --- Validators ---

    @field_validator("upi_id")
    @classmethod
    def validate_upi_id(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_upi_id(value)
        return value

    @field_validator("service_categories")
    @classmethod
    def normalize_service_categories(
        cls, value: list[str] | None,
    ) -> list[str] | None:
        if value is not None:
            normalized = [_validate_service_category(cat) for cat in value]
            seen: set[str] = set()
            unique: list[str] = []
            for cat in normalized:
                if cat not in seen:
                    seen.add(cat)
                    unique.append(cat)
            return unique
        return value

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, value: list[str] | None) -> list[str] | None:
        if value is not None:
            validated = [_validate_language(lang) for lang in value]
            return list(dict.fromkeys(validated))
        return value

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> "WorkerProfileUpdateRequest":
        """Ensure latitude and longitude are provided together."""
        has_lat = self.latitude is not None
        has_lng = self.longitude is not None
        if has_lat != has_lng:
            raise ValueError(
                "Both latitude and longitude must be provided together, or neither"
            )
        return self

    @model_validator(mode="after")
    def validate_government_id_pair(self) -> "WorkerProfileUpdateRequest":
        """Ensure government ID type and number are provided together."""
        _validate_government_id(self.government_id_type, self.government_id_number)
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "WorkerProfileUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class SkillResponse(BaseModel):
    """
    Skill representation in API responses.

    Attributes:
        id: Skill UUID.
        skill_name: Normalized skill name.
        experience_years: Experience in this skill.
        proficiency_level: Proficiency level.
        certified: Certification status.
        certificate_url: Certificate document URL.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Skill UUID")
    skill_name: str = Field(..., description="Skill name")
    experience_years: float = Field(..., description="Experience (years)")
    proficiency_level: ProficiencyLevel = Field(..., description="Proficiency")
    certified: bool = Field(..., description="Formally certified")
    certificate_url: str | None = Field(None, description="Certificate URL")


class WorkerProfileResponse(BaseModel):
    """
    Complete worker profile representation for API responses.

    Security:
        - government_id_number: MASKED (only last 4 chars visible).
        - metadata: EXCLUDED (may contain internal data).
        - wallet_balance: Included (service layer should filter for
          non-owner requests if needed).

    Includes computed fields:
        - skill_count: Number of registered skills.
        - job_completion_ratio: Completion rate percentage.
        - is_searchable: Whether worker appears in search results.

    Attributes:
        id: Profile document ID.
        user_id: Reference to User document.
        bio: Professional description.
        profile_photo: Photo URL.
        experience_years: Total experience.
        availability_status: Current availability.
        verification_status: KYC status.
        is_available: Master availability toggle.
        is_featured: Promoted flag.
        service_radius_km: Travel distance.
        latitude: Current latitude (from GeoJSON).
        longitude: Current longitude (from GeoJSON).
        skills: List of skill responses.
        service_categories: Service types.
        languages: Spoken languages.
        hourly_rate: Base rate (INR).
        average_rating: Mean customer rating.
        total_reviews: Review count.
        completed_jobs: Completed job count.
        cancelled_jobs: Cancelled job count.
        acceptance_rate: Request acceptance percentage.
        response_time_minutes: Average response time.
        wallet_balance: Wallet balance (INR).
        upi_id: UPI ID.
        bank_verified: Bank verification status.
        government_id_type: ID type.
        government_id_number: Masked ID number.
        government_id_verified: Whether ID is verified.
        police_verification: Police check status.
        skill_count: Number of skills (computed).
        job_completion_ratio: Completion % (computed).
        is_searchable: Search visibility (computed).
        created_at: Profile creation time.
        updated_at: Last update time.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="Profile ID (MongoDB ObjectId)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    user_id: str = Field(..., description="Reference to User document")

    # --- Professional ---
    bio: str | None = Field(None, description="Professional description")
    profile_photo: str | None = Field(None, description="Profile photo URL")
    experience_years: float = Field(..., description="Total experience (years)")

    # --- Availability ---
    availability_status: AvailabilityStatus = Field(..., description="Availability")
    verification_status: VerificationStatus = Field(..., description="KYC status")
    is_available: bool = Field(..., description="Master availability toggle")
    is_featured: bool = Field(..., description="Promoted worker flag")
    service_radius_km: float = Field(..., description="Travel distance (km)")
    latitude: float | None = Field(None, description="Current latitude")
    longitude: float | None = Field(None, description="Current longitude")

    # --- Skills & Services ---
    skills: list[SkillResponse] = Field(default_factory=list, description="Skills")
    service_categories: list[str] = Field(
        default_factory=list, description="Service types",
    )
    languages: list[str] = Field(default_factory=list, description="Languages")

    # --- Pricing ---
    hourly_rate: float = Field(..., description="Base hourly rate (INR)")

    # --- Performance ---
    average_rating: float = Field(..., description="Mean rating (0-5)")
    total_reviews: int = Field(..., description="Review count")
    completed_jobs: int = Field(..., description="Completed jobs")
    cancelled_jobs: int = Field(..., description="Cancelled jobs")
    acceptance_rate: float = Field(..., description="Acceptance rate %")
    response_time_minutes: float = Field(..., description="Avg response time")

    # --- Financial ---
    wallet_balance: float = Field(..., description="Wallet balance (INR)")
    upi_id: str | None = Field(None, description="UPI ID")
    bank_verified: bool = Field(..., description="Bank verified")

    # --- Verification ---
    government_id_type: GovernmentIdType | None = Field(None, description="ID type")
    government_id_number: str | None = Field(None, description="Masked ID number")
    government_id_verified: bool = Field(
        default=False, description="Government ID verified",
    )
    police_verification: bool = Field(..., description="Police check completed")

    # --- Computed ---
    skill_count: int = Field(default=0, description="Number of skills")
    job_completion_ratio: float = Field(default=0.0, description="Completion %")
    is_searchable: bool = Field(default=False, description="Visible in search")

    # --- Timestamps ---
    created_at: datetime = Field(..., description="Profile creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """Convert Beanie PydanticObjectId to plain string."""
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def transform_for_response(cls, data: object) -> object:
        """
        Transform document data for API response:
        1. Flatten GeoJSON coordinates to latitude/longitude.
        2. Mask government ID number (show only last 4 chars).
        3. Compute derived fields (skill_count, job_completion_ratio).
        4. Derive government_id_verified from verification_status.
        """
        if isinstance(data, dict):
            # Flatten GeoJSON
            location = data.get("current_location")
            if location and isinstance(location, dict):
                coords = location.get("coordinates", [])
                if len(coords) == 2:
                    data["longitude"] = coords[0]
                    data["latitude"] = coords[1]

            # Mask government ID
            gov_id = data.get("government_id_number")
            if gov_id and len(gov_id) > 4:
                data["government_id_number"] = (
                    "X" * (len(gov_id) - 4) + gov_id[-4:]
                )
            elif gov_id:
                data["government_id_number"] = "X" * len(gov_id)

            # Compute derived fields
            skills = data.get("skills", [])
            data["skill_count"] = len(skills)

            completed = data.get("completed_jobs", 0)
            cancelled = data.get("cancelled_jobs", 0)
            total_jobs = completed + cancelled
            data["job_completion_ratio"] = (
                round((completed / total_jobs) * 100, 2) if total_jobs > 0 else 0.0
            )

            # Derive government_id_verified
            v_status = data.get("verification_status")
            data["government_id_verified"] = (
                v_status == VerificationStatus.VERIFIED
                or v_status == "verified"
            )

            # Derive is_searchable
            is_available = data.get("is_available", False)
            avail_status = data.get("availability_status")
            non_searchable = {
                AvailabilityStatus.OFFLINE,
                AvailabilityStatus.ON_LEAVE,
                "offline",
                "on_leave",
            }
            data["is_searchable"] = (
                data.get("government_id_verified", False)
                and is_available
                and avail_status not in non_searchable
            )

            return data

        # Beanie Document with @property access — from_attributes reads them
        if hasattr(data, "current_location") and data.current_location is not None:
            coords = getattr(data.current_location, "coordinates", [])
            if len(coords) == 2:
                # We need to convert to dict to inject lat/lng
                result = data.model_dump()
                result["longitude"] = coords[0]
                result["latitude"] = coords[1]
                # Mask government ID using model property
                if hasattr(data, "masked_government_id"):
                    result["government_id_number"] = data.masked_government_id
                # Computed properties will be read by from_attributes
                return result

        return data
