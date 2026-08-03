"""
ContextRetriever — pulls session history and user profile for the pipeline.
"""
import logging
from typing import Any, Dict, List, Optional

from app.assistant.memory.conversation_memory import ConversationMemory
from app.assistant.repositories.conversation_repository import ConversationRepository
from app.assistant.schemas.assistant_schemas import AssistantRole

logger = logging.getLogger(__name__)


class ContextRetriever:
    def __init__(self, conv_repo: ConversationRepository):
        self._repo = conv_repo
        self._memory = ConversationMemory(conv_repo)

    async def get_or_create_session(
        self,
        session_id: Optional[str],
        role: AssistantRole,
        user_id: Optional[str] = None,
    ) -> str:
        if session_id:
            session = await self._repo.get_session(session_id)
            if session:
                return session_id
        # Create a new session
        return await self._repo.create_session(role=role.value, user_id=user_id)

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return await self._memory.get_history_as_messages(session_id)

    async def append_turn(self, session_id: str, user_message: str,
                          assistant_response: str, tools_called: List[str],
                          grounded: bool):
        await self._memory.append_turn(
            session_id, user_message, assistant_response, tools_called, grounded
        )
