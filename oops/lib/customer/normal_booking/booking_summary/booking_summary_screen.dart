// File: lib/customer/normal_booking/booking_summary/booking_summary_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_dimensions.dart';
import '../../../models/address_model.dart';
import '../../../models/booking_model.dart';
import '../../../models/service_model.dart';
import '../../../services/api_service.dart';
import '../../../services/booking_service.dart';

class BookingSummaryScreen extends StatefulWidget {
  final ServiceModel? service;
  final AddressModel? address;
  final String? bookingType;
  final String? scheduledDate;
  final String? scheduledTime;
  final String? customerNotes;

  const BookingSummaryScreen({
    super.key,
    this.service,
    this.address,
    this.bookingType,
    this.scheduledDate,
    this.scheduledTime,
    this.customerNotes,
  });

  @override
  State<BookingSummaryScreen> createState() => _BookingSummaryScreenState();
}

class _BookingSummaryScreenState extends State<BookingSummaryScreen> {
  final BookingService _bookingService = BookingService.instance;

  ServiceModel? _service;
  AddressModel? _address;
  String _bookingType = 'normal_service';
  String? _scheduledDate;
  String? _scheduledTime;
  String? _customerNotes;
  String? _problemDescription;

  String? _customTitle;
  String? _customDescription;
  double? _customBudget;
  String? _categorySlug;
  List<String> _problemPhotos = [];

  bool _isSubmitting = false;
  String? _submitError;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _extractArgs();
    });
  }

  void _extractArgs() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic>) {
      setState(() {
        _service = args['service'] as ServiceModel?;
        _address = args['address'] as AddressModel?;
        _bookingType = args['booking_type'] as String? ?? 'normal_service';
        _scheduledDate = args['scheduled_date'] as String?;
        _scheduledTime = args['scheduled_time'] as String?;
        _customerNotes = args['customer_notes'] as String?;
        _problemDescription = args['problem_description'] as String?;
        _customTitle = args['custom_title'] as String?;
        _customDescription = args['custom_description'] as String?;
        _customBudget = (args['custom_budget'] as num?)?.toDouble();
        _categorySlug = args['category_slug'] as String?;
        _problemPhotos = (args['problem_photos'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];
      });
    } else {
      setState(() {
        _service = widget.service;
        _address = widget.address;
        _bookingType = widget.bookingType ?? 'normal_service';
        _scheduledDate = widget.scheduledDate;
        _scheduledTime = widget.scheduledTime;
        _customerNotes = widget.customerNotes;
      });
    }
  }

  Future<void> _confirmAndBook() async {
    if (_address == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Missing address details. Please go back and select.')),
      );
      return;
    }

    if (_bookingType == 'normal_service' && _service == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Missing service selection. Please go back and select a service.')),
      );
      return;
    }

    setState(() {
      _isSubmitting = true;
      _submitError = null;
    });

    try {
      final payload = CreateBookingPayload(
        serviceId: _service?.id,
        addressId: _address!.id,
        bookingType: _bookingType,
        scheduledDate: _scheduledDate,
        scheduledTime: _scheduledTime,
        customerNotes: _customerNotes,
        problemDescription: _problemDescription,
        problemPhotos: _problemPhotos,
        customTitle: _customTitle,
        customDescription: _customDescription,
        customBudget: _customBudget,
        categorySlug: _categorySlug,
      );

      final bookingResult = await _bookingService.createBooking(payload);

      if (!mounted) return;

      setState(() => _isSubmitting = false);

      // Navigate to Booking Success Screen, replacing summary screen
      Navigator.pushNamedAndRemoveUntil(
        context,
        AppRoutes.bookingSuccess,
        (route) => route.isFirst || route.settings.name == AppRoutes.customerHome,
        arguments: {'booking': bookingResult},
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _isSubmitting = false;
        _submitError = e.message;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.message),
          backgroundColor: AppColors.error,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSubmitting = false;
        _submitError = 'An unexpected error occurred. Please try again.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Network error. Please check your connection and try again.'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final service = _service;
    final address = _address;

    if (address == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Booking Summary')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.info_outline_rounded, size: 48, color: AppColors.warning),
              const SizedBox(height: 12),
              const Text('Incomplete booking information.', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Go Back'),
              ),
            ],
          ),
        ),
      );
    }

    final displayTitle = service?.name ?? _customTitle ?? 'Inspection Visit (${_categorySlug ?? "General"})';
    final priceDisplay = service != null
        ? (service.priceRangeDisplay.isNotEmpty ? service.priceRangeDisplay : '₹${service.basePrice.toStringAsFixed(0)}')
        : (_customBudget != null ? '₹${_customBudget!.toStringAsFixed(0)} (Estimated)' : 'Free Visit / Quote Pending');

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Column(
          children: [
            Text(
              'Step 2 of 2',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.primary),
            ),
            Text(
              'Booking Summary',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_submitError != null) ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF2F2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFFCA5A5)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline_rounded, color: AppColors.error, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _submitError!,
                            style: const TextStyle(fontSize: 13, color: AppColors.error),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],

                // ── Service Details Summary Card ───────────────────────
                _buildSummaryCard(
                  title: 'Service Selected',
                  icon: Icons.build_circle_rounded,
                  content: Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          width: 50,
                          height: 50,
                          color: const Color(0xFFF1F5F9),
                          child: service != null
                              ? Image.network(
                                  service.resolvedImage,
                                  fit: BoxFit.cover,
                                  errorBuilder: (_, __, ___) => const Icon(Icons.handyman_rounded, color: AppColors.primary, size: 24),
                                )
                              : Icon(
                                  _bookingType == 'inspection_request'
                                      ? Icons.search_rounded
                                      : Icons.assignment_rounded,
                                  color: AppColors.primary,
                                  size: 24,
                                ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              displayTitle,
                              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Category: ${(service?.categorySlug ?? "general").replaceAll('-', ' ').toUpperCase()}',
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        priceDisplay,
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppColors.primary),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Address Card ──────────────────────────────────────
                _buildSummaryCard(
                  title: 'Service Address',
                  icon: Icons.location_on_rounded,
                  onChangeTap: () => Navigator.pop(context),
                  content: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            address.label,
                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                          ),
                          const SizedBox(width: 8),
                          Text('(${address.fullName} • ${address.phone})', style: const TextStyle(fontSize: 12)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        address.shortAddress,
                        style: const TextStyle(fontSize: 13, height: 1.3),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Date, Time & Booking Type Card ─────────────────────
                _buildSummaryCard(
                  title: 'Schedule & Type',
                  icon: Icons.calendar_month_rounded,
                  onChangeTap: () => Navigator.pop(context),
                  content: Column(
                    children: [
                      _buildRow('Booking Type', _bookingType == 'inspection_request' ? 'Inspection Visit' : 'Normal Service', isBold: true),
                      const SizedBox(height: 6),
                      _buildRow('Scheduled Date', _scheduledDate ?? 'ASAP'),
                      const SizedBox(height: 6),
                      _buildRow('Scheduled Time', _scheduledTime ?? 'Flexible'),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Customer Notes Card ───────────────────────────────
                if (_customerNotes != null && _customerNotes!.isNotEmpty) ...[
                  _buildSummaryCard(
                    title: 'Customer Notes',
                    icon: Icons.note_alt_rounded,
                    onChangeTap: () => Navigator.pop(context),
                    content: Text(
                      '"$_customerNotes"',
                      style: const TextStyle(fontSize: 13, fontStyle: FontStyle.italic),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // ── Estimated Price Breakdown Card ────────────────────
                _buildSummaryCard(
                  title: 'Price Estimate',
                  icon: Icons.receipt_long_rounded,
                  content: Column(
                    children: [
                      _buildRow(
                        'Base / Estimated Price',
                        service != null
                            ? '₹${service.basePrice.toStringAsFixed(0)}'
                            : (_customBudget != null ? '₹${_customBudget!.toStringAsFixed(0)}' : 'To be quoted'),
                      ),
                      const SizedBox(height: 6),
                      _buildRow(
                        'Estimated Duration',
                        service != null
                            ? (service.durationDisplay.isNotEmpty ? service.durationDisplay : '${service.estimatedDurationMinutes} mins')
                            : 'Site visit / Quote dependent',
                      ),
                      const SizedBox(height: 8),
                      const Divider(color: AppColors.divider, height: 1),
                      const SizedBox(height: 8),
                      _buildRow('Total Estimated Pay', priceDisplay, isBold: true),
                    ],
                  ),
                ),

                const SizedBox(height: 120),
              ],
            ),
          ),

          // ── Sticky Bottom Confirm CTA ───────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.08),
                    blurRadius: 20,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text('Total Estimated', style: TextStyle(fontSize: 11)),
                      const SizedBox(height: 2),
                      Text(
                        priceDisplay,
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppColors.primary),
                      ),
                    ],
                  ),
                  const SizedBox(width: 20),
                  Expanded(
                    child: SizedBox(
                      height: 52,
                      child: ElevatedButton(
                        onPressed: _isSubmitting ? null : _confirmAndBook,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                          ),
                        ),
                        child: _isSubmitting
                            ? const SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                              )
                            : const Text(
                                'Confirm & Book',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard({
    required String title,
    required IconData icon,
    required Widget content,
    VoidCallback? onChangeTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(icon, size: 18, color: AppColors.primary),
                  const SizedBox(width: 8),
                  Text(
                    title,
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                  ),
                ],
              ),
              if (onChangeTap != null)
                GestureDetector(
                  onTap: onChangeTap,
                  child: const Text('Edit', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
                ),
            ],
          ),
          const SizedBox(height: 12),
          content,
        ],
      ),
    );
  }

  Widget _buildRow(String label, String value, {bool isBold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: isBold ? 14 : 13,
            fontWeight: isBold ? FontWeight.w800 : FontWeight.w500,
            color: isBold ? AppColors.textPrimary : AppColors.textSecondary,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: isBold ? 15 : 13,
            fontWeight: isBold ? FontWeight.w800 : FontWeight.w600,
            color: isBold ? AppColors.primary : AppColors.textPrimary,
          ),
        ),
      ],
    );
  }
}
