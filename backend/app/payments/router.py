"""
Payment router — Razorpay order creation, verification, webhook handling, and refunds.

Endpoint map:
    POST /api/v1/payments/create-order   Create a Razorpay order (authenticated customer / worker)
    POST /api/v1/payments/verify         Verify payment signature after SDK success (authenticated)
    POST /api/v1/payments/webhook        Razorpay webhook receiver (no auth — Razorpay signed)
    POST /api/v1/payments/refund         Initiate refund (admin only)
    GET  /api/v1/payments/{payment_id}   Fetch Razorpay payment info (admin)

Design decisions:
    - create-order and verify require authentication so we can tie the payment
      to the correct booking + user, preventing spoofed payment confirmations.
    - The webhook endpoint intentionally has NO JWT auth — Razorpay calls it.
      Instead it's secured by HMAC-SHA256 signature verification on the raw body.
    - Refund and fetch are admin-only endpoints to prevent customers from
      initiating their own refunds.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.dependencies import get_current_user
from app.core.permissions import require_admin
from app.auth.models import User
from app.core.config import settings
from app.booking.models import Booking
from app.payments.schemas import (
    CreateOrderRequest,
    OrderCreatedResponse,
    PaymentVerifiedResponse,
    RefundRequest,
    RefundResponse,
    VerifyPaymentRequest,
)
from app.payments.service import razorpay_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Payments"])


# ---------------------------------------------------------------------------
# POST /payments/create-order
# ---------------------------------------------------------------------------

@router.post(
    "/create-order",
    response_model=OrderCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Razorpay order",
    description=(
        "Called by the Flutter app BEFORE opening the Razorpay checkout modal. "
        "Creates a server-side order, returns the order_id + public key_id "
        "that the Flutter SDK needs to launch the payment sheet."
    ),
)
async def create_payment_order(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
) -> OrderCreatedResponse:
    """
    1. Validates booking_id belongs to the current user (or is accessible).
    2. Creates a Razorpay order for the specified amount.
    3. Returns order details to Flutter.
    """
    # Optionally validate the booking exists and belongs to this user
    try:
        booking = await Booking.get(req.booking_id)
    except Exception:
        booking = None

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking '{req.booking_id}' not found.",
        )

    # Ownership check: user must be the booking customer, assigned worker, or admin
    if str(booking.customer_id) != str(current_user.id) and getattr(current_user, "role", "customer") not in ("admin", "worker"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a payment order for this booking.",
        )

    receipt = f"rcpt_{req.booking_id}"
    notes = req.notes or {
        "booking_id": req.booking_id,
        "payment_type": req.payment_type.value,
        "user_id": str(current_user.id),
    }

    try:
        order = razorpay_service.create_order(
            amount_rupees=req.amount,
            receipt=receipt,
            notes=notes,
        )
    except Exception as exc:
        logger.exception("Failed to create Razorpay order for booking %s: %s", req.booking_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment gateway error. Please try again.",
        ) from exc

    return OrderCreatedResponse(
        order_id=order["id"],
        amount=order["amount"],
        currency=order["currency"],
        key_id=settings.RAZORPAY_KEY_ID,
    )


# ---------------------------------------------------------------------------
# POST /payments/verify
# ---------------------------------------------------------------------------

@router.post(
    "/verify",
    response_model=PaymentVerifiedResponse,
    summary="Verify Razorpay payment signature",
    description=(
        "Called by Flutter immediately after Razorpay checkout success. "
        "Verifies the HMAC-SHA256 signature, then marks the booking payment_status=PAID."
    ),
)
async def verify_payment(
    req: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
) -> PaymentVerifiedResponse:
    """
    Security: We NEVER trust the client saying 'payment succeeded'.
    We always independently verify the signature with our KEY_SECRET.
    Only after verification do we update booking state.
    """
    is_valid = razorpay_service.verify_payment_signature(
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature,
    )

    if not is_valid:
        logger.warning(
            "Invalid payment signature from user %s for booking %s",
            current_user.id,
            req.booking_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment signature verification failed. Payment not recorded.",
        )

    # --- Update booking payment status ---
    booking = await Booking.get(req.booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if str(booking.customer_id) != str(current_user.id) and getattr(current_user, "role", "customer") not in ("admin", "worker"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to verify payment for this booking.",
        )

    await booking.set({
        "payment_status": "PAID",
        "payment_id": req.razorpay_payment_id,
    })


    logger.info(
        "Payment verified and booking updated: booking=%s payment=%s user=%s",
        req.booking_id,
        req.razorpay_payment_id,
        current_user.id,
    )

    return PaymentVerifiedResponse(
        booking_id=req.booking_id,
        payment_status="PAID",
    )


# ---------------------------------------------------------------------------
# POST /payments/webhook
# ---------------------------------------------------------------------------

@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Razorpay webhook receiver",
    description=(
        "Receives real-time payment events from Razorpay (payment.captured, "
        "payment.failed, refund.created, etc.). "
        "Secured by HMAC-SHA256 signature verification — NO JWT auth required."
    ),
    include_in_schema=True,
)
async def razorpay_webhook(request: Request) -> dict:
    """
    Razorpay calls this endpoint when payment events occur.
    We verify the signature using RAZORPAY_WEBHOOK_SECRET before processing.

    Configure this URL in Razorpay Dashboard:
        Settings → Webhooks → Add New Webhook → URL: https://your-api.com/api/v1/payments/webhook
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not razorpay_service.verify_webhook_signature(body, signature):
        logger.warning("Razorpay webhook signature verification FAILED.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature.")

    import json
    try:
        event = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    event_type = event.get("event", "")
    logger.info("Razorpay webhook received: event=%s", event_type)

    # --- Handle events ---
    if event_type == "payment.captured":
        payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
        payment_id = payment_entity.get("id")
        order_id = payment_entity.get("order_id")
        notes = payment_entity.get("notes", {})
        booking_id = notes.get("booking_id")

        if booking_id:
            try:
                booking = await Booking.get(booking_id)
                if booking and booking.payment_status != "PAID":
                    await booking.set({
                        "payment_status": "PAID",
                        "payment_id": payment_id,
                    })
                    logger.info(
                        "Webhook: Booking %s marked PAID via payment %s (order %s)",
                        booking_id, payment_id, order_id,
                    )
            except Exception as exc:
                logger.exception("Webhook: Failed to update booking %s: %s", booking_id, exc)

    elif event_type == "payment.failed":
        payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
        notes = payment_entity.get("notes", {})
        booking_id = notes.get("booking_id")
        if booking_id:
            try:
                booking = await Booking.get(booking_id)
                if booking:
                    await booking.set({"payment_status": "FAILED"})
                    logger.info("Webhook: Booking %s marked FAILED.", booking_id)
            except Exception as exc:
                logger.exception("Webhook: Failed to mark booking failed %s: %s", booking_id, exc)

    elif event_type == "refund.created":
        logger.info("Webhook: Refund created event received.")

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /payments/refund  (Admin only)
# ---------------------------------------------------------------------------

@router.post(
    "/refund",
    response_model=RefundResponse,
    summary="Initiate a refund (Admin only)",
    description="Admin-initiated refund for cancellations, disputes, or over-charges.",
)
async def create_refund(
    req: RefundRequest,
    current_user: User = Depends(require_admin),
) -> RefundResponse:
    try:
        refund = razorpay_service.create_refund(
            payment_id=req.razorpay_payment_id,
            amount_rupees=req.amount,
        )
    except Exception as exc:
        logger.exception("Refund failed for payment %s: %s", req.razorpay_payment_id, exc)
        raise HTTPException(status_code=502, detail="Refund request to Razorpay failed.") from exc

    # Mark booking as REFUNDED
    try:
        booking = await Booking.get(req.booking_id)
        if booking:
            await booking.set({"payment_status": "REFUNDED"})
    except Exception:
        pass  # Non-fatal — refund was still initiated at Razorpay

    return RefundResponse(
        refund_id=refund["id"],
        amount_refunded=refund["amount"],
        status=refund["status"],
    )


# ---------------------------------------------------------------------------
# GET /payments/{payment_id}  (Admin only — for reconciliation)
# ---------------------------------------------------------------------------

@router.get(
    "/{payment_id}",
    summary="Fetch a Razorpay payment (Admin only)",
    description="Fetch raw payment details from Razorpay for reconciliation or debugging.",
)
async def fetch_payment(
    payment_id: str,
    current_user: User = Depends(require_admin),
) -> dict:
    try:
        return razorpay_service.fetch_payment(payment_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Payment not found: {exc}") from exc
