"""
ToolRegistry — role-scoped tool registry.
Structural permission enforcement: a role's registry only contains its allowed tools.
Calling .get() with an unknown tool name raises PermissionError BEFORE any data access.
"""
import logging
from typing import Dict, List

from app.assistant.tools.base_tool import AssistantTool
from app.assistant.schemas.assistant_schemas import AssistantRole

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    A closed registry of tools available to a specific role.

    Permission model:
        - The dict is populated at construction time with exactly the tools for that role.
        - get(name) raises PermissionError if name is not in the dict.
        - There is no way to add tools at runtime.
        - The LLM can only call tools that appear in to_llm_schema() — which reads from _tools.
    """

    def __init__(self, role: AssistantRole, tools: List[AssistantTool]):
        self._role = role
        self._tools: Dict[str, AssistantTool] = {t.name: t for t in tools}
        logger.debug(f"ToolRegistry created for role={role}, tools={list(self._tools.keys())}")

    def get(self, name: str) -> AssistantTool:
        if name not in self._tools:
            logger.warning(f"Permission denied: tool '{name}' not available for role '{self._role}'")
            raise PermissionError(
                f"Tool '{name}' is not available for role '{self._role}'. "
                "This may indicate a prompt injection or misconfiguration."
            )
        return self._tools[name]

    def to_llm_schema(self) -> List[Dict]:
        return [t.to_llm_schema() for t in self._tools.values()]

    @property
    def tool_names(self) -> List[str]:
        return list(self._tools.keys())


def build_registry(role: AssistantRole) -> ToolRegistry:
    """
    Factory that builds the closed tool registry for a given role.
    Import here to avoid circular imports.
    """
    if role == AssistantRole.CUSTOMER:
        from app.assistant.tools.customer_tools import get_customer_tools
        return ToolRegistry(role, get_customer_tools())
    elif role == AssistantRole.WORKER:
        from app.assistant.tools.worker_tools import get_worker_tools
        return ToolRegistry(role, get_worker_tools())
    elif role == AssistantRole.ADMIN:
        from app.assistant.tools.admin_tools import get_admin_tools
        return ToolRegistry(role, get_admin_tools())
    raise ValueError(f"Unknown role: {role}")
