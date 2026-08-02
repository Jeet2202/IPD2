"""
Request/response schemas for the Admin & System module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Extensive validation for dates, URLs, emails, and phone numbers.
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - AuditLogUpdateRequest does not exist. Audit logs are append-only and
      immutable by design.
    - BannerCreateRequest/UpdateRequest validates that start_date <= end_date.
    - SupportTicketUpdateRequest strictly requires a resolution when the status
      is changed to RESOLVED.
    - AppSettings is a singleton, so create/update schemas are merged into a
      single AppSettingsUpdateRequest for patching the global state.
"""

from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from app.admin.models import TicketPriority, TicketStatus, VerificationStatus


# ---------------------------------------------------------------------------
# 1. Worker Verification Schemas
# ---------------------------------------------------------------------------

class WorkerVerificationCreateRequest(BaseModel):
    """Payload to initialize a verification queue item for a worker."""
    model_config = ConfigDict(str_strip_whitespace=True)

    worker_id: str = Field(..., description="Worker ObjectId")
    submitted_documents: dict = Field(..., description="URLs to docs")


class WorkerVerificationUpdateRequest(BaseModel):
    """Admin payload to update the moderation state of a worker."""
    model_config = ConfigDict(str_strip_whitespace=True)

    verification_status: VerificationStatus | None = Field(None)
    verification_notes: str | None = Field(None, max_length=2000)
    rejection_reason: str | None = Field(None, max_length=1000)
    verified_by: str | None = Field(None, description="Admin ObjectId")

    @model_validator(mode="after")
    def validate_rejection(self) -> "WorkerVerificationUpdateRequest":
        """Require a reason if the worker is rejected."""
        if self.verification_status == VerificationStatus.REJECTED:
            if not self.rejection_reason:
                raise ValueError("rejection_reason is required when rejecting a worker")
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "WorkerVerificationUpdateRequest":
        provided = {k for k in self.model_fields if getattr(self, k) is not None}
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


class WorkerVerificationResponse(BaseModel):
    """API response for Worker Verification state."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(...)
    worker_id: str = Field(...)
    verification_status: VerificationStatus = Field(...)
    submitted_documents: dict = Field(...)
    verified_by: str | None = Field(None)
    verification_notes: str | None = Field(None)
    rejection_reason: str | None = Field(None)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, value: object) -> str:
        return str(value)


# ---------------------------------------------------------------------------
# 2. Audit Log Schemas (No Update Schema)
# ---------------------------------------------------------------------------

class AuditLogCreateRequest(BaseModel):
    """Payload for internal services to append to the audit ledger."""
    model_config = ConfigDict(str_strip_whitespace=True)

    performed_by: str = Field(...)
    action: str = Field(..., max_length=100)
    module: str = Field(..., max_length=50)
    entity_type: str = Field(..., max_length=50)
    entity_id: str | None = Field(None)
    old_data: dict | None = Field(None)
    new_data: dict | None = Field(None)
    ip_address: str | None = Field(None, max_length=50)
    device: str | None = Field(None, max_length=200)


class AuditLogResponse(BaseModel):
    """API response for an Audit Log entry."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(...)
    performed_by: str = Field(...)
    action: str = Field(...)
    module: str = Field(...)
    entity_type: str = Field(...)
    entity_id: str | None = Field(None)
    old_data: dict | None = Field(None)
    new_data: dict | None = Field(None)
    ip_address: str | None = Field(None)
    device: str | None = Field(None)
    created_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, value: object) -> str:
        return str(value)


# ---------------------------------------------------------------------------
# 3. App Settings Schemas
# ---------------------------------------------------------------------------

class AppSettingsUpdateRequest(BaseModel):
    """Payload to patch the global application configuration."""
    model_config = ConfigDict(str_strip_whitespace=True)

    platform_name: str | None = Field(None, max_length=100)
    support_email: EmailStr | None = Field(None)
    support_phone: str | None = Field(
        None, pattern=r"^\+?[1-9]\d{1,14}$", description="E.164 phone format"
    )
    minimum_app_version: str | None = Field(None, max_length=20)
    maintenance_mode: bool | None = Field(None)
    maintenance_message: str | None = Field(None, max_length=500)
    default_currency: str | None = Field(None, max_length=10)
    default_language: str | None = Field(None, max_length=10)
    firebase_enabled: bool | None = Field(None)
    notifications_enabled: bool | None = Field(None)
    inspection_enabled: bool | None = Field(None)
    pricing_enabled: bool | None = Field(None)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "AppSettingsUpdateRequest":
        provided = {k for k in self.model_fields if getattr(self, k) is not None}
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


class AppSettingsResponse(BaseModel):
    """API response for global application configuration."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(...)
    platform_name: str = Field(...)
    support_email: str = Field(...)
    support_phone: str = Field(...)
    minimum_app_version: str = Field(...)
    maintenance_mode: bool = Field(...)
    maintenance_message: str | None = Field(None)
    default_currency: str = Field(...)
    default_language: str = Field(...)
    firebase_enabled: bool = Field(...)
    notifications_enabled: bool = Field(...)
    inspection_enabled: bool = Field(...)
    pricing_enabled: bool = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, value: object) -> str:
        return str(value)


# ---------------------------------------------------------------------------
# 4. Banner Schemas
# ---------------------------------------------------------------------------

class BannerCreateRequest(BaseModel):
    """Payload to create a new marketing banner."""
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., max_length=150)
    description: str | None = Field(None, max_length=500)
    image_url: HttpUrl = Field(...)
    redirect_url: HttpUrl | None = Field(None)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    start_date: date | None = Field(None)
    end_date: date | None = Field(None)

    @field_validator("image_url", "redirect_url")
    @classmethod
    def convert_urls(cls, value: HttpUrl | None) -> str | None:
        if value:
            return str(value)
        return None

    @model_validator(mode="after")
    def validate_dates(self) -> "BannerCreateRequest":
        """Ensure start_date is before end_date."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        return self


class BannerUpdateRequest(BaseModel):
    """Payload to update an existing banner."""
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(None, max_length=150)
    description: str | None = Field(None, max_length=500)
    image_url: HttpUrl | None = Field(None)
    redirect_url: HttpUrl | None = Field(None)
    display_order: int | None = Field(None, ge=0)
    is_active: bool | None = Field(None)
    start_date: date | None = Field(None)
    end_date: date | None = Field(None)

    @field_validator("image_url", "redirect_url")
    @classmethod
    def convert_urls(cls, value: HttpUrl | None) -> str | None:
        if value:
            return str(value)
        return None

    @model_validator(mode="after")
    def validate_dates(self) -> "BannerUpdateRequest":
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date cannot be after end_date")
        return self
        
    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "BannerUpdateRequest":
        provided = {k for k in self.model_fields if getattr(self, k) is not None}
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


class BannerResponse(BaseModel):
    """API response for a Banner."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    image_url: str = Field(...)
    redirect_url: str | None = Field(None)
    display_order: int = Field(...)
    is_active: bool = Field(...)
    start_date: date | None = Field(None)
    end_date: date | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, value: object) -> str:
        return str(value)


# ---------------------------------------------------------------------------
# 5. Support Ticket Schemas
# ---------------------------------------------------------------------------

class SupportTicketCreateRequest(BaseModel):
    """Payload for a user (Customer/Worker) to open a new support ticket."""
    model_config = ConfigDict(str_strip_whitespace=True)

    category: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=200)
    description: str = Field(..., max_length=3000)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    attachments: list[HttpUrl] = Field(default_factory=list, max_length=5)

    @field_validator("attachments")
    @classmethod
    def convert_urls(cls, value: list[HttpUrl]) -> list[str]:
        return [str(url) for url in value]


class SupportTicketUpdateRequest(BaseModel):
    """Payload for an admin to update or resolve a support ticket."""
    model_config = ConfigDict(str_strip_whitespace=True)

    status: TicketStatus | None = Field(None)
    priority: TicketPriority | None = Field(None)
    assigned_admin: str | None = Field(None, description="Admin ObjectId")
    resolution: str | None = Field(None, max_length=3000)

    @model_validator(mode="after")
    def validate_resolution(self) -> "SupportTicketUpdateRequest":
        """Require a resolution text if the ticket is marked RESOLVED."""
        if self.status == TicketStatus.RESOLVED:
            if not self.resolution:
                raise ValueError("resolution is required when resolving a ticket")
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "SupportTicketUpdateRequest":
        provided = {k for k in self.model_fields if getattr(self, k) is not None}
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


class SupportTicketResponse(BaseModel):
    """API response for a Support Ticket."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(...)
    ticket_number: str = Field(...)
    user_id: str = Field(...)
    category: str = Field(...)
    subject: str = Field(...)
    description: str = Field(...)
    status: TicketStatus = Field(...)
    priority: TicketPriority = Field(...)
    assigned_admin: str | None = Field(None)
    attachments: list[str] = Field(...)
    resolution: str | None = Field(None)
    closed_at: datetime | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id(cls, value: object) -> str:
        return str(value)
