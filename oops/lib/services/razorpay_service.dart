// lib/services/razorpay_service.dart
//
// Razorpay payment service for the Ally app.
//
// Usage:
//   final svc = RazorpayService();
//   svc.init(
//     onSuccess: (res) => ...,
//     onFailure: (res) => ...,
//   );
//   await svc.openInspectionPayment(bookingId: id, amountRupees: 99.0, ...);
//   // in dispose():
//   svc.dispose();

import 'package:flutter/material.dart';
import 'package:razorpay_flutter/razorpay_flutter.dart';

import '../constants/api_endpoints.dart';
import '../services/api_service.dart';

/// Lightweight wrapper around the Razorpay Flutter SDK.
///
/// Responsibilities:
///   1. Call backend to create a Razorpay order.
///   2. Open the native Razorpay checkout sheet.
///   3. On success → call backend /payments/verify.
///   4. Expose callbacks so calling widgets can react.
class RazorpayService {
  late final Razorpay _razorpay;

  // Caller-provided callbacks
  VoidCallback? _onPaymentSuccess;
  void Function(String message)? _onPaymentFailure;

  bool _isInitialised = false;

  // ---------------------------------------------------------------------------
  // Lifecycle
  // ---------------------------------------------------------------------------

  /// Initialise the SDK and register event listeners.
  ///
  /// Call this in initState() of your screen.
  /// [onSuccess] is called AFTER backend verification succeeds.
  /// [onFailure] receives a human-readable error message.
  void init({
    required VoidCallback onSuccess,
    required void Function(String message) onFailure,
  }) {
    if (_isInitialised) return;

    _onPaymentSuccess = onSuccess;
    _onPaymentFailure = onFailure;

    _razorpay = Razorpay();
    _razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, _handleSuccess);
    _razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, _handleFailure);
    _razorpay.on(Razorpay.EVENT_EXTERNAL_WALLET, _handleExternalWallet);

    _isInitialised = true;
    debugPrint('[RazorpayService] Initialised.');
  }

  /// Release Razorpay SDK resources.
  ///
  /// Call this in dispose() of your screen.
  void dispose() {
    if (!_isInitialised) return;
    _razorpay.clear();
    _isInitialised = false;
    debugPrint('[RazorpayService] Disposed.');
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /// Open a Razorpay payment sheet for the ₹99 inspection fee.
  ///
  /// Steps:
  ///   1. POST /payments/create-order → get order_id + key_id from backend.
  ///   2. Open Razorpay native checkout.
  ///   3. Razorpay SDK fires _handleSuccess or _handleFailure.
  Future<void> openInspectionPayment({
    required String bookingId,
    double amountRupees = 99.0,
    required String customerName,
    required String customerPhone,
    required String customerEmail,
  }) async {
    await _openPayment(
      bookingId: bookingId,
      amountRupees: amountRupees,
      paymentType: 'inspection_fee',
      description: 'Diagnostic Visit Inspection Fee',
      customerName: customerName,
      customerPhone: customerPhone,
      customerEmail: customerEmail,
    );
  }

  /// Open a Razorpay payment sheet for a quotation or final settlement.
  Future<void> openServicePayment({
    required String bookingId,
    required double amountRupees,
    required String description,
    required String customerName,
    required String customerPhone,
    required String customerEmail,
    String paymentType = 'final_settlement',
  }) async {
    await _openPayment(
      bookingId: bookingId,
      amountRupees: amountRupees,
      paymentType: paymentType,
      description: description,
      customerName: customerName,
      customerPhone: customerPhone,
      customerEmail: customerEmail,
    );
  }

  String? _activeBookingId;

  // ---------------------------------------------------------------------------
  // Internal helpers
  // ---------------------------------------------------------------------------

  Future<void> _openPayment({
    required String bookingId,
    required double amountRupees,
    required String paymentType,
    required String description,
    required String customerName,
    required String customerPhone,
    required String customerEmail,
  }) async {
    assert(_isInitialised, 'RazorpayService.init() must be called before opening a payment.');
    _activeBookingId = bookingId;

    // 1. Create order on backend
    late Map<String, dynamic> orderData;
    try {
      orderData = await ApiService.instance.post(
        ApiEndpoints.paymentsCreateOrder,
        {
          'booking_id': bookingId,
          'amount': amountRupees,
          'payment_type': paymentType,
        },
      ) as Map<String, dynamic>;
    } on ApiException catch (e) {
      debugPrint('[RazorpayService] Backend order creation failed: ${e.message}');
      _onPaymentFailure?.call(e.message);
      return;
    } catch (e) {
      debugPrint('[RazorpayService] Unexpected error during order creation: $e');
      _onPaymentFailure?.call('Could not connect to payment server. Please try again.');
      return;
    }

    final String orderId = orderData['order_id'] as String;
    final String keyId = orderData['key_id'] as String;

    // Clean prefill contact/email for Razorpay Test Mode modal stability
    final cleanPhone = customerPhone.replaceAll(RegExp(r'\D'), '');
    final prefillContact = cleanPhone.length >= 10 ? cleanPhone.substring(cleanPhone.length - 10) : customerPhone;
    final prefillEmail = (customerEmail.trim().isNotEmpty && customerEmail.contains('@'))
        ? customerEmail.trim()
        : 'customer@ally.com';

    // 2. Open Razorpay checkout
    final options = <String, dynamic>{
      'key': keyId,
      'amount': (amountRupees * 100).toInt(),  // Razorpay expects paise
      'name': 'Ally Services',
      'order_id': orderId,
      'description': description,
      'prefill': {
        'name': customerName.isNotEmpty ? customerName : 'Customer',
        'contact': prefillContact,
        'email': prefillEmail,
      },
      'theme': {
        'color': '#2563EB',  // Ally brand blue
      },
    };

    debugPrint('[RazorpayService] Opening checkout for order: $orderId');
    try {
      _razorpay.open(options);
    } catch (e) {
      debugPrint('[RazorpayService] Failed to open Razorpay checkout: $e');
      _onPaymentFailure?.call('Could not open payment screen. Please try again.');
    }
  }

  bool _isVerifying = false;

  // ---------------------------------------------------------------------------
  // Event handlers (called by Razorpay SDK)
  // ---------------------------------------------------------------------------

  /// Fired by SDK when user completes payment successfully.
  /// We MUST verify the signature on backend before trusting this.
  Future<void> _handleSuccess(PaymentSuccessResponse response) async {
    if (_isVerifying) return;
    _isVerifying = true;

    debugPrint('[RazorpayService] Payment success callback fired: ${response.paymentId}');

    final orderId = response.orderId;
    final paymentId = response.paymentId;
    final signature = response.signature;

    if (orderId == null || orderId.trim().isEmpty ||
        paymentId == null || paymentId.trim().isEmpty ||
        signature == null || signature.trim().isEmpty) {
      _isVerifying = false;
      debugPrint('[RazorpayService] Missing payment fields in success response');
      _onPaymentFailure?.call('Payment response was incomplete. Please contact support if money was deducted.');
      return;
    }

    final bookingId = _activeBookingId ?? '';

    // Verify signature on backend
    try {
      await ApiService.instance.post(
        ApiEndpoints.paymentsVerify,
        {
          'booking_id': bookingId,
          'razorpay_order_id': orderId,
          'razorpay_payment_id': paymentId,
          'razorpay_signature': signature,
        },
      );
      debugPrint('[RazorpayService] Signature verified. Payment confirmed.');
      _isVerifying = false;
      _onPaymentSuccess?.call();
    } on ApiException catch (e) {
      _isVerifying = false;
      debugPrint('[RazorpayService] Signature verification failed: ${e.message}');
      _onPaymentFailure?.call('Payment verification failed. Please contact support.');
    } catch (e) {
      _isVerifying = false;
      debugPrint('[RazorpayService] Unexpected verification error: $e');
      _onPaymentFailure?.call('Payment recorded but verification error occurred. Contact support.');
    }
  }

  /// Fired by SDK when payment fails or user cancels.
  void _handleFailure(PaymentFailureResponse response) {
    _isVerifying = false;
    debugPrint('[RazorpayService] Payment failed: code=${response.code} msg=${response.message}');
    final msg = response.code == Razorpay.PAYMENT_CANCELLED
        ? 'Payment was cancelled.'
        : 'Payment failed: ${response.message ?? "Unknown error"}';
    _onPaymentFailure?.call(msg);
  }

  /// Fired when user selects an external wallet (Paytm, etc).
  void _handleExternalWallet(ExternalWalletResponse response) {
    _isVerifying = false;
    final walletName = response.walletName ?? 'external wallet';
    debugPrint('[RazorpayService] External wallet selected: $walletName');
    _onPaymentFailure?.call('External wallet selected ($walletName). If payment was not completed, please retry.');
  }
}
