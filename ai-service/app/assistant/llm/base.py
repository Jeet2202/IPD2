"""
LLMClient ABC — the only interface the rest of the system uses.
No SDK imports here. Swap providers by implementing this interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    content: Optional[str]
    tool_calls: List[ToolCall] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"


class LLMClient(ABC):
    """
    Provider-agnostic LLM interface.
    All pipeline code depends only on this class — never on a specific SDK.
    """

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """
        Send a message list to the LLM and receive a response.

        Args:
            messages: OpenAI-style message list:
                      [{"role": "system"|"user"|"assistant"|"tool", "content": "..."}]
            tools: Optional list of function-calling tool schemas (OpenAI function format).

        Returns:
            LLMResponse — content and/or tool_calls, never both None.
        """
        ...
