"""
Assistant schemas — request/response shapes for the assistant API.
"""
import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AssistantRole(str, Enum):
    CUSTOMER = "customer"
    WORKER = "worker"
    ADMIN = "admin"


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' | 'assistant' | 'system' | 'summary'")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    session_id: Optional[str] = Field(None, description="Existing session ID; omit to start new session")
    role: AssistantRole = Field(default=AssistantRole.CUSTOMER)
    # Auth context — in production injected from JWT; provided in request for Phase 5.5 simplicity
    user_id: Optional[str] = None
    worker_id: Optional[str] = None
    admin_id: Optional[str] = None
    auth_token: Optional[str] = Field(None, description="Bearer token forwarded to backend API calls")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    role: AssistantRole
    grounded: bool = Field(description="True if response was verified against tool results")
    tools_called: List[str] = Field(default_factory=list)
    turn_index: int


class SessionInfo(BaseModel):
    session_id: str
    role: AssistantRole
    created_at: str
    turn_count: int


class TurnRecord(BaseModel):
    turn_index: int
    user_message: str
    assistant_response: str
    tools_called: List[str] = Field(default_factory=list)
    grounded: bool
    timestamp: str
