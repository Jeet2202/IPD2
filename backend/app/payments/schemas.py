"""
Payment Pydantic schemas — request validation and response serialization.

Endpoints:
    POST /payments/create-order   → CreateOrderRequest / OrderCreatedResponse
    POST /payments/verify         → VerifyPaymentRequest / PaymentVerifiedResponse
    POST /payments/webhook        → (raw bytes, no schema)
    POST /payments/refund         → RefundRequest / RefundResponse
"""

from enum import Enum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PaymentType(str, Enum):
    """Which step of the booking flow triggered this payment."""
    INSPECTION_FEE       = "inspection_fee"       # ₹99 diagnostic visit charge
    QUOTATION_ADVANCE    = "quotation_advance"     # Partial advance after quotation approval
    FINAL_SETTLEMENT     = "final_settlement"      # Remaining balance after job completion
    FULL_SERVICE_PAYMENT = "full_service_payment"  # One-shot payment for standard services


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CreateOrderRequest(BaseModel):
    """
    POST /payments/create-order

    The Flutter app sends this BEFORE showing the Razorpay checkout modal.
    The backend creates the order with Razorpay and returns the order_id that
    the Flutter SDK needs to open the payment sheet.
    """
    booking_id: str = Field(
        ...,
        description="MongoDB ObjectId of the associated Booking document.",
        examples=["64a1f9c3e3d4e5b6f7a8b9c0"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Amount in Indian Rupees (e.g. 99.0 for ₹99 inspection fee).",
        examples=[99.0, 1101.0],
    )
    payment_type: PaymentType = Field(
        default=PaymentType.INSPECTION_FEE,
        description="Stage of the booking flow this payment belongs to.",
    )
    notes: dict | None = Field(
        default=None,
        description="Optional metadata attached to the Razorpay order.",
    )


class VerifyPaymentRequest(BaseModel):
    """
    POST /payments/verify

    Sent by Flutter IMMEDIATELY after the Razorpay checkout modal closes with
    success. The three fields come directly from PaymentSuccessResponse in the
    razorpay_flutter SDK.

    Backend verifies the HMAC-SHA256 signature, then marks the booking PAID.
    """
    booking_id: str = Field(..., description="MongoDB ObjectId of the booking.")
    razorpay_order_id: str = Field(..., description="Order ID returned by create-order.")
    razorpay_payment_id: str = Field(..., description="Payment ID from Razorpay gateway.")
    razorpay_signature: str = Field(..., description="HMAC-SHA256 signature from Razorpay.")


class RefundRequest(BaseModel):
    """
    POST /payments/refund

    Admin-initiated refund (cancellations, disputes, over-charges).
    """
    booking_id: str = Field(..., description="MongoDB ObjectId of the booking to refund.")
    razorpay_payment_id: str = Field(..., description="The captured payment to refund.")
    amount: float | None = Field(
        default=None,
        description="Amount in rupees to refund. Omit for full refund.",
    )
    reason: str | None = Field(
        default=None,
        max_length=255,
        description="Internal reason for the refund (not shown to customer).",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class OrderCreatedResponse(BaseModel):
    """
    Returned by POST /payments/create-order.

    Flutter reads order_id and key_id to open the Razorpay checkout modal.
    """
    success: bool = True
    order_id: str = Field(..., description="Razorpay order ID (e.g. 'order_xxxxx').")
    amount: int = Field(..., description="Amount in paise (rupees × 100).")
    currency: str = Field(default="INR")
    key_id: str = Field(..., description="Razorpay publishable key — safe to send to client.")


class PaymentVerifiedResponse(BaseModel):
    """Returned by POST /payments/verify on successful signature check."""
    success: bool = True
    message: str = "Payment verified and booking updated."
    booking_id: str
    payment_status: str = "PAID"


class RefundResponse(BaseModel):
    """Returned by POST /payments/refund."""
    success: bool = True
    refund_id: str
    amount_refunded: int = Field(..., description="Amount refunded in paise.")
    status: str
