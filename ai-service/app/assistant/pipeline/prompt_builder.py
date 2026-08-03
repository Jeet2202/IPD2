"""
PromptBuilder — assembles the final message list sent to the LLM.
Role-specific system prompts + history + knowledge context + user message.
"""
import json
import logging
from typing import Any, Dict, List

from app.assistant.schemas.assistant_schemas import AssistantRole
from app.assistant.pipeline.intent_detector import DetectedIntent
from app.assistant.prompts.customer_prompts import CUSTOMER_SYSTEM, CUSTOMER_TOOL_RESULT_FRAME, CUSTOMER_NO_RESULT_FRAME
from app.assistant.prompts.worker_prompts import WORKER_SYSTEM, WORKER_TOOL_RESULT_FRAME, WORKER_NO_RESULT_FRAME
from app.assistant.prompts.admin_prompts import ADMIN_SYSTEM, ADMIN_TOOL_RESULT_FRAME, ADMIN_NO_RESULT_FRAME

logger = logging.getLogger(__name__)

_SYSTEM_TEMPLATES = {
    AssistantRole.CUSTOMER: CUSTOMER_SYSTEM,
    AssistantRole.WORKER: WORKER_SYSTEM,
    AssistantRole.ADMIN: ADMIN_SYSTEM,
}

_TOOL_RESULT_TEMPLATES = {
    AssistantRole.CUSTOMER: (CUSTOMER_TOOL_RESULT_FRAME, CUSTOMER_NO_RESULT_FRAME),
    AssistantRole.WORKER: (WORKER_TOOL_RESULT_FRAME, WORKER_NO_RESULT_FRAME),
    AssistantRole.ADMIN: (ADMIN_TOOL_RESULT_FRAME, ADMIN_NO_RESULT_FRAME),
}


class PromptBuilder:
    @staticmethod
    def build_initial_messages(
        role: AssistantRole,
        history: List[Dict[str, Any]],
        knowledge: Dict[str, Any],
        user_message: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Builds the initial message list for the LLM:
        [system, ...history, knowledge_context_system, user_message]
        """
        system_tmpl = _SYSTEM_TEMPLATES[role]
        system_msg = system_tmpl.to_message(**context)

        messages: List[Dict[str, Any]] = [system_msg]
        messages.extend(history)

        # Inject pre-fetched knowledge as a system context block
        if knowledge.get("faq_results") or knowledge.get("policy_results"):
            knowledge_text = json.dumps(knowledge, ensure_ascii=False, indent=2)
            messages.append({
                "role": "system",
                "content": f"[Knowledge base context for this query — use if relevant]:\n{knowledge_text}"
            })

        messages.append({"role": "user", "content": user_message})
        return messages

    @staticmethod
    def append_tool_results(
        messages: List[Dict[str, Any]],
        role: AssistantRole,
        tool_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Appends tool call results as system messages for the second LLM pass.
        Uses the role-specific template (result or no-result).
        """
        result_tmpl, no_result_tmpl = _TOOL_RESULT_TEMPLATES[role]
        for entry in tool_results:
            tool_name = entry["tool_name"]
            result = entry.get("result", {})
            has_data = bool(result) and "error" not in result

            if has_data:
                messages.append(result_tmpl.to_message(
                    tool_name=tool_name,
                    tool_result=json.dumps(result, ensure_ascii=False, indent=2),
                ))
            else:
                messages.append(no_result_tmpl.to_message(tool_name=tool_name))

        # After adding results, prompt the LLM to generate the final answer
        messages.append({"role": "user", "content": "Based on the tool results above, please answer my question."})
        return messages
