"""
AssistantTool ABC — every tool implements this interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class AssistantTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique snake_case identifier used in LLM tool-calling schemas."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description used in the LLM tool schema."""
        ...

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema for the tool's arguments (OpenAI function-calling format)."""
        ...

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            arguments: The arguments provided by the LLM (validated against parameters_schema).
            context: Auth/session context — e.g. {"auth_token": "...", "user_id": "..."}

        Returns:
            A dict that will be serialized as the tool result message.
        """
        ...

    def to_llm_schema(self) -> Dict[str, Any]:
        """Returns an OpenAI-compatible function-calling schema entry."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            }
        }
