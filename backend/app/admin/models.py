"""
Admin & System module models — platform-level management and auditing.

Architecture:
    - Contains 5 distinct Beanie Documents: WorkerVerification, AuditLog,
      AppSettings, Banner, and SupportTicket.
    - These models are consolidated in the admin module because they represent
      platform-wide operations, moderation, and systemic configurations rather
      than user-facing transactional entities.

Why these models are separated:
    - WorkerVerification: Separated from WorkerProfile. The profile holds
      publicly facing data; Verification holds sensitive backend checks,
      document scans, and moderation notes.
    - AuditLog: A high-volume append-only collection. Must be separated from
      transactional collections to prevent performance degradation.
    - AppSettings: A singleton document for global toggles, decoupled from code
      to allow instant zero-deploy updates (e.g., turning on maintenance mode).
    - Banner: Marketing entities with distinct date-bounded lifecycles.
    - SupportTicket: Independent workflow for customer/worker issues.

Audit Logging Strategy:
    - Polymorphic linkage (`module`, `entity_type`, `entity_id`).
    - Stores `old_data` and `new_data` as flexible dicts to capture state
      transitions without strict schema limits.
    - Captures `ip_address` and `device` for security forensics.

Index Strategy:
    - WorkerVerification: `verification_status` for the moderation queue.
    - AuditLog: Highly indexed on `entity_type` + `entity_id` for fast timeline
      reconstruction, and `created_at` for pagination/archiving.
    - Banner: `is_active` + date ranges for active UI rendering.
    - SupportTicket: `status` + `priority` for support agent dashboards.

Future Scalability:
    - AuditLogs will grow massive. The schema allows for easy archiving/sharding
      based on `created_at`.
    - AppSettings singleton design prepares for distributed caching (Redis).
    - Support tickets support multi-agent assignment via `assigned_admin`.
"""

from datetime import date, datetime, timezone
from enum import Enum

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VerificationStatus(str, Enum):
    """Lifecycle of worker identity and skill verification."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class TicketStatus(str, Enum):
    """Lifecycle of a support or dispute ticket."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_USER = "waiting_for_user"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Urgency of a support ticket."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# 1. Worker Verification Document
# ---------------------------------------------------------------------------

class WorkerVerification(Document):
    """
    Moderation and verification state for a worker.
    Kept separate from WorkerProfile for security and isolation.
    """
    worker_id: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ..., description="Reference to Worker ObjectId"
    )
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.PENDING, description="Moderation state"
    )
    
    # E.g., {"aadhar": "url", "police_verification": "url", "certificate": "url"}
    submitted_documents: dict = Field(
        default_factory=dict, description="URLs to sensitive verification docs"
    )
    
    verified_by: str | None = Field(
        default=None, description="Admin User ObjectId who processed this"
    )
    verification_notes: str | None = Field(
        default=None, max_length=2000, description="Internal moderation notes"
    )
    rejection_reason: str | None = Field(
        default=None, max_length=1000, description="Reason shown to worker if rejected"
    )
    
    verified_at: datetime | None = Field(None, description="Approval timestamp")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "admin_worker_verifications"
        use_state_management = True
        indexes = [
            IndexModel([("verification_status", ASCENDING), ("created_at", ASCENDING)]),
            IndexModel([("verified_by", ASCENDING)]),
        ]


# ---------------------------------------------------------------------------
# 2. Audit Log Document
# ---------------------------------------------------------------------------

class AuditLog(Document):
    """
    Immutable ledger of critical actions performed across the platform.
    Append-only collection.
    """
    performed_by: str = Field(..., description="User ObjectId who took action")
    action: str = Field(..., max_length=100, description="E.g., 'UPDATE_PRICING'")
    module: str = Field(..., max_length=50, description="E.g., 'Pricing', 'Auth'")
    
    entity_type: str = Field(..., max_length=50, description="Target model name")
    entity_id: str | None = Field(None, description="Target document ObjectId")
    
    old_data: dict | None = Field(None, description="State before action")
    new_data: dict | None = Field(None, description="State after action")
    
    ip_address: str | None = Field(None, max_length=50, description="Origin IP")
    device: str | None = Field(None, max_length=200, description="User Agent/Device")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "admin_audit_logs"
        # use_state_management is false for append-only performance
        use_state_management = False
        indexes = [
            IndexModel([("performed_by", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("module", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("entity_type", ASCENDING), ("entity_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]


# ---------------------------------------------------------------------------
# 3. App Settings Document (Singleton)
# ---------------------------------------------------------------------------

class AppSettings(Document):
    """
    Global platform configuration.
    Only one document should ever exist in this collection.
    """
    platform_name: str = Field(default="Ally", max_length=100)
    support_email: str = Field(..., max_length=255)
    support_phone: str = Field(..., max_length=20)
    
    minimum_app_version: str = Field(default="1.0.0", max_length=20)
    maintenance_mode: bool = Field(default=False)
    maintenance_message: str | None = Field(None, max_length=500)
    
    default_currency: str = Field(default="INR", max_length=10)
    default_language: str = Field(default="en", max_length=10)
    
    firebase_enabled: bool = Field(default=True)
    notifications_enabled: bool = Field(default=True)
    inspection_enabled: bool = Field(default=True)
    pricing_enabled: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "admin_app_settings"
        use_state_management = True


# ---------------------------------------------------------------------------
# 4. Banner Document
# ---------------------------------------------------------------------------

class Banner(Document):
    """Marketing and informational banners for the mobile app home screen."""
    title: str = Field(..., max_length=150)
    description: str | None = Field(None, max_length=500)
    
    image_url: str = Field(..., max_length=512)
    redirect_url: str | None = Field(None, max_length=512)
    
    display_order: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    
    start_date: date | None = Field(None, description="Start displaying on")
    end_date: date | None = Field(None, description="Stop displaying on")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "admin_banners"
        use_state_management = True
        indexes = [
            IndexModel(
                [("is_active", ASCENDING), ("display_order", ASCENDING)],
                name="idx_active_order"
            ),
            IndexModel([("start_date", ASCENDING), ("end_date", ASCENDING)]),
        ]


# ---------------------------------------------------------------------------
# 5. Support Ticket Document
# ---------------------------------------------------------------------------

class SupportTicket(Document):
    """Customer or Worker support requests and disputes."""
    ticket_number: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ..., description="Human-readable ID (e.g. TKT-123)"
    )
    user_id: str = Field(..., description="User ObjectId who opened the ticket")
    
    category: str = Field(..., max_length=100, description="E.g., 'Billing', 'Worker Conduct'")
    subject: str = Field(..., max_length=200)
    description: str = Field(..., max_length=3000)
    
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    
    assigned_admin: str | None = Field(
        default=None, description="Admin User ObjectId"
    )
    attachments: list[str] = Field(
        default_factory=list, max_length=5, description="Image/PDF URLs"
    )
    
    resolution: str | None = Field(None, max_length=3000, description="Resolution notes")
    closed_at: datetime | None = Field(None)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "admin_support_tickets"
        use_state_management = True
        indexes = [
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("status", ASCENDING), ("priority", DESCENDING)]),
            IndexModel([("assigned_admin", ASCENDING), ("status", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
