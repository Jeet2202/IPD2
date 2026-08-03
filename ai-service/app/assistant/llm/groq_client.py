"""
GroqLLMClient — the ONLY file in the entire codebase that imports the Groq SDK.
Swapping to another provider means only replacing this file.
"""
import json
import logging
from typing import List, Optional, Dict, Any

from groq import AsyncGroq

from app.assistant.llm.base import LLMClient, LLMResponse, ToolCall
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqLLMClient(LLMClient):
    def __init__(self):
        self._client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        logger.debug(f"Groq request: model={settings.ASSISTANT_LLM_MODEL}, messages={len(messages)}, tools={len(tools) if tools else 0}")

        kwargs: Dict[str, Any] = {
            "model": settings.ASSISTANT_LLM_MODEL,
            "messages": messages,
            "max_tokens": settings.ASSISTANT_MAX_TOKENS,
            "temperature": settings.ASSISTANT_TEMPERATURE,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        # Map Groq tool_calls to internal ToolCall objects
        internal_tool_calls: List[ToolCall] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}
                    logger.warning(f"Could not parse tool call arguments for {tc.function.name}")
                internal_tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=args,
                ))

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        logger.debug(f"Groq response: finish_reason={choice.finish_reason}, usage={usage}")

        return LLMResponse(
            content=message.content,
            tool_calls=internal_tool_calls,
            usage=usage,
            finish_reason=choice.finish_reason or "stop",
        )
