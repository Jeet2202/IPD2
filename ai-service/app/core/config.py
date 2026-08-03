import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    LOGGING_LEVEL: str = "INFO"

    # MongoDB — env vars are MONGODB_URI / MONGODB_DATABASE (matching .env)
    MONGODB_URI: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    MONGODB_DATABASE: str = Field(default="kaamsetu_db", alias="MONGODB_DATABASE")

    # Backwards-compat aliases used throughout the existing codebase
    # These just read from the same env vars
    @property
    def MONGO_URI(self) -> str:
        return self.MONGODB_URI

    @property
    def DATABASE_NAME(self) -> str:
        return self.MONGODB_DATABASE

    # Backend
    BACKEND_BASE_URL: str = Field(default="http://localhost:8000")
    REQUEST_TIMEOUT: float = Field(default=10.0)

    # Third Party
    GROQ_API_KEY: str = Field(default="")

    # File System
    MODEL_DIRECTORY: str = Field(default="./trained_models")
    DATASET_DIRECTORY: str = Field(default="./datasets")

    # Security / API
    # NOTE: Default is ["*"] for development only. Set explicit origins in production.
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # Recommendation Engine
    WEIGHT_DISTANCE: float = Field(default=0.30)
    WEIGHT_RATING: float = Field(default=0.20)
    WEIGHT_EXPERIENCE: float = Field(default=0.20)
    WEIGHT_COMPLETION: float = Field(default=0.15)
    WEIGHT_AVAILABILITY: float = Field(default=0.0)
    WEIGHT_RESPONSE_TIME: float = Field(default=0.15)

    MAX_SEARCH_RADIUS_KM: float = Field(default=50.0)
    MIN_WORKER_RATING: float = Field(default=3.0)
    MAX_RECOMMENDATIONS: int = Field(default=20)

    # Search Engine
    EMBEDDING_MODEL_NAME: str = Field(default="all-MiniLM-L6-v2")
    WEIGHT_SEMANTIC: float = Field(default=0.60)
    WEIGHT_KEYWORD: float = Field(default=0.30)
    WEIGHT_POPULARITY: float = Field(default=0.10)
    SEARCH_HISTORY_COLLECTION: str = Field(default="search_history")

    # Smart Pricing Engine
    PRICE_WEIGHT_BASE: float = Field(default=0.40)
    PRICE_WEIGHT_HISTORICAL: float = Field(default=0.30)
    PRICE_WEIGHT_DEMAND: float = Field(default=0.15)
    PRICE_WEIGHT_URGENCY: float = Field(default=0.05)
    PRICE_WEIGHT_WEEKEND: float = Field(default=0.05)
    PRICE_WEIGHT_COMPLEXITY: float = Field(default=0.05)

    PRICE_MULTIPLIER_WEEKEND: float = Field(default=1.15)
    PRICE_MULTIPLIER_HOLIDAY: float = Field(default=1.25)
    PRICE_MULTIPLIER_URGENT: float = Field(default=1.20)

    DEMAND_MULTIPLIER_PEAK: float = Field(default=1.30)
    DEMAND_MULTIPLIER_HIGH: float = Field(default=1.10)
    DEMAND_MULTIPLIER_LOW: float = Field(default=0.90)

    OUTLIER_STD_DEV_THRESHOLD: float = Field(default=2.0)
    MAX_PRICE_VARIANCE_PERCENT: float = Field(default=50.0)

    # Search query sanity limits
    MAX_QUERY_LENGTH: int = Field(default=500)

    # Phase 5.5 - AI Assistant Platform
    ASSISTANT_LLM_MODEL: str = "llama-3.1-8b-instant"
    ASSISTANT_MAX_TURNS: int = 20
    ASSISTANT_SUMMARY_THRESHOLD: int = 10
    ASSISTANT_MAX_TOKENS: int = 1024
    ASSISTANT_TEMPERATURE: float = 0.1
    ASSISTANT_SESSION_TTL_HOURS: int = 24
    
    ASSISTANT_FAQ_COLLECTION: str = "assistant_faqs"
    ASSISTANT_POLICY_COLLECTION: str = "assistant_policies"
    ASSISTANT_SESSION_COLLECTION: str = "assistant_sessions"
    ASSISTANT_TURN_COLLECTION: str = "assistant_turns"
    ASSISTANT_TOP_K_KNOWLEDGE: int = 3

    # Phase 5.6 - Analytics & Data Intelligence
    ANALYTICS_DATASET_EXPORT_DIR: str = "./datasets/exports"
    ANALYTICS_DASHBOARD_CACHE_TTL_SEC: int = 300 # 5 minutes default

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,  # Allow field name OR alias
    )

settings = Settings()
