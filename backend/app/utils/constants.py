"""
Application-wide constants.

Single source of truth for regex patterns, limits, and default values
used across multiple feature modules. Import from here instead of
hardcoding values in business logic.

Naming convention:
    - Regex patterns: *_REGEX
    - Limits: MAX_*, MIN_*
    - Defaults: DEFAULT_*
"""

import re


# ---------------------------------------------------------------------------
# Regex Patterns (pre-compiled for performance)
# ---------------------------------------------------------------------------

# Indian phone: +91 followed by 10 digits starting with 6-9.
# Used by validators.py and auth module for phone-based registration.
PHONE_REGEX = re.compile(r"^\+91[6-9]\d{9}$")

# MongoDB ObjectId: exactly 24 hex characters.
# Used to validate path parameters and foreign key references.
OBJECT_ID_REGEX = re.compile(r"^[0-9a-fA-F]{24}$")

# Slug: lowercase letters, digits, and hyphens. 3-60 chars.
# Used for URL-friendly service names and worker slugs.
SLUG_REGEX = re.compile(r"^[a-z0-9][a-z0-9-]{1,58}[a-z0-9]$")

# PIN code: exactly 6 digits (Indian postal code).
PIN_CODE_REGEX = re.compile(r"^\d{6}$")

# OTP: exactly 6 digits.
OTP_REGEX = re.compile(r"^\d{6}$")


# ---------------------------------------------------------------------------
# String Length Limits
# ---------------------------------------------------------------------------

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

MAX_DESCRIPTION_LENGTH = 2000
MAX_SHORT_DESCRIPTION_LENGTH = 500
MAX_ADDRESS_LENGTH = 500

MAX_REVIEW_LENGTH = 1000
MAX_TITLE_LENGTH = 200


# ---------------------------------------------------------------------------
# File Upload Limits
# ---------------------------------------------------------------------------

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024        # 10 MB
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024         # 5 MB
MAX_UPLOAD_FILES_PER_REQUEST = 5
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}


# ---------------------------------------------------------------------------
# Pagination Defaults
# ---------------------------------------------------------------------------

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# ---------------------------------------------------------------------------
# Business Constants
# ---------------------------------------------------------------------------

# OTP expiry in seconds (5 minutes)
OTP_EXPIRY_SECONDS = 300

# Maximum failed OTP attempts before lockout
MAX_OTP_ATTEMPTS = 5

# OTP lockout duration in seconds (15 minutes)
OTP_LOCKOUT_SECONDS = 900

# Maximum active jobs per worker at one time
MAX_ACTIVE_JOBS_PER_WORKER = 5

# Minimum hours before scheduled job start for cancellation
MIN_CANCELLATION_HOURS = 2

# Review window: days after job completion to leave a review
REVIEW_WINDOW_DAYS = 30

# Maximum radius in kilometers for location-based worker search
MAX_SEARCH_RADIUS_KM = 50
DEFAULT_SEARCH_RADIUS_KM = 10
