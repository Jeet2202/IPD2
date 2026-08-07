"""
Application configuration — single source of truth for all settings.

Architecture:
    - Uses pydantic-settings to load from .env and environment variables.
    - SecretStr prevents credentials from leaking into logs/tracebacks.
    - ENVIRONMENT field drives behavior (debug mode, docs visibility, CORS).
    - Optional fields for future integrations (JWT, Cloudinary, Firebase)
      so the app boots without them during early development.

Priority order:
    1. Environment variables (highest — Docker/CI/production)
    2. .env file (local development)
    3. Default values (fallback)
"""

from enum import Enum

from pydantic import Field, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.constants import JWT_SECRET_MIN_LENGTH


# ---------------------------------------------------------------------------
# Environment Enum
# ---------------------------------------------------------------------------

class Environment(str, Enum):
    """Deployment environment. Controls debug mode, docs, and CORS."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """
    Root configuration class.

    All settings are loaded from environment variables or .env file.
    Grouped logically with env_prefix for namespacing where needed.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    APP_NAME: str = "Service Marketplace"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["*"]
    TRUSTED_HOSTS: list[str] = ["*"]  # Restrict to your domain(s) in production
    GZIP_MINIMUM_SIZE: int = 500      # Compress responses larger than 500 bytes
    RATE_LIMIT_ENABLED: bool = False   # Enable when Redis backend is available
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # --- Logging ---
    LOG_LEVEL: str = "DEBUG"          # DEBUG in dev, INFO or WARNING in production
    LOG_JSON_FORMAT: bool = False     # True enables JSON logs + file rotation

    # --- Database (MongoDB Atlas) ---
    MONGODB_URI: SecretStr = SecretStr("mongodb://localhost:27017")
    MONGODB_DATABASE: str = "service_marketplace"
    MONGODB_MIN_POOL_SIZE: int = 0   # Pre-warmed connections (set 5-10 in production)
    MONGODB_MAX_POOL_SIZE: int = 100  # Max concurrent connections per process

    # --- JWT Authentication ---
    JWT_SECRET_KEY: SecretStr | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "ally"
    JWT_AUDIENCE: str = "ally-api"

    # --- Password Security ---
    BCRYPT_ROUNDS: int = 12  # Work factor: 4 for testing, 12 for production

    # --- Email Provider (Gmail SMTP / Resend / SendGrid) ---
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: SecretStr | None = None
    FROM_EMAIL: str = "noreply@ally.com"
    FROM_NAME: str = "Ally - AI Home Services"

    # --- OTP Configuration ---
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    OTP_MAX_RESEND: int = 3
    OTP_RESEND_COOLDOWN_SECONDS: int = 60
    REQUIRE_LOGIN_OTP: bool = False

    # --- Security, Account Locking & Sessions ---
    LOGIN_MAX_ATTEMPTS: int = 5
    ACCOUNT_LOCK_DURATION_MINUTES: int = 15
    MAX_ACTIVE_SESSIONS: int = 5
    AUDIT_RETENTION_DAYS: int = 90

    # --- Cloudinary ---
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: SecretStr | None = None
    CLOUDINARY_API_SECRET: SecretStr | None = None
    CLOUDINARY_FOLDER: str = "ally/profile_pictures"

    # --- Booking & Scheduling Configuration ---
    BOOKING_BUSINESS_START_HOUR: int = 8       # 08:00 AM
    BOOKING_BUSINESS_END_HOUR: int = 20        # 08:00 PM
    BOOKING_SLOT_DURATION_MINUTES: int = 120   # 2-hour slots
    BOOKING_MAX_ADVANCE_DAYS: int = 60          # 60 days max booking window
    BOOKING_SAME_DAY_BUFFER_HOURS: int = 1     # 1 hour minimum lead time for today's slots

    # --- Quotation Configuration ---
    QUOTATION_DEFAULT_VALIDITY_DAYS: int = 14
    QUOTATION_MAX_VALIDITY_DAYS: int = 90
    QUOTATION_MIN_PRICE: float = 0.0
    QUOTATION_MAX_PRICE: float = 500000.0
    QUOTATION_DEFAULT_TAX_RATE: float = 0.0

    # --- Firebase (activate when notifications module is built) ---
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # --- Razorpay Payment Gateway ---
    RAZORPAY_KEY_ID: str = ""                              # rzp_test_... or rzp_live_...
    RAZORPAY_KEY_SECRET: SecretStr = SecretStr("")         # Keep secret — never expose
    RAZORPAY_WEBHOOK_SECRET: SecretStr = SecretStr("")     # Webhook signing secret
    INSPECTION_FEE: float = 99.0                           # ₹99 diagnostic visit charge

    # --- Socket.IO Configuration ---
    SOCKET_CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    SOCKET_MESSAGE_QUEUE: str | None = None  # e.g., "redis://localhost:6379/0"

    # --- Computed Properties ---

    @computed_field
    @property
    def is_production(self) -> bool:
        """True when running in production. Use for conditional logic."""
        return self.ENVIRONMENT == Environment.PRODUCTION

    @computed_field
    @property
    def docs_url(self) -> str | None:
        """Disable Swagger UI in production for security."""
        if self.is_production:
            return None
        return "/docs"

    @computed_field
    @property
    def redoc_url(self) -> str | None:
        """Disable ReDoc in production for security."""
        if self.is_production:
            return None
        return "/redoc"

    # --- Validation ---

    @model_validator(mode="after")
    def validate_required_secrets(self) -> "Settings":
        """
        Enforce that critical secrets are set in production.

        In development/staging, missing secrets are allowed so the app
        can boot without full infrastructure. In production, missing
        secrets cause an immediate startup crash — fail fast.
        """
        missing: list[str] = []

        if self.JWT_SECRET_KEY is None:
            missing.append("JWT_SECRET_KEY")
        else:
            jwt_secret = self.JWT_SECRET_KEY.get_secret_value().strip()
            if not jwt_secret:
                missing.append("JWT_SECRET_KEY")
            elif len(jwt_secret) < JWT_SECRET_MIN_LENGTH:
                missing.append(
                    f"JWT_SECRET_KEY (minimum {JWT_SECRET_MIN_LENGTH} characters)"
                )
            else:
                self.JWT_SECRET_KEY = SecretStr(jwt_secret)

        if missing:
            raise ValueError(
                f"Authentication requires these environment variables: "
                f"{', '.join(missing)}"
            )

        if self.ENVIRONMENT != Environment.PRODUCTION:
            return self

        production_missing: list[str] = []

        # Database URI must not be the localhost default
        if self.MONGODB_URI.get_secret_value() == "mongodb://localhost:27017":
            production_missing.append("MONGODB_URI")

        # Cloudinary is required for media uploads in production
        if not self.CLOUDINARY_CLOUD_NAME:
            production_missing.append("CLOUDINARY_CLOUD_NAME")
        if not self.CLOUDINARY_API_KEY:
            production_missing.append("CLOUDINARY_API_KEY")
        if not self.CLOUDINARY_API_SECRET:
            production_missing.append("CLOUDINARY_API_SECRET")

        # Firebase is required for push notifications in production
        if not self.FIREBASE_CREDENTIALS_PATH:
            production_missing.append("FIREBASE_CREDENTIALS_PATH")

        # Razorpay is required for payments in production
        if not self.RAZORPAY_KEY_ID or not self.RAZORPAY_KEY_ID.startswith("rzp_live"):
            production_missing.append("RAZORPAY_KEY_ID (must be rzp_live_... in production)")
        if not self.RAZORPAY_KEY_SECRET.get_secret_value():
            production_missing.append("RAZORPAY_KEY_SECRET")
        if not self.RAZORPAY_WEBHOOK_SECRET.get_secret_value():
            production_missing.append("RAZORPAY_WEBHOOK_SECRET")

        # CORS origins must be restricted (not open wildcard) in production
        if "*" in self.ALLOWED_ORIGINS:
            production_missing.append(
                "ALLOWED_ORIGINS (must not be ['*'] in production — set to your domain list)"
            )

        if production_missing:
            raise ValueError(
                f"Production requires these environment variables: "
                f"{', '.join(production_missing)}"
            )

        return self


# ---------------------------------------------------------------------------
# Singleton — import this, not the class
# ---------------------------------------------------------------------------

settings = Settings()
