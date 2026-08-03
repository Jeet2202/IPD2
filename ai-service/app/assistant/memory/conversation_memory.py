"""
ConversationMemory — manages session history and summarization.
Phase 4: summarizes when turn count crosses ASSISTANT_SUMMARY_THRESHOLD.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from app.assistant.repositories.conversation_repository import ConversationRepository
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationMemory:
    def __init__(self, repo: ConversationRepository):
        self._repo = repo

    async def get_history_as_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Returns conversation history as an OpenAI-style message list.
        Includes any saved summary as a system message first.
        """
        turns = await self._repo.get_turns(session_id, n=settings.ASSISTANT_MAX_TURNS)
        messages = []
        for turn in turns:
            role = turn["role"]
            content = turn["content"]
            if role == "summary":
                messages.append({"role": "system", "content": f"[Previous conversation summary]: {content}"})
            elif role in ("user", "assistant"):
                messages.append({"role": role, "content": content})
        return messages

    async def append_turn(self, session_id: str, user_message: str,
                          assistant_response: str, tools_called: List[str],
                          grounded: bool):
        """Saves the user + assistant turns and triggers summarization if threshold met."""
        await self._repo.append_turn(session_id, "user", user_message)
        turn_index = await self._repo.append_turn(
            session_id, "assistant", assistant_response,
            tools_called=tools_called, grounded=grounded
        )

        # Check if summarization is needed
        session = await self._repo.get_session(session_id)
        if session and session.get("turn_count", 0) >= settings.ASSISTANT_SUMMARY_THRESHOLD:
            await self._maybe_summarize(session_id, turn_index)

    async def _maybe_summarize(self, session_id: str, current_turn_index: int):
        """
        Summarizes the oldest half of turns when threshold is crossed.
        The summary is stored as a special 'summary' role turn.
        Old turns are marked as archived.
        """
        threshold = settings.ASSISTANT_SUMMARY_THRESHOLD
        midpoint = max(1, current_turn_index - threshold // 2)

        turns_to_summarize = await self._repo.get_turns(session_id, n=midpoint, include_archived=False)
        if len(turns_to_summarize) < 3:
            return

        # Build a condensed text of the conversation to summarize
        conversation_text = "\n".join(
            f"{t['role'].upper()}: {t['content'][:300]}" for t in turns_to_summarize
        )
        summary_text = (
            f"[Auto-summary of {len(turns_to_summarize)} earlier turns]: "
            f"{conversation_text[:800]}..."
        )

        await self._repo.save_summary(session_id, summary_text)
        await self._repo.archive_turns(session_id, up_to_index=midpoint)
        logger.info(f"Summarized {len(turns_to_summarize)} turns for session {session_id}")
