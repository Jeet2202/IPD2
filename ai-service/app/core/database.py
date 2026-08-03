from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

    @classmethod
    async def connect_db(cls):
        try:
            # Mask credentials in log — only show the scheme + host portion
            safe_uri = settings.MONGODB_URI.split("@")[-1] if "@" in settings.MONGODB_URI else settings.MONGODB_URI
            logger.info(f"Connecting to MongoDB at ...{safe_uri}")
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise e

    @classmethod
    async def close_db(cls):
        if cls.client:
            logger.info("Closing MongoDB connection")
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_db(cls):
        if cls.client is None:
            raise Exception("Database client not initialized. Call connect_db first.")
        return cls.client[settings.MONGODB_DATABASE]

db = Database()

