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
# Booking Lifecycle
# ---------------------------------------------------------------------------

class BookingStatus(str, Enum):
    """
    Booking lifecycle states (Phase 4.7.1 Foundation).

    Flow:
        PENDING -> ASSIGNED / ACCEPTED -> WORKER_EN_ROUTE -> ARRIVED -> IN_PROGRESS -> WORK_COMPLETED -> CUSTOMER_CONFIRMED
               \-> CANCELLED
    """
    PENDING = "pending"                     # Created by customer, awaiting worker assignment
    ASSIGNED = "assigned"                   # Worker assigned / quotation accepted
    ACCEPTED = "accepted"                   # Alias for assigned (legacy compatibility)
    WORKER_EN_ROUTE = "worker_en_route"     # Worker traveling to customer location
    ARRIVED = "arrived"                     # Worker arrived at customer location
    IN_PROGRESS = "in_progress"             # Service execution in progress
    WORK_COMPLETED = "work_completed"       # Worker marked work as finished
    CUSTOMER_CONFIRMED = "customer_confirmed"# Customer confirmed work completion
    COMPLETED = "completed"                 # Legacy alias for completed
    CANCELLED = "cancelled"                 # Booking cancelled



class BookingType(str, Enum):
    """
    Type of booking the customer is making.

    NORMAL_SERVICE     — Standard fixed-price service booking.
                         Worker is dispatched and performs the service.
    PREDEFINED_SERVICE — Service from the catalog with predefined scope.
    INSPECTION_REQUEST — Customer requests a site visit for assessment
                         before committing to a full service. Results in a Quotation.
    CUSTOM_SERVICE     — Custom service request defined by customer.
    """
    NORMAL_SERVICE = "normal_service"
    PREDEFINED_SERVICE = "predefined_service"
    INSPECTION_REQUEST = "inspection_request"
    CUSTOM_SERVICE = "custom_service"


class InspectionStatus(str, Enum):
    """
    Canonical lifecycle states for Inspection Requests.
    """
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    SCHEDULED = "scheduled"
    VISIT_SCHEDULED = "visit_scheduled"
    IN_PROGRESS = "in_progress"
    VISITED = "visited"
    REPORT_READY = "report_ready"
    REPORT_SUBMITTED = "report_submitted"
    QUOTATION_PENDING = "quotation_pending"
    QUOTATION_GENERATED = "quotation_generated"
    QUOTATION_SUBMITTED = "quotation_submitted"
    CUSTOMER_APPROVED = "customer_approved"
    CUSTOMER_REJECTED = "customer_rejected"
    JOB_CREATED = "job_created"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Service Categories (DEPRECATED ENUM - DO NOT USE FOR WORKER MATCHING)
# ---------------------------------------------------------------------------

class ServiceCategory(str, Enum):
    """
    DEPRECATED string Enum for service categories.

    NOTE: Domain matching and category queries use the Beanie Document model
    `app.category.models.ServiceCategory` which is backed by the `service_categories`
    collection in MongoDB (slug-based matching). This Enum is kept for backward
    compatibility only.
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


class ApplicationStatus(str, Enum):
    """
    Worker job application states.

    PENDING   — Application submitted, awaiting customer/system review.
    ACCEPTED  — Application accepted for assignment.
    REJECTED  — Application rejected.
    WITHDRAWN — Application withdrawn by worker.
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Gender(str, Enum):
    """Gender options for user profiles."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class QuotationStatus(str, Enum):
    """
    Quotation lifecycle states.

    DRAFT     — Created by worker, not yet submitted.
    SUBMITTED — Submitted by worker, awaiting customer review.
    ACCEPTED  — Accepted by customer.
    REJECTED  — Rejected by customer.
    EXPIRED   — Passed validity_date without acceptance.
    CANCELLED — Cancelled by worker or system before acceptance.
    """
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class QuotationEventType(str, Enum):
    """
    Audit trail event types for quotation lifecycle.
    """
    CREATED = "created"
    UPDATED = "updated"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    WORKER_ASSIGNED = "worker_assigned"
