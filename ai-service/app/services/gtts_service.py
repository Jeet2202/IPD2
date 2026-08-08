"""
Google Text-to-Speech (gTTS) Service -- Worker Voice Summary Feature.

Replaces ElevenLabs TTS. gTTS is completely free, requires no API key,
and supports both English ('en') and Hindi ('hi') natively.

The service converts summary text to MP3 bytes by calling the Google
Translate TTS endpoint internally (same engine as Google Translate audio).

Marathi ('mr') must be mapped to Hindi ('hi') upstream before calling this.
"""

import asyncio
import io
import logging
import base64
from typing import Literal

from gtts import gTTS, gTTSError

logger = logging.getLogger(__name__)

# gTTS language code mapping
_LANG_MAP = {
    "en": "en",
    "hi": "hi",
}

# Slow speech rate is clearer for workers listening while working.
# gTTS has a slow=True flag that speaks at a reduced pace.
_USE_SLOW_SPEECH = False  # set True if workers find normal pace too fast


class GTTSService:
    """
    Async wrapper around gTTS (Google Text-to-Speech).

    gTTS is synchronous internally, so we run it in a thread executor
    to avoid blocking the asyncio event loop.

    Usage:
        service = GTTSService()
        mp3_bytes = await service.synthesize("Hello, you have 3 pending jobs.", "en")
        b64 = await service.synthesize_base64("Aapke 3 kaam hain.", "hi")
    """

    def _synthesize_sync(self, text: str, lang: str) -> bytes:
        """
        Blocking gTTS call -- runs inside a thread executor.
        Returns raw MP3 bytes.
        """
        tts = gTTS(text=text, lang=lang, slow=_USE_SLOW_SPEECH)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)
        return mp3_buffer.read()

    async def synthesize(
        self,
        text: str,
        language_code: Literal["en", "hi"],
    ) -> bytes:
        """
        Convert text to MP3 audio bytes using Google TTS (free, no API key).

        Args:
            text:          The spoken summary text (2-3 sentences max).
            language_code: 'en' for English, 'hi' for Hindi.

        Returns:
            Raw MP3 bytes.

        Raises:
            RuntimeError: If gTTS call fails.
        """
        lang = _LANG_MAP.get(language_code, "en")

        logger.info(
            "gTTS TTS request: lang=%s text_length=%d",
            lang,
            len(text),
        )

        loop = asyncio.get_event_loop()
        try:
            mp3_bytes: bytes = await loop.run_in_executor(
                None,
                self._synthesize_sync,
                text,
                lang,
            )
        except gTTSError as exc:
            logger.error("gTTS error: %s", exc)
            raise RuntimeError(f"Google TTS failed: {exc}") from exc
        except Exception as exc:
            logger.error("gTTS unexpected error: %s", exc)
            raise RuntimeError(f"Voice synthesis error: {exc}") from exc

        logger.info("gTTS success: %d bytes returned", len(mp3_bytes))
        return mp3_bytes

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


# Singleton instance -- drop-in replacement for elevenlabs_service
gtts_service = GTTSService()
