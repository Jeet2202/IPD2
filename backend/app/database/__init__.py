"""
Database package — MongoDB connection lifecycle and access.

Public API:
    connect_to_database()       — Call in FastAPI lifespan startup.
    close_database_connection() — Call in FastAPI lifespan shutdown.
    get_database()              — FastAPI Depends() for raw database access.
    get_client()                — Direct Motor client access.
    check_database_health()     — Health check for monitoring endpoints.
"""

from app.database.connection import (
    check_database_health,
    close_database_connection,
    connect_to_database,
    get_client,
    get_database,
)

__all__ = [
    "connect_to_database",
    "close_database_connection",
    "get_database",
    "get_client",
    "check_database_health",
]
