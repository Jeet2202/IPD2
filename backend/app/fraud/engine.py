"""
Fraud Rule Engine — Evaluates configurable rules against event activity metrics.
"""

import logging
from typing import Any

from app.fraud.models import FraudRule
from app.fraud.schemas import FraudRuleType, TriggeredRuleDetail
from app.trust.schemas import RiskLevel

logger = logging.getLogger(__name__)


class FraudRuleEngine:
    """Evaluates activity data against active FraudRule definitions."""

    @staticmethod
    def evaluate_rules(
        activity_data: dict[str, Any],
        active_rules: list[FraudRule],
    ) -> list[TriggeredRuleDetail]:
        """
        Evaluate activity_data dictionary against a list of active FraudRule objects.

        Returns:
            list[TriggeredRuleDetail] of triggered rule matches.
        """
        triggered: list[TriggeredRuleDetail] = []

        for rule in active_rules:
            if not rule.is_active:
                continue

            t = rule.thresholds or {}
            match_reason: str | None = None

            if rule.rule_type == FraudRuleType.MULTIPLE_FAILED_LOGINS:
                failed = activity_data.get("failed_logins", activity_data.get("failed_logins_1h", 0))
                max_allowed = t.get("max_attempts", 5)
                if failed >= max_allowed:
                    match_reason = f"Multiple failed logins: {failed} attempts recorded (threshold: {max_allowed})."

            elif rule.rule_type == FraudRuleType.DUPLICATE_ACCOUNT_ATTEMPT:
                matches = activity_data.get("matching_accounts_count", 0)
                is_dup = activity_data.get("is_duplicate_identity", False)
                max_matches = t.get("max_matches", 1)
                if is_dup or matches >= max_matches:
                    match_reason = f"Duplicate account attempt: {matches} matching accounts detected sharing credentials."

            elif rule.rule_type == FraudRuleType.RAPID_BOOKING_CREATION:
                bookings_1h = activity_data.get("bookings_count_1h", 0)
                max_b = t.get("max_bookings_per_hour", 5)
                if bookings_1h >= max_b:
                    match_reason = f"Rapid booking creation: {bookings_1h} bookings created in 1 hour (threshold: {max_b})."

            elif rule.rule_type == FraudRuleType.EXCESSIVE_CANCELLATION:
                rate = activity_data.get("cancellation_rate", 0.0)
                cancels = activity_data.get("cancellations_count_24h", 0)
                max_rate = t.get("max_cancellation_rate", 0.5)
                max_cancels = t.get("max_cancellations_24h", 4)
                if rate >= max_rate or cancels >= max_cancels:
                    match_reason = f"Excessive cancellation: {cancels} cancellations (rate: {rate:.1%})."

            elif rule.rule_type == FraudRuleType.SUSPICIOUS_QUOTATION_ACTIVITY:
                price_dev = activity_data.get("quotation_price_deviation", 0.0)
                quotes_10m = activity_data.get("quotations_count_10m", 0)
                max_dev = t.get("max_deviation_multiplier", 3.0)
                max_q = t.get("max_quotes_10m", 10)
                if price_dev >= max_dev or quotes_10m >= max_q:
                    match_reason = f"Suspicious quotation activity: price deviation multiplier {price_dev:.1f}x."

            elif rule.rule_type == FraudRuleType.REPEATED_VERIFICATION_FAILURES:
                failures = activity_data.get("verification_failures_count", 0)
                max_f = t.get("max_failures", 3)
                if failures >= max_f:
                    match_reason = f"Repeated verification failures: {failures} document verification rejections."

            elif rule.rule_type == FraudRuleType.SPAM_BEHAVIOUR:
                messages = activity_data.get("identical_messages_count", 0)
                is_spam = activity_data.get("is_spam_flagged", False)
                max_m = t.get("max_identical_messages", 5)
                if is_spam or messages >= max_m:
                    match_reason = f"Spam behavior detected: {messages} identical messages sent."

            elif rule.rule_type == FraudRuleType.REVIEW_ABUSE:
                reviews_1h = activity_data.get("reviews_given_1h", 0)
                stuffing = activity_data.get("is_rating_stuffing", False)
                max_r = t.get("max_reviews_per_hour", 5)
                if stuffing or reviews_1h >= max_r:
                    match_reason = f"Review abuse pattern detected: {reviews_1h} reviews submitted in 1 hour."

            elif rule.rule_type == FraudRuleType.EXCESSIVE_PROFILE_UPDATES:
                updates_1h = activity_data.get("profile_updates_1h", 0)
                max_u = t.get("max_updates_per_hour", 6)
                if updates_1h >= max_u:
                    match_reason = f"Excessive profile updates: {updates_1h} profile updates in 1 hour."

            elif rule.rule_type == FraudRuleType.UNUSUAL_LOGIN_LOCATION:
                unusual = activity_data.get("is_unusual_location", False)
                ip_mismatch = activity_data.get("ip_country_mismatch", False)
                if unusual or ip_mismatch:
                    match_reason = "Unusual login location or country IP mismatch detected."

            elif rule.rule_type == FraudRuleType.SUSPICIOUS_API_PATTERNS:
                rpm = activity_data.get("api_requests_per_minute", 0)
                susp_ua = activity_data.get("is_suspicious_user_agent", False)
                max_rpm = t.get("max_rpm", 120)
                if susp_ua or rpm >= max_rpm:
                    match_reason = f"Suspicious API request pattern: {rpm} requests/min."

            if match_reason:
                triggered.append(
                    TriggeredRuleDetail(
                        rule_key=rule.rule_key,
                        name=rule.name,
                        rule_type=rule.rule_type,
                        severity=rule.severity,
                        score_impact=rule.score_impact,
                        reason=match_reason,
                    )
                )

        return triggered
