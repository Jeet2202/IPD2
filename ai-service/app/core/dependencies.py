from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import Database
from app.core.config import Settings, settings

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Dependency to get the database session"""
    db = Database.get_db()
    yield db

def get_settings() -> Settings:
    """Dependency to get application settings"""
    return settings
