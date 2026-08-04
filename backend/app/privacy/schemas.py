"""
Pydantic v2 schemas and Enums for Privacy, Compliance & Data Protection.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ConsentType(str, Enum):
    """User privacy consent categories."""
    TERMS_AND_CONDITIONS = "terms_and_conditions"
    PRIVACY_POLICY = "privacy_policy"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    AI_FEATURES = "ai_features"


class PrivacyRequestType(str, Enum):
    """Privacy and data request categories."""
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    ACCOUNT_DELETION = "account_deletion"
    CANCEL_DELETION = "cancel_deletion"


class PrivacyRequestStatus(str, Enum):
    """Lifecycle status of privacy requests."""
    PENDING_GRACE_PERIOD = "pending_grace_period"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class ExportFormat(str, Enum):
    """Supported data export formats."""
    JSON = "json"
    CSV = "csv"


# ---------------------------------------------------------------------------
# Consent DTOs
# ---------------------------------------------------------------------------

class ConsentItem(BaseModel):
    """Single consent choice DTO."""
    consent_type: ConsentType
    is_granted: bool
    policy_version: str = "1.0"


class ConsentUpdateRequest(BaseModel):
    """Payload to update multiple user consents."""
    consents: list[ConsentItem] = Field(..., min_length=1)


class ConsentRead(BaseModel):
    """Stored user consent schema."""
    id: PyObjectId
    consent_id: str
    user_id: str
    consent_type: ConsentType
    is_granted: bool
    policy_version: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Privacy Profile & Requests DTOs
# ---------------------------------------------------------------------------

class PrivacyProfileRead(BaseModel):
    """User personal privacy profile overview."""
    user_id: str
    email: str
    phone: str
    full_name: str
    role: str
    is_active: bool
    deletion_status: str = "active"  # "active", "pending_deletion"
    scheduled_deletion_at: datetime | None = None
    consents: list[ConsentRead] = Field(default_factory=list)
    active_requests_count: int = 0


class DataExportRequest(BaseModel):
    """Payload to request personal data export."""
    format: ExportFormat = ExportFormat.JSON


class DataExportRead(BaseModel):
    """Stored data export schema."""
    id: PyObjectId
    export_id: str
    user_id: str
    format: ExportFormat
    file_content: str
    status: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountDeletionRequest(BaseModel):
    """Payload to request account deletion."""
    reason: str | None = Field(default=None, max_length=1000)


class PrivacyRequestRead(BaseModel):
    """Stored privacy request schema."""
    id: PyObjectId
    request_id: str
    user_id: str
    request_type: PrivacyRequestType
    status: PrivacyRequestStatus
    grace_period_days: int
    scheduled_deletion_at: datetime | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Retention & Compliance DTOs
# ---------------------------------------------------------------------------

class RetentionPolicyRead(BaseModel):
    """Data retention policy schema."""
    id: PyObjectId
    policy_key: str
    category_name: str
    retention_days: int
    description: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ComplianceRecordRead(BaseModel):
    """Compliance audit record schema."""
    id: PyObjectId
    record_id: str
    user_id: str
    event_type: str
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
