"""
Booking Lifecycle Centralized Configuration & Business Rules (Phase 4.7.5).

Centralizes:
- Allowed status transition matrix
- Terminal booking statuses
- Cancellation rules
- Future operational timeout / auto-confirmation settings
"""

from app.utils.enums import BookingStatus


class BookingLifecycleConfig:
    """Centralized governance configuration for booking lifecycle transitions."""

    # Explicit State Machine Matrix (Forward-only, non-skipping transitions)
    ALLOWED_TRANSITIONS: dict[BookingStatus, list[BookingStatus]] = {
        BookingStatus.PENDING: [
            BookingStatus.ASSIGNED,
            BookingStatus.ACCEPTED,
            BookingStatus.CANCELLED,
        ],
        BookingStatus.ASSIGNED: [
            BookingStatus.WORKER_EN_ROUTE,
            BookingStatus.CANCELLED,
        ],
        BookingStatus.ACCEPTED: [
            BookingStatus.WORKER_EN_ROUTE,
            BookingStatus.CANCELLED,
        ],
        BookingStatus.WORKER_EN_ROUTE: [
            BookingStatus.ARRIVED,
            BookingStatus.CANCELLED,
        ],
        BookingStatus.ARRIVED: [
            BookingStatus.IN_PROGRESS,
            BookingStatus.CANCELLED,
        ],
        BookingStatus.IN_PROGRESS: [
            BookingStatus.WORK_COMPLETED,
        ],
        BookingStatus.WORK_COMPLETED: [
            BookingStatus.CUSTOMER_CONFIRMED,
            BookingStatus.COMPLETED,
        ],
        BookingStatus.CUSTOMER_CONFIRMED: [],
        BookingStatus.COMPLETED: [],
        BookingStatus.CANCELLED: [],
    }

    # Terminal Statuses — Immutability Lock Active
    TERMINAL_STATUSES: set[BookingStatus] = {
        BookingStatus.CUSTOMER_CONFIRMED,
        BookingStatus.COMPLETED,
        BookingStatus.CANCELLED,
    }

    # Statuses eligible for cancellation
    CANCELLATION_ALLOWED_STATUSES: set[BookingStatus] = {
        BookingStatus.PENDING,
        BookingStatus.ASSIGNED,
        BookingStatus.ACCEPTED,
        BookingStatus.WORKER_EN_ROUTE,
        BookingStatus.ARRIVED,
    }

    # Centralized Operational Config (Prepared for future modules)
    CANCELLATION_FREE_WINDOW_MINUTES: int = 15
    AUTO_CONFIRMATION_DELAY_HOURS: int = 24
    MAX_ATTACHED_PHOTOS: int = 5
