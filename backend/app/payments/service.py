"""
Razorpay payment service — wraps the official razorpay-python SDK.

Responsibilities:
    - Create Razorpay Orders (customer initiates payment).
    - Verify payment signatures (HMAC-SHA256) to confirm real payments.
    - Handle Razorpay webhook events (payment.captured, payment.failed, etc.).
    - Initiate refunds when needed (cancellations / disputes).

Architecture:
    This is a pure service layer — no FastAPI, no HTTP.
    The router (router.py) handles HTTP concerns; this handles Razorpay API calls.

Razorpay amount convention:
    Razorpay accepts amounts in the SMALLEST currency unit (paise for INR).
    ₹99 → 9900 paise.  Always multiply rupees × 100 before passing here.
"""

import hashlib
import hmac
import logging

import razorpay

from app.core.config import settings

logger = logging.getLogger(__name__)


class RazorpayService:
    """
    Singleton wrapper around the Razorpay Python SDK client.

    Usage:
        from app.payments.service import razorpay_service
        order = await razorpay_service.create_order(amount_rupees=99.0, receipt="rcpt_abc")
    """

    def __init__(self) -> None:
        self._client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET.get_secret_value(),
            )
        )
        logger.info("RazorpayService initialised (mode=%s)", self._mode)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def _mode(self) -> str:
        """Returns 'live' or 'test' based on the key prefix."""
        return "live" if settings.RAZORPAY_KEY_ID.startswith("rzp_live") else "test"

    # ------------------------------------------------------------------
    # Order creation
    # ------------------------------------------------------------------

    def create_order(
        self,
        amount_rupees: float,
        receipt: str,
        notes: dict | None = None,
        currency: str = "INR",
    ) -> dict:
        """
        Create a Razorpay Order.

        Args:
            amount_rupees: Amount in Indian Rupees (e.g. 99.0 for ₹99).
            receipt:       Unique receipt ID — typically the booking/job ObjectId.
            notes:         Optional metadata dict attached to the order (visible in dashboard).
            currency:      ISO 4217 currency code. Defaults to "INR".

        Returns:
            Full Razorpay order dict including 'id', 'amount', 'currency', 'status'.

        Raises:
            razorpay.errors.BadRequestError: Invalid request params.
            razorpay.errors.ServerError:     Razorpay is down.
        """
        amount_paise = int(amount_rupees * 100)
        payload: dict = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt[:40],       # Razorpay max 40 chars
            "payment_capture": 1,          # Auto-capture on success
            "notes": notes or {},
        }
        logger.debug("Creating Razorpay order: receipt=%s amount_paise=%d", receipt, amount_paise)
        order = self._client.order.create(data=payload)
        logger.info("Razorpay order created: order_id=%s receipt=%s", order["id"], receipt)
        return order

    # ------------------------------------------------------------------
    # Signature verification
    # ------------------------------------------------------------------

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """
        Verify the HMAC-SHA256 signature returned by Razorpay after payment.

        Razorpay computes:
            signature = HMAC_SHA256(key=KEY_SECRET, msg="{order_id}|{payment_id}")

        We recompute and compare with hmac.compare_digest (timing-safe).

        Returns:
            True  — signature valid (payment is genuine).
            False — signature mismatch (potential fraud / replay attack).
        """
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated = hmac.new(
            settings.RAZORPAY_KEY_SECRET.get_secret_value().encode(),
            msg.encode(),
            hashlib.sha256,
        ).hexdigest()
        valid = hmac.compare_digest(generated, razorpay_signature)
        if not valid:
            logger.warning(
                "Razorpay signature mismatch! order_id=%s payment_id=%s",
                razorpay_order_id,
                razorpay_payment_id,
            )
        return valid

    def verify_webhook_signature(self, payload_body: bytes, signature: str) -> bool:
        """
        Verify Razorpay webhook signature.

        Razorpay signs the raw request body with RAZORPAY_WEBHOOK_SECRET.
        Call this in your webhook endpoint BEFORE processing the event.

        Returns:
            True if the webhook is genuine.
        """
        generated = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value().encode(),
            payload_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(generated, signature)

    # ------------------------------------------------------------------
    # Refunds
    # ------------------------------------------------------------------

    def create_refund(self, payment_id: str, amount_rupees: float | None = None) -> dict:
        """
        Initiate a refund for a captured payment.

        Args:
            payment_id:    Razorpay payment ID (e.g. "pay_xxxxxxxxxxxxx").
            amount_rupees: Amount to refund in rupees. Pass None for full refund.

        Returns:
            Razorpay refund dict.
        """
        payload: dict = {}
        if amount_rupees is not None:
            payload["amount"] = int(amount_rupees * 100)
        logger.info("Initiating refund: payment_id=%s amount=%s", payment_id, amount_rupees)
        refund = self._client.payment.refund(payment_id, payload)
        logger.info("Refund created: refund_id=%s", refund.get("id"))
        return refund

    # ------------------------------------------------------------------
    # Payment fetch (for reconciliation / admin checks)
    # ------------------------------------------------------------------

    def fetch_payment(self, payment_id: str) -> dict:
        """Fetch a single payment record from Razorpay."""
        return self._client.payment.fetch(payment_id)


# ---------------------------------------------------------------------------
# Singleton — import this everywhere, do NOT re-instantiate
# ---------------------------------------------------------------------------
razorpay_service = RazorpayService()
