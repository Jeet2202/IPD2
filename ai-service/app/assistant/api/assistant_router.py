"""
Assistant API router — Phase 6 endpoints.
Role can be specified explicitly via endpoint OR inferred from the role field in ChatRequest.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.assistant.pipeline.assistant_pipeline import AssistantPipeline
from app.assistant.pipeline.context_retriever import ContextRetriever
from app.assistant.pipeline.knowledge_retriever import KnowledgeRetriever
from app.assistant.pipeline.safety_filter import AssistantSafetyError
from app.assistant.repositories.conversation_repository import ConversationRepository
from app.assistant.repositories.knowledge_repositories import FAQRepository, PolicyRepository
from app.assistant.schemas.assistant_schemas import (
    AssistantRole, ChatRequest, ChatResponse, TurnRecord
)
from app.assistant.llm.groq_client import GroqLLMClient
from app.core.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

# Singleton LLM client — re-used across requests
_llm_client = GroqLLMClient()


def get_pipeline(db=Depends(get_db)) -> AssistantPipeline:
    conv_repo = ConversationRepository(db)
    faq_repo = FAQRepository(db)
    policy_repo = PolicyRepository(db)
    ctx_retriever = ContextRetriever(conv_repo)
    knowledge_retriever = KnowledgeRetriever(faq_repo, policy_repo)
    return AssistantPipeline(_llm_client, ctx_retriever, knowledge_retriever)


async def _run_chat(request: ChatRequest, pipeline: AssistantPipeline) -> ChatResponse:
    try:
        return await pipeline.run(request)
    except AssistantSafetyError as e:
        logger.warning(f"Safety violation [{e.code}]: {e.reason}")
        raise HTTPException(status_code=400, detail={"code": e.code, "reason": e.reason})
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "reason": str(e)})
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "PIPELINE_ERROR", "reason": "An internal error occurred"})


@router.post("/chat", response_model=ChatResponse, summary="Send a message to the AI assistant (role in body)")
async def chat(request: ChatRequest, pipeline: AssistantPipeline = Depends(get_pipeline)):
    """
    Generic chat endpoint. Role is specified in the request body.
    Session is created automatically if session_id is omitted.
    """
    return await _run_chat(request, pipeline)


@router.post("/customer", response_model=ChatResponse, summary="Customer assistant endpoint")
async def chat_customer(request: ChatRequest, pipeline: AssistantPipeline = Depends(get_pipeline)):
    """Customer-scoped assistant. Forces role=customer regardless of request body."""
    request.role = AssistantRole.CUSTOMER
    return await _run_chat(request, pipeline)


@router.post("/worker", response_model=ChatResponse, summary="Worker assistant endpoint")
async def chat_worker(request: ChatRequest, pipeline: AssistantPipeline = Depends(get_pipeline)):
    """Worker-scoped assistant. Forces role=worker regardless of request body."""
    request.role = AssistantRole.WORKER
    return await _run_chat(request, pipeline)


@router.post("/admin", response_model=ChatResponse, summary="Admin assistant endpoint")
async def chat_admin(request: ChatRequest, pipeline: AssistantPipeline = Depends(get_pipeline)):
    """Admin-scoped assistant. Forces role=admin regardless of request body."""
    request.role = AssistantRole.ADMIN
    return await _run_chat(request, pipeline)


@router.get("/history/{session_id}", response_model=List[TurnRecord], summary="Retrieve conversation history")
async def get_history(session_id: str, db=Depends(get_db)):
    conv_repo = ConversationRepository(db)
    turns = await conv_repo.get_turns(session_id, n=50, include_archived=False)
    if not turns:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    return [
        TurnRecord(
            turn_index=t["turn_index"],
            user_message=t["content"] if t["role"] == "user" else "",
            assistant_response=t["content"] if t["role"] == "assistant" else "",
            tools_called=t.get("tools_called", []),
            grounded=t.get("grounded", True),
            timestamp=t.get("timestamp", ""),
        )
        for t in turns
    ]


@router.delete("/history/{session_id}", summary="Delete a conversation session")
async def delete_history(session_id: str, db=Depends(get_db)):
    conv_repo = ConversationRepository(db)
    await conv_repo.delete_session(session_id)
    return {"message": f"Session {session_id} deleted"}
