"""
MongoDB connection lifecycle manager.

Responsibilities:
    - Async connect/disconnect with Motor (async driver) and Beanie (ODM).
    - Connection pool configuration via environment variables.
    - Startup verification (ping) to fail fast if Atlas is unreachable.
    - Health check for load balancers and monitoring.
    - FastAPI dependency for raw database access.

Design decisions:
    - No wrapper class around Motor — AsyncIOMotorClient IS the pool.
    - Module-level _client keeps lifecycle simple and importable.
    - Ping on connect ensures we don't silently start without a database.
"""

import logging
from typing import TYPE_CHECKING

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

if TYPE_CHECKING:
    from beanie import Document

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Private state
# ---------------------------------------------------------------------------

_client: AsyncIOMotorClient | None = None


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

async def connect_to_database(document_models: list[type["Document"]] | None = None) -> None:
    """
    Initialize Motor client with connection pooling and Beanie ODM.

    Called from FastAPI lifespan on startup. Pings the server after
    connecting to verify reachability — crashes immediately if Atlas
    is down rather than failing silently on first request.

    Args:
        document_models: Beanie Document subclasses to register.
                         Pass empty list during project init phase.
                         Add models as feature modules are built.
    """
    global _client

    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI.get_secret_value(),
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=5000,
        )

        # Verify connectivity — fail fast if Atlas is unreachable.
        await _client.admin.command("ping")
        logger.info(
            "MongoDB connected — database=%s, pool=%d-%d",
            settings.MONGODB_DATABASE,
            settings.MONGODB_MIN_POOL_SIZE,
            settings.MONGODB_MAX_POOL_SIZE,
        )

        await init_beanie(
            database=_client[settings.MONGODB_DATABASE],
            document_models=document_models or [],
            allow_index_dropping=True,
        )
        logger.info("Beanie ODM initialized with %d document model(s).", len(document_models or []))
    except Exception as exc:
        logger.error(
            "MongoDB connection failed! Check MONGODB_URI, credentials, and IP allowlist in Atlas.\n"
            "Error detail: %s",
            exc,
        )
        if _client is not None:
            _client.close()
            _client = None
        raise RuntimeError(
            f"Failed to connect to MongoDB Atlas [{settings.MONGODB_DATABASE}]: {exc}. "
            "Please verify that MONGODB_URI is well-formed, credentials are correct, "
            "and your IP address is whitelisted in MongoDB Atlas Network Access."
        ) from exc



async def close_database_connection() -> None:
    """
    Close the Motor client and release all pooled connections.

    Called from FastAPI lifespan on shutdown. Safe to call multiple
    times — no-ops if already closed.
    """
    global _client

    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed.")


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

def get_client() -> AsyncIOMotorClient:
    """
    Return the active Motor client.

    Raises:
        RuntimeError: If called before connect_to_database().
    """
    if _client is None:
        raise RuntimeError(
            "Database client is not initialized. "
            "Ensure connect_to_database() was called during app startup."
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency — returns the active database instance.

    Usage in routers:
        from app.database.connection import get_database

        @router.get("/stats")
        async def stats(db: AsyncIOMotorDatabase = Depends(get_database)):
            result = await db.command("dbStats")
            return result

    For normal CRUD, use Beanie Document methods directly — no dependency needed.
    """
    return get_client()[settings.MONGODB_DATABASE]


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

async def check_database_health() -> dict:
    """
    Ping MongoDB and return connection health status.

    Returns a dict with:
        - status: "connected" or "disconnected"
        - database: database name
        - pool: pool size configuration

    Used by the /health endpoint for load balancer and monitoring checks.
    """
    if _client is None:
        return {"status": "disconnected"}

    try:
        result = await _client.admin.command("ping")
        return {
            "status": "connected" if result.get("ok") == 1.0 else "error",
            "database": settings.MONGODB_DATABASE,
            "pool": {
                "min": settings.MONGODB_MIN_POOL_SIZE,
                "max": settings.MONGODB_MAX_POOL_SIZE,
            },
        }
    except Exception as exc:
        logger.error("MongoDB health check failed: %s", exc)
        return {
            "status": "error",
            "detail": str(exc),
        }
