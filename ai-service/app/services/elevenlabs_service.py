"""
ElevenLabs Text-to-Speech Service — Worker Voice Summary Feature.

Converts text to MP3 audio bytes using ElevenLabs multilingual_v2 model.
Supports English (en-US) and Hindi (hi-IN) voices.
Marathi (mr) is mapped to Hindi upstream before reaching this service.
"""
import base64
import logging
from typing import Literal

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# ElevenLabs model that natively supports English + Hindi
ELEVENLABS_MODEL = "eleven_multilingual_v2"

# Voice settings tuned for clarity at slower speed (workers listening on the go)
VOICE_SETTINGS = {
    "stability": 0.60,
    "similarity_boost": 0.75,
    "style": 0.20,
    "use_speaker_boost": True,
}

# Output audio format
OUTPUT_FORMAT = "mp3_44100_128"


class ElevenLabsService:
    """
    Async TTS client that calls the ElevenLabs REST API.

    Usage:
        service = ElevenLabsService()
        mp3_bytes = await service.synthesize("Hello, you have 3 pending jobs.", "en")
    """

    def __init__(self) -> None:
        if not settings.ELEVENLABS_API_KEY or settings.ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_API_KEY_HERE":
            logger.warning(
                "ELEVENLABS_API_KEY is not configured. Voice synthesis will fail. "
                "Set ELEVENLABS_API_KEY in ai-service/.env"
            )

    def _get_voice_id(self, language_code: str) -> str:
        """Map language code to the correct ElevenLabs voice ID."""
        if language_code == "hi":
            return settings.ELEVENLABS_VOICE_ID_HI
        return settings.ELEVENLABS_VOICE_ID_EN  # Default: English

    async def synthesize(
        self,
        text: str,
        language_code: Literal["en", "hi"],
    ) -> bytes:
        """
        Convert text to MP3 audio bytes.

        Args:
            text:          The spoken summary text (2-3 sentences max).
            language_code: 'en' for English, 'hi' for Hindi.

        Returns:
            Raw MP3 bytes from ElevenLabs API.

        Raises:
            RuntimeError: If ElevenLabs API call fails.
        """
        voice_id = self._get_voice_id(language_code)
        url = ELEVENLABS_TTS_URL.format(voice_id=voice_id)

        payload = {
            "text": text,
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": VOICE_SETTINGS,
        }

        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        params = {"output_format": OUTPUT_FORMAT}

        logger.info(
            "ElevenLabs TTS request: voice_id=%s language=%s text_length=%d",
            voice_id,
            language_code,
            len(text),
        )

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(
                "ElevenLabs API error: status=%d body=%s",
                response.status_code,
                response.text[:300],
            )
            raise RuntimeError(
                f"ElevenLabs TTS failed with HTTP {response.status_code}: {response.text[:200]}"
            )

        logger.info(
            "ElevenLabs TTS success: %d bytes returned", len(response.content)
        )
        return response.content

    async def synthesize_base64(
        self,
        text: str,
        language_code: Literal["en", "hi"],
    ) -> str:
        """
        Convert text to base64-encoded MP3 string (for JSON transport to Flutter).

        Returns:
            Base64-encoded MP3 string.
        """
        mp3_bytes = await self.synthesize(text, language_code)
        return base64.b64encode(mp3_bytes).decode("utf-8")


# Singleton instance
elevenlabs_service = ElevenLabsService()
