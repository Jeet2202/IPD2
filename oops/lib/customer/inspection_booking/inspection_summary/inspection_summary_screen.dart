// File: lib/customer/inspection_booking/inspection_summary/inspection_summary_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../models/address_model.dart';
import '../../../models/booking_model.dart';
import '../../../services/api_service.dart';
import '../../../services/booking_service.dart';
import '../../../services/razorpay_service.dart';
import '../../../utils/token_storage.dart';

class InspectionSummaryScreen extends StatefulWidget {
  const InspectionSummaryScreen({super.key});

  @override
  State<InspectionSummaryScreen> createState() => _InspectionSummaryScreenState();
}

class _InspectionSummaryScreenState extends State<InspectionSummaryScreen> {
  final BookingService _bookingService = BookingService.instance;
  final RazorpayService _razorpayService = RazorpayService();

  AddressModel? _address;
  String _categorySlug = 'electrical';
  String _typeOfWork = 'General Diagnostic Check';
  String _problemDescription = '';
  List<String> _problemPhotos = [];
  String? _scheduledDate;
  String? _scheduledTime;
  String? _customerNotes;
  double _inspectionCharge = 99.0;

  bool _isSubmitting = false;
  String? _pendingBookingId;   // Set before opening Razorpay; used by _submitBookingPayload

  @override
  void initState() {
    super.initState();
    _razorpayService.init(
      onSuccess: () {
        // Razorpay confirmed + backend verified → submit booking
        _submitBookingPayload();
      },
      onFailure: (String message) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message), backgroundColor: AppColors.error),
        );
        setState(() => _isSubmitting = false);
      },
    );
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _extractArgs();
    });
  }

  @override
  void dispose() {
    _razorpayService.dispose();
    super.dispose();
  }

  void _extractArgs() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic>) {
      setState(() {
        _address = args['address'] as AddressModel?;
        _categorySlug = args['category_slug'] as String? ?? 'electrical';
        _typeOfWork = args['type_of_work'] as String? ?? 'General Diagnostic Check';
        _problemDescription = args['problem_description'] as String? ?? '';
        _problemPhotos = (args['problem_photos'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];
        _scheduledDate = args['scheduled_date'] as String?;
        _scheduledTime = args['scheduled_time'] as String?;
        _customerNotes = args['customer_notes'] as String?;
        _inspectionCharge = (args['inspection_charge'] as num?)?.toDouble() ?? 99.0;
      });
    }
  }

  Future<void> _handlePaymentAndBooking() async {
    if (_address == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Missing address. Please go back and select an address.')),
      );
      return;
    }

    // First create the booking to get a real booking_id
    setState(() => _isSubmitting = true);

    String bookingId;
    try {
      final payload = CreateBookingPayload(
        addressId: _address!.id,
        bookingType: 'inspection_request',
        categorySlug: _categorySlug,
        problemDescription: '[$_typeOfWork] $_problemDescription',
        problemPhotos: _problemPhotos,
        scheduledDate: _scheduledDate,
        scheduledTime: _scheduledTime,
        customerNotes: _customerNotes,
      );
      final result = await _bookingService.createBooking(payload);
      bookingId = result.id;
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _isSubmitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message), backgroundColor: AppColors.error),
      );
      return;
    } catch (_) {
      if (!mounted) return;
      setState(() => _isSubmitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Could not create booking. Please try again.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = false);

    // Open Razorpay payment sheet
    // Success callback (_razorpayService.init onSuccess) calls _submitBookingPayload
    _pendingBookingId = bookingId;
    await _razorpayService.openInspectionPayment(
      bookingId: bookingId,
      amountRupees: _inspectionCharge,
      customerName: TokenStorage.userName.isNotEmpty ? TokenStorage.userName : 'Customer',
      customerPhone: TokenStorage.userPhone.isNotEmpty ? TokenStorage.userPhone : '',
      customerEmail: TokenStorage.userEmail.isNotEmpty ? TokenStorage.userEmail : '',
    );
  }

  Future<void> _submitBookingPayload() async {
    // Booking was already created in _handlePaymentAndBooking before opening Razorpay.
    // Payment has been verified by backend. Simply navigate to the success screen.
    if (!mounted) return;
    setState(() => _isSubmitting = false);
    Navigator.pushNamedAndRemoveUntil(
      context,
      AppRoutes.bookingSuccess,
      (route) => route.isFirst || route.settings.name == AppRoutes.customerHome,
      arguments: {'booking_id': _pendingBookingId},
    );
  }

  @override
  Widget build(BuildContext context) {
    final catTitle = _categorySlug.replaceAll('-', ' ').replaceAll('_', ' ').toUpperCase();

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Inspection Summary',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 100),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Diagnostic Overview Banner ───────────────────────
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF2563EB).withValues(alpha: 0.3),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.assignment_turned_in_rounded, color: Colors.white, size: 36),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '$catTitle Inspection',
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.white),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              _typeOfWork,
                              style: const TextStyle(fontSize: 12, color: Color(0xFFDBEAFE)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // ── Schedule & Address Details Card ─────────────────────
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.calendar_today_rounded, size: 18, color: Color(0xFF2563EB)),
                          const SizedBox(width: 10),
                          const Text('Schedule:', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                          const Spacer(),
                          Text(
                            '${_scheduledDate ?? "ASAP"} • ${_scheduledTime ?? "Flexible"}',
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Divider(color: Color(0xFFF1F5F9), height: 1),
                      const SizedBox(height: 12),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(Icons.location_on_rounded, size: 18, color: Color(0xFF2563EB)),
                          const SizedBox(width: 10),
                          const Text('Location:', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _address != null ? '${_address!.label}: ${_address!.shortAddress}' : 'No address selected',
                              textAlign: TextAlign.right,
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // ── Diagnosis Fee Breakdown Card ──────────────────────
                const Text('Fee Breakdown', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                const SizedBox(height: 10),

                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Diagnostic Visit Charge', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                          Text('₹${_inspectionCharge.toStringAsFixed(2)}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Taxes & GST (18%)', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                          Text('Included', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF16A34A))),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Divider(color: Color(0xFFF1F5F9), height: 1),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Total Payable Now', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                          Text('₹${_inspectionCharge.toStringAsFixed(2)}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // ── Fee Waiver Highlight ──────────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: const Color(0xFFBFDBFE)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.workspace_premium_rounded, color: Color(0xFF2563EB), size: 24),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '100% of this ₹99 fee will be deducted from your final repair bill upon quotation approval!',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF1E40AF), height: 1.3),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── Bottom Pay & Book Button ────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha: 0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _handlePaymentAndBooking,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: _isSubmitting
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('Pay ₹99 & Book Inspection', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                            SizedBox(width: 8),
                            Icon(Icons.arrow_forward_rounded, size: 20),
                          ],
                        ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
