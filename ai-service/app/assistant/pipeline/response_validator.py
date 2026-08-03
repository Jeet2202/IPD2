"""
ResponseValidator — grounding check + output safety scan.

Grounding rule: if the response contains a price figure (₹NNN or NNN rupees),
verify that figure appears in at least one tool result payload from this turn.
If not → replace with a grounding-failure message.

This is the ONLY place that enforces the no-hallucination contract in code.
"""
import re
import json
import logging
from typing import Any, Dict, List, Tuple

from app.assistant.pipeline.safety_filter import SafetyFilter

logger = logging.getLogger(__name__)

# Matches price figures in the response: ₹850, Rs.850, INR 850, 850 rupees
_PRICE_PATTERN = re.compile(r"(?:₹|Rs\.?\s*|INR\s*)(\d[\d,]*)|(\d[\d,]*)\s+rupees?", re.I)

_GROUNDING_FAILURE_MSG = (
    "I'm sorry, I couldn't verify that information from the available data. "
    "Please contact KaamSetu support for accurate details."
)


class ResponseValidator:
    @staticmethod
    def validate(response_text: str, tool_results: List[Dict[str, Any]]) -> Tuple[str, bool]:
        """
        Validates the LLM response against tool results.

        Returns:
            (validated_text, is_grounded)
            is_grounded = True if all factual claims could be traced back.
        """
        if not response_text:
            return _GROUNDING_FAILURE_MSG, False

        # Step 1: Check for price claims that need grounding
        price_matches = _PRICE_PATTERN.findall(response_text)
        claimed_prices = set()
        for m in price_matches:
            val = m[0] or m[1]
            claimed_prices.add(val.replace(",", ""))

        if claimed_prices:
            # Serialize all tool results to one string for scanning
            results_text = json.dumps(tool_results, ensure_ascii=False)
            ungrounded = [p for p in claimed_prices if p not in results_text]
            if ungrounded:
                logger.warning(f"Grounding failure: prices {ungrounded} not found in tool results")
                return _GROUNDING_FAILURE_MSG, False

        # Step 2: Output PII scan
        safe_text = SafetyFilter.check_output(response_text)

        return safe_text, True
