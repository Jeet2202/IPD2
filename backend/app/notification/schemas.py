"""
Request/response schemas for the Notification module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict bounds checking for text lengths and future expiry dates.
    - Polymorphic entity relationships handled via generic string fields.
    - `NotificationMetadataSchema` uses `extra="allow"` to permit arbitrary
      payload injection for Firebase Cloud Messaging without requiring
      backend schema migrations for every new mobile app feature.

Design decisions:
    - `NotificationCreateRequest` is heavily used by internal system services
      (e.g., JobService dispatches a "Worker Arrived" notification).
    - `NotificationUpdateRequest` is primarily for tracking read status
      (`is_read = True`) when the user opens the app, and delivery statuses
      updated by background push worker queues.
"""

from datetime import datetime, timezone

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from app.notification.models import DeliveryStatus, NotificationPriority, NotificationType


# ---------------------------------------------------------------------------
# Embedded Component Schemas
# ---------------------------------------------------------------------------

class NotificationMetadataSchema(BaseModel):
    """
    Flexible metadata object for push notification payloads.

    Configured with `extra="allow"`, meaning clients and backend services
    can inject arbitrary key-value pairs (e.g., `job_id`, `tracking_url`,
    `discount_code`) without needing to update this schema. This perfectly
    matches the requirements of Firebase Cloud Messaging (FCM) data payloads.
    """

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    # Optional known keys for documentation purposes
    entity_id: str | None = Field(None, description="Primary related entity ID")
    action_intent: str | None = Field(None, description="Mobile app routing intent")


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class NotificationCreateRequest(BaseModel):
    """
    Payload for dispatching a new notification.

    Typically invoked by internal services (JobService, PaymentService),
    but can also be used by Admin dashboards for promotional blasts.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="Target User ObjectId")
    title: str = Field(..., min_length=2, max_length=150, description="Headline")
    message: str = Field(..., min_length=2, max_length=1000, description="Body content")
    
    notification_type: NotificationType = Field(..., description="Categorization")
    priority: NotificationPriority = Field(
        default=NotificationPriority.NORMAL, description="Delivery priority"
    )

    # --- Polymorphic Relations ---
    related_entity_type: str | None = Field(
        None, max_length=50, description="E.g., 'Job', 'ServiceRequest'"
    )
    related_entity_id: str | None = Field(
        None, description="Specific document ObjectId"
    )

    # --- Rich Media & Routing ---
    image_url: HttpUrl | None = Field(
        None, description="Image for rich push (must be valid HTTP URL)"
    )
    action_url: str | None = Field(
        None, max_length=512, description="Deep-link routing URL"
    )

    # --- Metadata & Lifecycle ---
    metadata: NotificationMetadataSchema = Field(
        default_factory=NotificationMetadataSchema,
        description="Flexible data payload for FCM"
    )
    expires_at: datetime | None = Field(
        None, description="Auto-deletion timestamp"
    )

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, value: HttpUrl | None) -> str | None:
        """Convert HttpUrl object to plain string for storage."""
        if value:
            return str(value)
        return None

    @field_validator("expires_at")
    @classmethod
    def validate_future_expiry(cls, value: datetime | None) -> datetime | None:
        """Ensure expiry date is firmly in the future."""
        if value is not None:
            now = datetime.now(timezone.utc)
            if value <= now:
                raise ValueError("expires_at must be a future timestamp")
        return value


class NotificationUpdateRequest(BaseModel):
    """
    Partial update for an existing notification.
    
    Used by:
      - Client App: Marking as read (`is_read=True`).
      - Push Workers: Updating `delivery_status` and `sent_push`.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # In-App State
    is_read: bool | None = Field(None, description="Mark as read")
    
    # Push Worker State
    sent_push: bool | None = Field(None, description="Push attempt status")
    delivery_status: DeliveryStatus | None = Field(None, description="External delivery state")
    
    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "NotificationUpdateRequest":
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

class NotificationResponse(BaseModel):
    """
    Complete Notification representation for API responses.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Notification ID")
    notification_number: str = Field(..., description="Human-readable ID")
    user_id: str = Field(..., description="Target User ID")
    
    title: str = Field(..., description="Headline")
    message: str = Field(..., description="Body content")
    notification_type: NotificationType = Field(..., description="Categorization")
    priority: NotificationPriority = Field(..., description="Delivery priority")
    
    related_entity_type: str | None = Field(None, description="Polymorphic type")
    related_entity_id: str | None = Field(None, description="Polymorphic ID")
    
    image_url: str | None = Field(None, description="Image URL")
    action_url: str | None = Field(None, description="Deep-link URL")
    
    is_read: bool = Field(..., description="Read status")
    read_at: datetime | None = Field(None, description="Read timestamp")
    
    sent_push: bool = Field(..., description="Push attempt status")
    push_sent_at: datetime | None = Field(None, description="Push timestamp")
    delivery_status: DeliveryStatus = Field(..., description="Delivery state")
    
    metadata: dict = Field(..., description="Flexible payload dict")
    expires_at: datetime | None = Field(None, description="TTL timestamp")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        return str(value)
