"""
Repositories for the AI Assistant Platform.
"""
import datetime
import uuid
import logging
from typing import List, Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationRepository:
    """Persists assistant sessions and turns in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.sessions = db[settings.ASSISTANT_SESSION_COLLECTION]
        self.turns = db[settings.ASSISTANT_TURN_COLLECTION]

    async def create_session(self, role: str, user_id: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        await self.sessions.insert_one({
            "_id": session_id,
            "role": role,
            "user_id": user_id,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "turn_count": 0,
        })
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return await self.sessions.find_one({"_id": session_id})

    async def increment_turn_count(self, session_id: str):
        await self.sessions.update_one(
            {"_id": session_id},
            {"$inc": {"turn_count": 1}}
        )

    async def append_turn(self, session_id: str, role: str, content: str,
                          tools_called: List[str] = None, grounded: bool = True,
                          archived: bool = False) -> int:
        turn_count_doc = await self.sessions.find_one({"_id": session_id}, {"turn_count": 1})
        turn_index = (turn_count_doc or {}).get("turn_count", 0)
        await self.turns.insert_one({
            "session_id": session_id,
            "turn_index": turn_index,
            "role": role,
            "content": content,
            "tools_called": tools_called or [],
            "grounded": grounded,
            "archived": archived,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })
        await self.increment_turn_count(session_id)
        return turn_index

    async def get_turns(self, session_id: str, n: int = 20,
                        include_archived: bool = False) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"session_id": session_id}
        if not include_archived:
            query["archived"] = {"$ne": True}
        cursor = self.turns.find(query).sort("turn_index", 1).limit(n)
        return [doc async for doc in cursor]

    async def archive_turns(self, session_id: str, up_to_index: int):
        await self.turns.update_many(
            {"session_id": session_id, "turn_index": {"$lt": up_to_index}},
            {"$set": {"archived": True}}
        )

    async def save_summary(self, session_id: str, summary_text: str):
        await self.turns.insert_one({
            "session_id": session_id,
            "turn_index": -1,  # Summaries are always prepended as index -1
            "role": "summary",
            "content": summary_text,
            "archived": False,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })

    async def delete_session(self, session_id: str):
        await self.sessions.delete_one({"_id": session_id})
        await self.turns.delete_many({"session_id": session_id})
