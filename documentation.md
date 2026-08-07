# Complete Payment Flow & Razorpay Setup Guide (Customer & Worker)

This document provides a comprehensive analysis and step-by-step implementation guide for integrating **Razorpay** into the **KaamSetu / Ally (IPD2)** platform for direct APK distribution and local testing/production readiness.

---

## 1. System Payment Architecture & Workflows

The platform consists of two primary user roles—**Customer** and **Worker (Partner)**—managed by the **FastAPI Backend** and monitored via the **Admin Dashboard**.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Customer App    │ ───►  │ FastAPI Backend │ ───►  │ Razorpay API    │
│ (Flutter)       │       │ (Python)        │       │ Gateway         │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ Worker App      │ ◄───► │ MongoDB Database│
│ (Partner)       │       │ (Bookings/Wallet│
└─────────────────┘       └─────────────────┘
```

---

## 2. Detailed Payment Logic & Financial Lifecycle

### Flow A: Diagnostic / Inspection Booking (₹99 Fee)

1. **Trigger**: Customer requests an inspection visit for a service (e.g., Electrical, Plumbing, Appliance Repair).
2. **Standard Inspection Charge**: Fixed at **₹99.00**.
3. **Pre-Booking Payment**:
   - Customer lands on `InspectionSummaryScreen`.
   - Customer taps **Pay ₹99 & Book Inspection**.
   - Flutter calls Backend `POST /api/v1/payments/create-order` with `amount: 99.0`, `booking_type: "inspection_request"`.
   - Backend calls Razorpay API to generate a `razorpay_order_id` (amount in paise: `9900`).
   - Flutter opens native Razorpay checkout modal (UPI, Google Pay, PhonePe, Cards, NetBanking).
   - Upon successful payment, Razorpay SDK returns `razorpay_payment_id`, `razorpay_order_id`, `razorpay_signature`.
   - Flutter calls Backend `POST /api/v1/payments/verify`.
   - Backend verifies HMAC-SHA256 signature using `RAZORPAY_KEY_SECRET`.
   - On valid signature:
     - `payment_status` is updated to `PAID`.
     - Booking status changes to `SEARCHING_WORKER` / `PENDING_ASSIGNMENT`.
     - Inspection payment record is stored in DB with `is_deductible: true`.

---

### Flow B: Worker Inspection & Quotation Submission (₹99 Waiver / Credit)

1. **Worker Arrival & Diagnostic**: Worker arrives at customer location and inspects problem.
2. **Quotation Generation**: Worker submits itemized quotation in Worker App (`QuotationFormScreen`):
   - Example: Labour = ₹800, Spare Parts = ₹400 → **Gross Total = ₹1,200**.
3. **Inspection Fee Adjustment Logic (100% Deduction)**:
   - System checks if customer has paid ₹99 inspection charge for this booking.
   - If paid:
     - `Gross Total` = ₹1,200.00
     - `Inspection Credit Applied` = -₹99.00
     - `Net Amount Payable by Customer` = **₹1,101.00**
4. **Customer Quotation Approval**:
   - Customer receives quotation in Customer App.
   - Customer approves & pays advance/full amount via Razorpay.

---

### Flow C: Work Completion & Final Bill Settlement

1. **Job Completion**: Worker finishes work and submits final invoice in `WorkerCompleteWorkScreen`.
2. **Settlement Modes**:
   - **Online Payment (Razorpay)**:
     - Customer pays net balance via Razorpay UPI / Card.
     - Backend verifies payment → updates booking `payment_status: PAID`.
     - Worker Wallet is credited: `Net Earnings = Total Amount - Platform Commission %`.
   - **Cash Payment (Pay After Service)**:
     - Customer pays cash directly to worker.
     - Worker confirms receipt in app.
     - Platform Commission is debited from Worker's Wallet balance.

---

### Flow D: Worker Payouts & Wallet Withdrawal

1. **Earnings Accumulation**: All online completed jobs credit worker's in-app wallet balance (`Worker.wallet_balance`).
2. **Payout Methods**:
   - Worker inputs Bank Account / UPI ID in `PaymentAccountsScreen`.
   - Payout requested via `WalletScreen`.
   - Admin approves payout or automated Razorpay Route / RazorpayX Payout API transfers funds directly to worker bank account.

---

## 3. Backend Setup & API Implementation (FastAPI)

### Step 3.1: Add Dependencies & Environment Variables

Add to `backend/requirements.txt`:
```txt
razorpay>=1.4.1
```

Add to `backend/.env`:
```env
# Razorpay Credentials (Use rzp_test_... for testing, rzp_live_... for production)
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Step 3.2: Create Razorpay Service (`backend/app/payments/service.py`)

```python
import hmac
import hashlib
import razorpay
from app.core.config import settings

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, amount_in_rupees: float, receipt_id: str, notes: dict = None) -> dict:
        amount_in_paise = int(amount_in_rupees * 100)
        data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt_id,
            "notes": notes or {}
        }
        order = self.client.order.create(data=data)
        return order

    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(generated_signature, razorpay_signature)

razorpay_service = RazorpayService()
```

---

### Step 3.3: Payment Router (`backend/app/payments/router.py`)

```python
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from app.payments.service import razorpay_service

router = APIRouter(prefix="/payments", tags=["Payments"])

class CreateOrderRequest(BaseModel):
    booking_id: str
    amount: float
    payment_type: str = "inspection_fee"  # inspection_fee, quotation, final_settlement

class VerifyPaymentRequest(BaseModel):
    booking_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order")
async def create_payment_order(req: CreateOrderRequest):
    try:
        order = razorpay_service.create_order(
            amount_in_rupees=req.amount,
            receipt_id=f"rcpt_{req.booking_id}",
            notes={"booking_id": req.booking_id, "type": req.payment_type}
        )
        return {
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": settings.RAZORPAY_KEY_ID
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify")
async def verify_payment(req: VerifyPaymentRequest):
    is_valid = razorpay_service.verify_payment_signature(
        razorpay_order_id=req.razorpay_order_id,
        razorpay_payment_id=req.razorpay_payment_id,
        razorpay_signature=req.razorpay_signature
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    
    # Update booking payment_status in database to 'PAID'
    # await booking_service.mark_as_paid(req.booking_id, req.razorpay_payment_id)
    
    return {"success": True, "message": "Payment verified successfully"}
```

---

## 4. Flutter Integration Guide (`oops` App)

### Step 4.1: Add `razorpay_flutter` Package

In `oops/pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  razorpay_flutter: ^1.3.7
```
Run command: `flutter pub get`

---

### Step 4.2: Android Native Configuration (`AndroidManifest.xml`)

Ensure minimum SDK version in `oops/android/app/build.gradle` is set to at least 21:
```groovy
defaultConfig {
    minSdkVersion 21
    targetSdkVersion 34
}
```

Add inside `oops/android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

---

### Step 4.3: Razorpay Helper Utility (`lib/services/razorpay_helper.dart`)

```dart
import 'package:flutter/material.dart';
import 'package:razorpay_flutter/razorpay_flutter.dart';

class RazorpayHelper {
  late Razorpay _razorpay;
  final Function(PaymentSuccessResponse) onSuccess;
  final Function(PaymentFailureResponse) onFailure;
  final Function(ExternalWalletResponse)? onExternalWallet;

  RazorpayHelper({
    required this.onSuccess,
    required this.onFailure,
    this.onExternalWallet,
  }) {
    _razorpay = Razorpay();
    _razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, onSuccess);
    _razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, onFailure);
    if (onExternalWallet != null) {
      _razorpay.on(Razorpay.EVENT_EXTERNAL_WALLET, onExternalWallet!);
    }
  }

  void openCheckout({
    required String razorpayKeyId,
    required String orderId,
    required double amountInRupees,
    required String name,
    required String description,
    required String userPhone,
    required String userEmail,
  }) {
    var options = {
      'key': razorpayKeyId,
      'amount': (amountInRupees * 100).toInt(),
      'name': name,
      'order_id': orderId,
      'description': description,
      'prefill': {
        'contact': userPhone,
        'email': userEmail,
      },
      'external': {
        'wallets': ['paytm', 'gpay', 'phonepe']
      }
    };

    try {
      _razorpay.open(options);
    } catch (e) {
      debugPrint('Error launching Razorpay: $e');
    }
  }

  void dispose() {
    _razorpay.clear();
  }
}
```

---

### Step 4.4: Connect Payment in `InspectionSummaryScreen` (₹99 Fee)

Update `lib/customer/inspection_booking/inspection_summary/inspection_summary_screen.dart`:

```dart
void _openRazorpayForInspection() async {
  // 1. Create order on backend
  final orderData = await ApiService.instance.post('/payments/create-order', {
    'booking_id': 'temp_id',
    'amount': 99.0,
    'payment_type': 'inspection_fee',
  });

  final String orderId = orderData['order_id'];
  final String keyId = orderData['key_id'];

  // 2. Launch Razorpay SDK
  final razorpayHelper = RazorpayHelper(
    onSuccess: (PaymentSuccessResponse response) async {
      // 3. Verify on backend
      await ApiService.instance.post('/payments/verify', {
        'razorpay_order_id': response.orderId,
        'razorpay_payment_id': response.paymentId,
        'razorpay_signature': response.signature,
      });
      // 4. Submit booking & navigate to success
      _submitBookingPayload();
    },
    onFailure: (PaymentFailureResponse response) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Payment Failed: ${response.message}')),
      );
    },
  );

  razorpayHelper.openCheckout(
    razorpayKeyId: keyId,
    orderId: orderId,
    amountInRupees: 99.0,
    name: 'Ally Services',
    description: 'Diagnostic Visit Inspection Fee',
    userPhone: '9876543210',
    userEmail: 'customer@example.com',
  );
}
```

---

## 5. APK Building & WhatsApp Sharing Checklist

Since you are distributing the APK via WhatsApp directly to users without Play Store publishing:

1. **Generate Release APK**:
   ```bash
   cd oops
   flutter build apk --release
   ```
   The generated APK will be located at:
   `oops/build/app/outputs/flutter-apk/app-release.apk`

2. **Razorpay Key Mode**:
   - Ensure you use **Razorpay Live Key ID (`rzp_live_...`)** for real payments or **Test Key ID (`rzp_test_...`)** for testing with dummy UPI IDs/cards.
   - For direct WhatsApp distribution, users will install the APK via "Unknown Sources" on Android. Razorpay SDK works seamlessly on sideloaded release APKs.

3. **Backend Accessibility**:
   - Ensure your backend API URL in `.env.production` is hosted on a public domain/server (e.g. AWS, Render, DigitalOcean) with HTTPS enabled, so WhatsApp APK users can reach your server from any network.

---

## Summary Table of Fee & Deduction Rules

| Phase | Flow | Amount | Customer Action | Worker Action | Backend/System Action |
|---|---|---|---|---|---|
| **1. Diagnostic** | Inspection Booking | **₹99** | Pays ₹99 via Razorpay | Receives visit notification | Stores payment with `is_deductible: true` |
| **2. Quotation** | Site Diagnostic | **Itemized** | Reviews & approves | Submits breakdown (e.g. ₹1,200) | Automatically subtracts ₹99 → Net ₹1,101 |
| **3. Execution** | Work Completion | **Remaining Net** | Pays ₹1,101 via Razorpay/Cash | Completes work & uploads photos | Marks booking `COMPLETED`, updates Worker Wallet |
| **4. Payout** | Earnings Withdrawal | **Wallet Balance** | N/A | Requests Payout | Transfers earnings to Worker Bank/UPI |
