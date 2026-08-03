"""
MockLLMClient — used in ALL unit tests. Never hits the network.
Configure via fixture responses dict before calling complete().
"""
from typing import List, Optional, Dict, Any

from app.assistant.llm.base import LLMClient, LLMResponse, ToolCall


class MockLLMClient(LLMClient):
    """
    Deterministic mock for unit tests.

    Usage:
        client = MockLLMClient()
        client.set_response(LLMResponse(content="Test answer"))
        result = await client.complete(messages=[...])
    """

    def __init__(self):
        self._responses: List[LLMResponse] = []
        self._call_count = 0
        self.recorded_calls: List[Dict] = []

    def set_response(self, response: LLMResponse):
        """Set a single response returned on every call."""
        self._responses = [response]

    def set_responses(self, responses: List[LLMResponse]):
        """Set a sequence of responses returned in order (for multi-turn tests)."""
        self._responses = responses

    def add_response(self, response: LLMResponse):
        """Append a response to the sequence."""
        self._responses.append(response)

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        self.recorded_calls.append({"messages": messages, "tools": tools})

        if not self._responses:
            # Default empty response if nothing configured
            return LLMResponse(content="I don't have information about that.")

        idx = min(self._call_count, len(self._responses) - 1)
        response = self._responses[idx]
        self._call_count += 1
        return response

    def reset(self):
        self._responses = []
        self._call_count = 0
        self.recorded_calls = []
