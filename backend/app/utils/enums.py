"""
Business domain enums — shared across feature modules.

These represent the possible states and categories for domain objects.
Stored as string values in MongoDB for readability. Used in Pydantic
schemas for validation and in service logic for state transitions.

Note: Environment lives in app/core/config.py (it's config).
All other enums — domain, authentication, and business — live here.

Naming convention:
    - Enum names: PascalCase, singular (JobStatus, not JobStatuses)
    - Values: lowercase snake_case (matches MongoDB storage)
"""

from enum import Enum


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    """
    User roles in the marketplace.

    Used by auth guards to restrict route access by role.
    Maps directly to the role field stored in the user document.
    """
    CUSTOMER = "customer"
    WORKER = "worker"
    ADMIN = "admin"


class TokenType(str, Enum):
    """JWT token type identifiers embedded in the token payload."""
    ACCESS = "access"
    REFRESH = "refresh"


# ---------------------------------------------------------------------------
# Job Lifecycle
# ---------------------------------------------------------------------------

class JobStatus(str, Enum):
    """
    Job lifecycle states.

    Flow: PENDING -> ACCEPTED -> IN_PROGRESS -> COMPLETED
                  \-> CANCELLED (from PENDING or ACCEPTED)
    """
    PENDING = "pending"             # Customer created, waiting for worker
    ACCEPTED = "accepted"           # Worker accepted the job
    IN_PROGRESS = "in_progress"     # Worker started working
    COMPLETED = "completed"         # Job finished successfully
    CANCELLED = "cancelled"         # Cancelled by customer or system


class JobType(str, Enum):
    """Whether the job is on-demand or scheduled for a future date."""
    ON_DEMAND = "on_demand"
    SCHEDULED = "scheduled"


# ---------------------------------------------------------------------------
# Service Categories
# ---------------------------------------------------------------------------

class ServiceCategory(str, Enum):
    """
    Blue-collar service categories offered on the marketplace.

    Each category maps to a set of workers with matching skills.
    Add new categories here as the platform expands.
    """
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    PAINTER = "painter"
    CARPENTER = "carpenter"
    CLEANER = "cleaner"
    AC_TECHNICIAN = "ac_technician"
    APPLIANCE_REPAIR = "appliance_repair"
    PEST_CONTROL = "pest_control"
    MASON = "mason"
    GARDENER = "gardener"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

class PaymentStatus(str, Enum):
    """Payment lifecycle states."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    WALLET = "wallet"


# ---------------------------------------------------------------------------
# Verification & Approval
# ---------------------------------------------------------------------------

class VerificationStatus(str, Enum):
    """Worker identity/document verification states."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class InspectionStatus(str, Enum):
    """Inspection lifecycle states."""
    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationType(str, Enum):
    """Types of notifications sent to users."""
    JOB_CREATED = "job_created"
    JOB_ACCEPTED = "job_accepted"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_CANCELLED = "job_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    REVIEW_RECEIVED = "review_received"
    WORKER_ASSIGNED = "worker_assigned"
    INSPECTION_SCHEDULED = "inspection_scheduled"
    ACCOUNT_VERIFIED = "account_verified"
    SYSTEM = "system"


class NotificationChannel(str, Enum):
    """Delivery channels for notifications."""
    IN_APP = "in_app"
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

class WorkerAvailability(str, Enum):
    """Worker's current availability status."""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class Gender(str, Enum):
    """Gender options for user profiles."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
