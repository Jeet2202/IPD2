# -*- coding: utf-8 -*-
"""
Worker Voice Summary API -- POST /ai/worker/voice-summary

Pipeline:
  1. Validate worker JWT via Backend /api/v1/auth/me
  2. Build language-aware LLM prompt from screen_name + screen_data
  3. Call Groq LLM -> 2-3 sentence spoken summary in English or Hindi
  4. Call ElevenLabs TTS -> MP3 bytes
  5. Return base64-encoded MP3 + text to Flutter

Language rules:
  - 'en'  -> English summary + English voice
  - 'hi'  -> Hindi summary  + Hindi voice
  - 'mr'  -> Flutter maps to 'hi' before sending -- this endpoint always receives 'en' or 'hi'
"""

import logging
from typing import Any, Dict, Literal

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.assistant.llm.groq_client import GroqLLMClient
from app.services.gtts_service import gtts_service
from app.utils.backend_client import BackendClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["Worker Voice Summary"])

# Shared LLM client instance
_llm = GroqLLMClient()

# -- LLM System Prompts ---------------------------------------------------------

_SYSTEM_PROMPT_EN = (
    "You are a concise voice assistant for blue-collar service workers in India. "
    "You will receive a JSON payload describing what a worker sees on their current app screen. "
    "Your job is to summarize the most important information in EXACTLY 2-3 short spoken sentences. "
    "Focus on: pending jobs, today's earnings, scheduled visits, and urgent action items. "
    "Do NOT mention technical IDs, codes, or system details. "
    "Use natural spoken English that is easy to understand. "
    "Reply ONLY with the summary sentences, no extra text or formatting."
)

# Hindi prompt stored as Unicode escape sequences to keep this file pure ASCII.
# The string at runtime is fully valid Hindi text.
_SYSTEM_PROMPT_HI = (
    "\u0906\u092a \u092d\u093e\u0930\u0924 \u092e\u0947\u0902 \u0915\u093e\u092e "
    "\u0915\u0930\u0928\u0947 \u0935\u093e\u0932\u0947 \u092e\u091c\u0926\u0942\u0930\u094b\u0902 "
    "(\u0938\u0930\u094d\u0935\u093f\u0938 \u0935\u0930\u094d\u0915\u0930) \u0915\u0947 \u0932\u093f\u090f "
    "\u090f\u0915 \u0938\u0902\u0915\u094d\u0937\u093f\u092a\u094d\u0924 \u0935\u0949\u092f\u0938 "
    "\u0905\u0938\u093f\u0938\u094d\u091f\u0947\u0902\u091f \u0939\u0948\u0902\u0964 "
    "\u0906\u092a\u0915\u094b \u0935\u0930\u094d\u0915\u0930 \u0915\u0947 \u090f\u092a "
    "\u0938\u094d\u0915\u094d\u0930\u0940\u0928 \u0915\u093e JSON \u0921\u0947\u091f\u093e "
    "\u092e\u093f\u0932\u0947\u0917\u093e\u0964 "
    "\u0938\u092c\u0938\u0947 \u092e\u0939\u0924\u094d\u0935\u092a\u0942\u0930\u094d\u0923 "
    "\u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0915\u094b \u0915\u0947\u0935\u0932 2-3 "
    "\u091b\u094b\u091f\u0947 \u092c\u094b\u0932\u0928\u0947 \u092f\u094b\u0917\u094d\u092f "
    "\u0935\u093e\u0915\u094d\u092f\u094b\u0902 \u092e\u0947\u0902 \u0938\u093e\u0930\u093e\u0902\u0936\u093f\u0924 "
    "\u0915\u0930\u0947\u0902\u0964 "
    "\u0927\u094d\u092f\u093e\u0928 \u0926\u0947\u0902: \u0932\u0902\u092c\u093f\u0924 "
    "\u0928\u094c\u0915\u0930\u093f\u092f\u093e\u0901, \u0906\u091c \u0915\u0940 \u0915\u092e\u093e\u0908, "
    "\u0928\u093f\u0930\u094d\u0927\u093e\u0930\u093f\u0924 \u0935\u093f\u091c\u093c\u093f\u091f, "
    "\u0914\u0930 \u0915\u094b\u0908 \u091c\u093c\u0930\u0942\u0930\u0940 \u0915\u093e\u092e\u0964 "
    "\u0915\u094b\u0908 \u0924\u0915\u0928\u0940\u0915\u0940 ID, \u0915\u094b\u0921 \u092f\u093e "
    "\u0938\u093f\u0938\u094d\u091f\u092e \u0935\u093f\u0935\u0930\u0923 \u0928 \u092c\u094b\u0932\u0947\u0902\u0964 "
    "\u0938\u0930\u0932 \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 \u092c\u094b\u0932\u0947\u0902 "
    "\u091c\u094b \u0906\u0938\u093e\u0928\u0940 \u0938\u0947 \u0938\u092e\u091d \u092e\u0947\u0902 "
    "\u0906\u090f\u0964 "
    "\u0915\u0947\u0935\u0932 \u0938\u093e\u0930\u093e\u0902\u0936 \u0935\u093e\u0915\u094d\u092f "
    "\u0932\u093f\u0916\u0947\u0902, \u0915\u094b\u0908 \u0905\u0924\u093f\u0930\u093f\u0915\u094d\u0924 "
    "\u091f\u0947\u0915\u094d\u0938\u094d\u091f \u092f\u093e \u092b\u093c\u0949\u0930\u094d\u092e\u0947\u091f\u093f\u0902\u0917 "
    "\u0928\u0939\u0940\u0902\u0964"
)

# Fallback Hindi summaries (also Unicode escaped)
_HINDI_FALLBACK = "\u0905\u092d\u0940 \u0915\u094b\u0908 \u092e\u0939\u0924\u094d\u0935\u092a\u0942\u0930\u094d\u0923 \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u0939\u0940\u0902 \u0939\u0948\u0964"

# -- Screen name -> human-readable context hint for the LLM --------------------

_SCREEN_HINTS: Dict[str, str] = {
    "dashboard":      "Worker's home dashboard",
    "my_jobs":        "Worker's active and assigned jobs list",
    "marketplace":    "Open marketplace where workers browse available jobs to apply",
    "wallet":         "Worker's earnings wallet and payout history",
    "booking_detail": "Details of a specific customer booking assigned to the worker",
    "earnings":       "Worker's earnings overview and income summary",
    "profile":        "Worker's profile details and completion status",
}


# -- Request / Response schemas -------------------------------------------------

class VoiceSummaryRequest(BaseModel):
    screen_name: str = Field(..., description="Screen identifier (e.g. 'dashboard', 'wallet')")
    screen_data: Dict[str, Any] = Field(..., description="Key-value data visible on the screen")
    language: Literal["en", "hi"] = Field(
        default="en",
        description=(
            "Output language: 'en' for English, 'hi' for Hindi. "
            "Marathi should be mapped to 'hi' by client."
        ),
    )


class VoiceSummaryResponse(BaseModel):
    summary_text: str = Field(..., description="The AI-generated summary (for debugging / display)")
    audio_base64: str = Field(..., description="Base64-encoded MP3 audio bytes")
    language: str = Field(..., description="Language used for synthesis")


# -- Worker JWT validation via backend /auth/me ---------------------------------

async def _validate_worker_token(authorization: str) -> None:
    """
    Validates the Bearer token by calling the backend /api/v1/auth/me.
    Raises HTTP 401 / 403 on invalid token or non-worker role.

    Accepts both 'worker' and 'partner' roles (the app uses both terms).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    try:
        response = await BackendClient.request(
            method="GET",
            endpoint="/api/v1/auth/me",
            headers={"Authorization": authorization},
        )
        user_data = response.json()
    except Exception as exc:
        logger.warning("Token validation failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    # /auth/me response shape: { "data": { "user": { "role": "worker" } } }
    # Accept both "worker" and "partner" -- app uses both terms for the same role.
    data = user_data.get("data", {})
    user = data.get("user", data)  # graceful fallback if "user" key absent
    role = user.get("role") or user_data.get("role")

    logger.debug("Token validation: extracted role=%s", role)

    if role not in ("worker", "partner"):
        raise HTTPException(
            status_code=403,
            detail="Voice summary is only available for workers (partners).",
        )


# -- LLM summarization ---------------------------------------------------------

async def _generate_summary(
    screen_name: str,
    screen_data: Dict[str, Any],
    language: Literal["en", "hi"],
) -> str:
    """
    Call Groq LLM to produce a concise, voice-ready summary.
    Returns the summary text.
    """
    screen_hint = _SCREEN_HINTS.get(screen_name, f"Worker's {screen_name} screen")
    system_prompt = _SYSTEM_PROMPT_HI if language == "hi" else _SYSTEM_PROMPT_EN

    user_message = (
        f"Screen: {screen_hint}\n"
        f"Data: {screen_data}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    llm_response = await _llm.complete(
        messages=messages,
        tools=None,
    )

    summary = (llm_response.content or "").strip()
    if not summary:
        # Graceful fallback
        summary = _HINDI_FALLBACK if language == "hi" else "No important updates are available right now."

    logger.info("LLM summary generated: language=%s length=%d", language, len(summary))
    return summary


# -- Endpoint ------------------------------------------------------------------

@router.post(
    "/worker/voice-summary",
    response_model=VoiceSummaryResponse,
    summary="Generate a spoken summary of worker screen data (worker only)",
    description=(
        "Accepts the current screen's data, generates a 2-3 sentence AI summary via Groq LLM, "
        "synthesizes it to MP3 audio via ElevenLabs TTS, and returns base64-encoded audio. "
        "Language 'en' -> English voice, 'hi' -> Hindi voice. "
        "Marathi must be mapped to 'hi' by the client before calling this endpoint. "
        "Requires a valid worker JWT in the Authorization header."
    ),
)
async def worker_voice_summary(
    request: VoiceSummaryRequest,
    authorization: str = Header(..., alias="Authorization"),
) -> VoiceSummaryResponse:
    # 1. Validate worker identity
    await _validate_worker_token(authorization)

    # 2. Generate LLM summary
    try:
        summary_text = await _generate_summary(
            screen_name=request.screen_name,
            screen_data=request.screen_data,
            language=request.language,
        )
    except Exception as exc:
        logger.error("LLM summarization failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate voice summary") from exc

    # 3. Synthesize audio via Google TTS (free, no API key required)
    try:
        audio_base64 = await gtts_service.synthesize_base64(
            text=summary_text,
            language_code=request.language,
        )
    except Exception as exc:
        logger.error("gTTS synthesis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Voice synthesis failed. Please try again.") from exc

    return VoiceSummaryResponse(
        summary_text=summary_text,
        audio_base64=audio_base64,
        language=request.language,
    )
