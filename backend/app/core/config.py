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

    # --- JWT Authentication (activate when auth module is built) ---
    JWT_SECRET_KEY: SecretStr | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Cloudinary (activate when uploads module is built) ---
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: SecretStr | None = None
    CLOUDINARY_API_SECRET: SecretStr | None = None

    # --- Firebase (activate when notifications module is built) ---
    FIREBASE_CREDENTIALS_PATH: str | None = None

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
    def validate_production_secrets(self) -> "Settings":
        """
        Enforce that critical secrets are set in production.

        In development/staging, missing secrets are allowed so the app
        can boot without full infrastructure. In production, missing
        secrets cause an immediate startup crash — fail fast.
        """
        if self.ENVIRONMENT != Environment.PRODUCTION:
            return self

        missing: list[str] = []

        # Database URI must not be the localhost default
        if self.MONGODB_URI.get_secret_value() == "mongodb://localhost:27017":
            missing.append("MONGODB_URI")

        # JWT is mandatory in production (auth must work)
        if self.JWT_SECRET_KEY is None:
            missing.append("JWT_SECRET_KEY")

        if missing:
            raise ValueError(
                f"Production requires these environment variables: "
                f"{', '.join(missing)}"
            )

        return self


# ---------------------------------------------------------------------------
# Singleton — import this, not the class
# ---------------------------------------------------------------------------

settings = Settings()
