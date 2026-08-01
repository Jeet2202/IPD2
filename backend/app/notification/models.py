"""
Notification module models — centralized communication system for KaamSetu.

Architecture:
    - Single Beanie Document: Notification.
    - Represents both in-app notification center items and external push records.
    - Polymorphic relations: `related_entity_type` + `related_entity_id` allow
      a single collection to link dynamically to Jobs, Payments, Reviews, etc.

Database design:
    - Massive write volume: Notifications are written frequently (e.g., status 
      changes). The schema is flat and heavily indexed for fast retrieval.
    - Expiring Data: The `expires_at` TTL (Time-To-Live) index automatically
      cleans up old promotional or low-priority notifications to prevent
      database bloat over time.

Metadata strategy:
    - The `metadata` dict is a flexible JSON payload that matches Firebase FCM
      data payload requirements. It allows sending complex routing instructions
      (e.g., opening a specific screen with specific IDs) to the mobile app
      without altering the core schema.

Index strategy:
    - user_id + created_at: The primary timeline query ("My Notifications").
    - user_id + is_read: O(1) unread badge count calculation.
    - delivery_status + priority: Background worker queue querying (finding
      unsent high-priority push notifications).
    - expires_at: Automated TTL cleanup by MongoDB.

Scalability considerations:
    - As notifications scale to millions of rows, the schema avoids any
      Beanie Links. Linking is done at the application layer using string IDs.
    - Push statuses (sent_push, push_sent_at) allow the backend to retry failed
      FCM deliveries without losing track of what was sent.

Collection name: "notifications" (explicit, lowercase, plural).
"""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NotificationType(str, Enum):
    """Categorization of notification intent."""
    ACCOUNT = "account"
    BOOKING = "booking"
    JOB = "job"
    INSPECTION = "inspection"
    PAYMENT = "payment"
    REVIEW = "review"
    PROMOTION = "promotion"
    SYSTEM = "system"
    ADMIN = "admin"
    VERIFICATION = "verification"


class NotificationPriority(str, Enum):
    """
    Dispatch priority.
    - URGENT/HIGH: Dispatched immediately via push/SMS.
    - NORMAL: Standard push.
    - LOW: Silent or in-app only.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class DeliveryStatus(str, Enum):
    """External delivery (Push/FCM/Email) status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Notification Document
# ---------------------------------------------------------------------------

class Notification(Document):
    """
    Centralized user notification record.

    Attributes:
        notification_number: Human-readable ID (e.g., NOT-2023-XXXX).
        user_id: Target user (Customer, Worker, or Admin).
        title: Short headline.
        message: Detailed body content.
        notification_type: Classification.
        priority: Delivery priority queue.

        related_entity_type: E.g., "Job", "ServiceRequest".
        related_entity_id: The specific document ObjectId.

        image_url: Optional image for rich push notifications.
        action_url: Deep-link URL for the mobile app or web.

        is_read: True if the user opened the notification.
        read_at: Timestamp of reading.

        sent_push: True if the external push (FCM) was attempted.
        push_sent_at: Timestamp of the push attempt.
        delivery_status: State of external delivery.

        metadata: Flexible JSON payload matching FCM data constraints.
        expires_at: TTL index field for auto-deletion of old records.
    """

    # --- Identity & Targeting ---
    notification_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        description="Human-readable unique ID",
        examples=["NOT-1725184000-A1B2"],
    )
    user_id: str = Field(..., description="Target User ObjectId")

    # --- Content ---
    title: str = Field(..., max_length=150, description="Short headline")
    message: str = Field(..., max_length=1000, description="Detailed body")
    notification_type: NotificationType = Field(
        ..., description="Categorization"
    )
    priority: NotificationPriority = Field(
        default=NotificationPriority.NORMAL, description="Delivery priority queue"
    )

    # --- Polymorphic Relation ---
    related_entity_type: str | None = Field(
        default=None, max_length=50, description="E.g., 'Job', 'Payment'"
    )
    related_entity_id: str | None = Field(
        default=None, description="The specific document ObjectId"
    )

    # --- Rich Media & Routing ---
    image_url: str | None = Field(
        default=None, max_length=512, description="Image for rich push"
    )
    action_url: str | None = Field(
        default=None, max_length=512, description="Deep-link routing URL"
    )

    # --- In-App State ---
    is_read: bool = Field(default=False, description="Has user read this?")
    read_at: datetime | None = Field(
        default=None, description="Timestamp when read"
    )

    # --- External Delivery (Push/FCM) ---
    sent_push: bool = Field(
        default=False, description="Was external push attempted?"
    )
    push_sent_at: datetime | None = Field(
        default=None, description="Timestamp of push attempt"
    )
    delivery_status: DeliveryStatus = Field(
        default=DeliveryStatus.PENDING, description="State of external delivery"
    )

    # --- Extensibility & Lifecycle ---
    metadata: dict = Field(
        default_factory=dict, description="Flexible FCM data payload"
    )
    expires_at: datetime | None = Field(
        default=None, description="TTL cleanup timestamp"
    )
    
    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "notifications"
        use_state_management = True

        indexes = [
            # User Timeline & Unread Badge
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("is_read", ASCENDING)]),
            
            # Background Worker Queues (finding unsent/failed pushes)
            IndexModel([("delivery_status", ASCENDING), ("priority", DESCENDING)]),
            
            # Analytics & Filtering
            IndexModel([("notification_type", ASCENDING), ("created_at", DESCENDING)]),
            
            # Polymorphic lookups
            IndexModel([("related_entity_id", ASCENDING)]),
            
            # MongoDB TTL Index for automatic cleanup of expired notifications
            IndexModel(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=0,
                name="ttl_expires_at"
            ),
        ]
