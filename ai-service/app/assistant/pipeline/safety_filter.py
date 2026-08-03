"""
SafetyFilter — pattern-based guardrail.
Checks for prompt injection, jailbreak attempts, and sensitive data exposure patterns.
Raises AssistantSafetyError (never silently passes).
"""
import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class AssistantSafetyError(Exception):
    def __init__(self, code: str, reason: str):
        self.code = code
        self.reason = reason
        super().__init__(f"[{code}] {reason}")


# ── Injection / Jailbreak patterns ────────────────────────────────────────────
# Each tuple: (compiled regex, human-readable violation code)
_INJECTION_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I), "PROMPT_INJECTION"),
    (re.compile(r"<\s*system\s*>", re.I), "SYSTEM_TAG_INJECTION"),
    (re.compile(r"\bact\s+as\b.{0,30}\b(DAN|unrestricted|jailbreak|GPT-?[0-9])\b", re.I), "JAILBREAK_PERSONA"),
    (re.compile(r"\bDAN\b.*\b(mode|prompt|jailbreak)\b", re.I), "JAILBREAK_DAN"),
    (re.compile(r"(you\s+are\s+now|pretend\s+you\s+are|imagine\s+you\s+are)\s+(an?\s+)?(unrestricted|evil|unfiltered|different)\s+(AI|assistant|bot)", re.I), "PERSONA_OVERRIDE"),
    (re.compile(r"(reveal|show|print|output|display)\s+(your\s+)?(system\s+)?prompt", re.I), "PROMPT_EXTRACTION"),
    (re.compile(r"ignore\s+your\s+(guidelines?|rules?|restrictions?|training)", re.I), "GUIDELINE_BYPASS"),
    (re.compile(r"(developer|debug|admin|maintenance)\s+mode", re.I), "MODE_SWITCH"),
    (re.compile(r"(\[\[|\{\{|<\|).{0,20}(system|INST|SYS|instruction)", re.I), "TOKEN_INJECTION"),
    # Role escalation attempts
    (re.compile(r"(show|give|access|retrieve|fetch)\s+(me\s+)?(admin|worker|staff)\s+(data|stats?|info|details)", re.I), "ROLE_ESCALATION"),
]

# ── Sensitive data output patterns (check LLM response, not input) ────────────
_OUTPUT_PII_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b[6-9]\d{9}\b"), "PHONE_NUMBER_LEAK"),                  # Indian mobile number
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "PAN_LEAK"),                   # PAN card
    (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "AADHAAR_LEAK"),            # Aadhaar-like
    (re.compile(r"password\s*[:=]\s*\S+", re.I), "PASSWORD_LEAK"),
]

# ── Input sanitization ────────────────────────────────────────────────────────
_MAX_INPUT_LENGTH = 2000


class SafetyFilter:
    @staticmethod
    def check_input(text: str) -> None:
        """
        Validates a user input message.
        Raises AssistantSafetyError on any violation.
        Must be called BEFORE the message reaches the LLM.
        """
        if not text or not text.strip():
            raise AssistantSafetyError("EMPTY_INPUT", "Empty message received")

        if len(text) > _MAX_INPUT_LENGTH:
            raise AssistantSafetyError("INPUT_TOO_LONG", f"Input exceeds {_MAX_INPUT_LENGTH} characters")

        for pattern, code in _INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning(f"Safety violation detected: {code} | Input snippet: {text[:100]!r}")
                raise AssistantSafetyError(
                    code,
                    "Your message was flagged as a potential policy violation. "
                    "Please ask a legitimate customer service question."
                )

    @staticmethod
    def check_output(text: str) -> str:
        """
        Scans LLM-generated output for sensitive data patterns.
        If found, redacts and logs — does NOT raise (we redact, not block).
        Returns the (possibly redacted) text.
        """
        if not text:
            return text

        redacted = text
        for pattern, code in _OUTPUT_PII_PATTERNS:
            if pattern.search(redacted):
                logger.warning(f"Output PII pattern detected: {code} — redacting")
                redacted = pattern.sub("[REDACTED]", redacted)

        return redacted
