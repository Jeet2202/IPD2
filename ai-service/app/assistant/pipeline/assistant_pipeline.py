"""
AssistantPipeline — orchestrates all pipeline stages for one assistant turn.

Flow:
  1. SafetyFilter.check_input()
  2. ContextRetriever.get_or_create_session() + get_history()
  3. KnowledgeRetriever.retrieve()
  4. PromptBuilder.build_initial_messages()
  5. LLM.complete() — first pass (may return tool_calls)
  6. For each tool_call: ToolRegistry.get(name).execute(args, context)
  7. PromptBuilder.append_tool_results()
  8. LLM.complete() — second pass (final answer)
  9. ResponseValidator.validate()
 10. ContextRetriever.append_turn()
"""
import json
import logging
import time
from typing import Any, Dict, List, Optional

from app.assistant.llm.base import LLMClient, LLMResponse
from app.assistant.pipeline.safety_filter import SafetyFilter
from app.assistant.pipeline.context_retriever import ContextRetriever
from app.assistant.pipeline.knowledge_retriever import KnowledgeRetriever
from app.assistant.pipeline.intent_detector import IntentDetector
from app.assistant.pipeline.prompt_builder import PromptBuilder
from app.assistant.pipeline.response_validator import ResponseValidator
from app.assistant.tools.tool_registry import ToolRegistry, build_registry
from app.assistant.schemas.assistant_schemas import AssistantRole, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

_NO_INFO_RESPONSE = (
    "I'm sorry, I don't have information about that topic. "
    "Please contact KaamSetu support for further assistance."
)


class AssistantPipeline:
    def __init__(
        self,
        llm_client: LLMClient,
        context_retriever: ContextRetriever,
        knowledge_retriever: KnowledgeRetriever,
    ):
        self._llm = llm_client
        self._ctx = context_retriever
        self._knowledge = knowledge_retriever

    async def run(self, request: ChatRequest) -> ChatResponse:
        t_start = time.time()
        role = request.role

        # Build execution context (auth + user identity)
        exec_context: Dict[str, Any] = {
            "auth_token": request.auth_token or "",
            "user_id": request.user_id or "",
            "worker_id": request.worker_id or "",
            "admin_id": request.admin_id or "",
            "session_id": request.session_id or "",
        }

        # ── Step 1: Safety check ──────────────────────────────────────────
        SafetyFilter.check_input(request.message)

        # ── Step 2: Session + history ─────────────────────────────────────
        session_id = await self._ctx.get_or_create_session(
            session_id=request.session_id,
            role=role,
            user_id=request.user_id,
        )
        exec_context["session_id"] = session_id
        history = await self._ctx.get_history(session_id)

        # ── Step 3: Intent detection ──────────────────────────────────────
        intent = IntentDetector.detect(request.message)
        logger.info(f"[{session_id}] Intent: {intent.label} ({intent.confidence:.0%})")

        # ── Step 4: Knowledge retrieval ───────────────────────────────────
        knowledge = await self._knowledge.retrieve(request.message, role=role.value)
        exec_context.update(knowledge)  # Inject into tool context

        # ── Step 5: Build tools registry + prompt ─────────────────────────
        registry = build_registry(role)
        prompt_context = {**exec_context, "platform": "KaamSetu Home Services"}
        messages = PromptBuilder.build_initial_messages(
            role=role,
            history=history,
            knowledge=knowledge,
            user_message=request.message,
            context=prompt_context,
        )

        # ── Step 6: First LLM pass ────────────────────────────────────────
        llm_response: LLMResponse = await self._llm.complete(
            messages=messages,
            tools=registry.to_llm_schema(),
        )

        # ── Step 7: Tool execution ────────────────────────────────────────
        tool_results: List[Dict[str, Any]] = []
        tools_called: List[str] = []

        if llm_response.tool_calls:
            for tc in llm_response.tool_calls:
                logger.info(f"[{session_id}] Tool call: {tc.name}({tc.arguments})")
                try:
                    tool = registry.get(tc.name)  # Raises PermissionError if not allowed
                    result = await tool.execute(tc.arguments, exec_context)
                    tool_results.append({"tool_name": tc.name, "tool_call_id": tc.id, "result": result})
                    tools_called.append(tc.name)
                except PermissionError as e:
                    logger.error(f"[{session_id}] Permission denied for tool {tc.name}: {e}")
                    tool_results.append({"tool_name": tc.name, "tool_call_id": tc.id, "result": {"error": "Permission denied"}})
                except Exception as e:
                    logger.error(f"[{session_id}] Tool {tc.name} failed: {e}")
                    tool_results.append({"tool_name": tc.name, "tool_call_id": tc.id, "result": {"error": str(e)}})

            # ── Step 8: Second LLM pass with tool results ─────────────────
            # Add the assistant's tool-calling turn to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}}
                    for tc in llm_response.tool_calls
                ],
            })
            
            # Add tool result messages in Groq format
            for tr in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": json.dumps(tr["result"]),
                })

            # Append the framing instructions using PromptBuilder to enforce safety/grounding
            messages = PromptBuilder.append_tool_results(messages, role, tool_results)

            final_response: LLMResponse = await self._llm.complete(
                messages=messages,
                tools=None,  # No tools on second pass — force text response
            )
            response_text = final_response.content or _NO_INFO_RESPONSE
        else:
            # No tool calls — direct answer
            response_text = llm_response.content or _NO_INFO_RESPONSE

        # ── Step 9: Validate response ─────────────────────────────────────
        validated_text, is_grounded = ResponseValidator.validate(response_text, tool_results)

        # ── Step 10: Persist turn ─────────────────────────────────────────
        session = await self._ctx._repo.get_session(session_id)
        turn_count = (session or {}).get("turn_count", 0)

        await self._ctx.append_turn(
            session_id=session_id,
            user_message=request.message,
            assistant_response=validated_text,
            tools_called=tools_called,
            grounded=is_grounded,
        )

        elapsed = time.time() - t_start
        logger.info(f"[{session_id}] Turn complete in {elapsed:.2f}s | grounded={is_grounded} | tools={tools_called}")

        return ChatResponse(
            session_id=session_id,
            response=validated_text,
            role=role,
            grounded=is_grounded,
            tools_called=tools_called,
            turn_index=turn_count,
        )
