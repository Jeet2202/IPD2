"""
IntentDetector — lightweight rule-based intent classifier.
No LLM call — fast, deterministic, testable.
"""
import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class DetectedIntent:
    label: str
    confidence: float
    matched_pattern: str


_INTENT_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("booking_status",     re.compile(r"\b(booking|order)\s*(status|update|track|where|progress)\b", re.I)),
    ("service_search",     re.compile(r"\b(find|search|look\s+for|need|want|book)\s+(a\s+)?(plumber|electrician|cleaner|service|worker|help)\b", re.I)),
    ("price_enquiry",      re.compile(r"\b(price|cost|charge|rate|fee|estimate|how\s+much)\b", re.I)),
    ("recommendation",     re.compile(r"\b(recommend|suggest|best|top|who\s+should\s+i|which\s+worker)\b", re.I)),
    ("cancellation",       re.compile(r"\b(cancel|cancellation|refund|withdraw)\b", re.I)),
    ("payment",            re.compile(r"\b(pay|payment|paid|invoice|bill|transaction)\b", re.I)),
    ("policy",             re.compile(r"\b(policy|policies|rule|guideline|terms|conditions)\b", re.I)),
    ("worker_schedule",    re.compile(r"\b(my\s+schedule|upcoming\s+booking|assigned|jobs?\s+today)\b", re.I)),
    ("worker_quotation",   re.compile(r"\b(quote|quotation|bid|how\s+much\s+to\s+charge|pricing\s+guide)\b", re.I)),
    ("profile_help",       re.compile(r"\b(profile|improve|rating|performance|tips?)\b", re.I)),
    ("platform_stats",     re.compile(r"\b(stats?|statistics|total\s+booking|revenue|platform|dashboard)\b", re.I)),
    ("greeting",           re.compile(r"^\s*(hi|hello|hey|good\s+(morning|evening|afternoon)|namaste)\b", re.I)),
    ("general_faq",        re.compile(r"\b(how\s+does|what\s+is|explain|tell\s+me\s+about)\b", re.I)),
]

_FALLBACK_INTENT = DetectedIntent(label="general_faq", confidence=0.3, matched_pattern="fallback")


class IntentDetector:
    @staticmethod
    def detect(text: str) -> DetectedIntent:
        """
        Returns the first matching intent with confidence 0.9, or fallback at 0.3.
        Deterministic and always returns a result — no external calls.
        """
        for label, pattern in _INTENT_PATTERNS:
            if pattern.search(text):
                return DetectedIntent(label=label, confidence=0.9, matched_pattern=pattern.pattern)
        return _FALLBACK_INTENT
