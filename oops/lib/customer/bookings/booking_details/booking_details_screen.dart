// File: lib/customer/bookings/booking_details/booking_details_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../models/booking_model.dart';
import '../../../services/api_service.dart';
import '../../../services/booking_service.dart';
import '../../quotations/customer_quotations_screen.dart';

class BookingDetailsScreen extends StatefulWidget {
  final BookingModel? booking;
  final String? bookingId;

  const BookingDetailsScreen({
    super.key,
    this.booking,
    this.bookingId,
  });

  @override
  State<BookingDetailsScreen> createState() => _BookingDetailsScreenState();
}

class _BookingDetailsScreenState extends State<BookingDetailsScreen> {
  final BookingService _bookingService = BookingService.instance;

  BookingModel? _booking;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _booking = widget.booking;

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_booking == null) {
        _extractArgsAndFetch();
      } else {
        setState(() => _isLoading = false);
      }
    });
  }

  void _extractArgsAndFetch() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic>) {
      if (args['booking'] is BookingModel) {
        setState(() {
          _booking = args['booking'] as BookingModel;
          _isLoading = false;
        });
        return;
      }
      final id = args['booking_id'] as String?;
      if (id != null && id.isNotEmpty) {
        _fetchBookingById(id);
        return;
      }
    } else if (args is BookingModel) {
      setState(() {
        _booking = args;
        _isLoading = false;
      });
      return;
    } else if (widget.bookingId != null) {
      _fetchBookingById(widget.bookingId!);
      return;
    }

    setState(() {
      _isLoading = false;
      _errorMessage = 'No booking information provided.';
    });
  }

  Future<void> _fetchBookingById(String id) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final b = await _bookingService.getBookingById(id);
      if (!mounted) return;
      setState(() {
        _booking = b;
        _isLoading = false;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.message;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = 'Failed to load booking details. Please try again.';
        _isLoading = false;
      });
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return const Color(0xFFD97706);
      case 'accepted':
        return const Color(0xFF2563EB);
      case 'in_progress':
        return const Color(0xFF4F46E5);
      case 'completed':
        return const Color(0xFF16A34A);
      case 'cancelled':
        return const Color(0xFFDC2626);
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Booking Details',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _errorMessage != null
                ? _buildErrorView()
                : _booking == null
                    ? const Center(child: Text('Booking not found.'))
                    : SingleChildScrollView(
                        physics: const BouncingScrollPhysics(),
                        padding: const EdgeInsets.all(20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // ── Status Banner Card ─────────────────────────
                            _buildStatusBanner(),

                            const SizedBox(height: 20),

                            // ── Service Details Card ───────────────────────
                            _buildServiceCard(),

                            const SizedBox(height: 20),

                            // ── Address Card ──────────────────────────────
                            _buildAddressCard(),

                            const SizedBox(height: 20),

                            // ── Preferred Schedule Card ───────────────────
                            _buildScheduleCard(),

                            const SizedBox(height: 20),

                            // ── Inspection Problem Description (If Inspection) ──
                            if (_booking!.bookingType == 'inspection_request') ...[
                              _buildInspectionDetailsCard(),
                              const SizedBox(height: 20),
                            ],

                            // ── Customer Notes Card ────────────────────────
                            if (_booking!.customerNotes != null && _booking!.customerNotes!.isNotEmpty) ...[
                              _buildNotesCard(),
                              const SizedBox(height: 20),
                            ],

                            // ── Estimated Price Summary Card ───────────────
                            _buildPriceSummaryCard(),

                            const SizedBox(height: 20),

                            // ── Worker Quotations Button Card ───────────────
                            _buildViewQuotationsCard(),

                            const SizedBox(height: 28),
                          ],
                        ),
                      ),
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 56, color: Color(0xFFDC2626)),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBanner() {
    final statusColor = _getStatusColor(_booking!.status);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: statusColor.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: statusColor.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: statusColor.withValues(alpha: 0.15), shape: BoxShape.circle),
            child: Icon(
              _booking!.status == 'completed'
                  ? Icons.check_circle_rounded
                  : _booking!.status == 'cancelled'
                      ? Icons.cancel_rounded
                      : Icons.sync_rounded,
              color: statusColor,
              size: 24,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      _booking!.bookingNumber,
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: statusColor),
                    ),
                    Text(
                      _booking!.status.toUpperCase(),
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: statusColor),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  _booking!.bookingType == 'inspection_request' ? 'Site Inspection Request' : 'Direct Service Booking',
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildServiceCard() {
    final svc = _booking!.serviceSnapshot;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Service Information', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                child: const Icon(Icons.handyman_rounded, color: AppColors.primary, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(svc.name, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
                    const SizedBox(height: 2),
                    Text('Category: ${svc.categorySlug}', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(color: Color(0xFFF1F5F9), height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Base Market Price', style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
              Text('₹${svc.baseMarketPrice.toStringAsFixed(0)}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Estimated Duration', style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
              Text('${svc.estimatedDurationMinutes} mins', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAddressCard() {
    final addr = _booking!.addressSnapshot;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Service Address', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(Icons.location_on_rounded, color: AppColors.primary, size: 22),
              const SizedBox(width: 10),
              Text(addr.label, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
            ],
          ),
          const SizedBox(height: 8),
          Text(addr.fullName, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          Text(addr.phone, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
          const SizedBox(height: 6),
          Text(
            '${addr.addressLine1}${addr.addressLine2 != null ? ', ${addr.addressLine2}' : ''}\n${addr.landmark != null ? 'Landmark: ${addr.landmark}\n' : ''}${addr.city}, ${addr.state} - ${addr.postalCode}',
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildScheduleCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Schedule Preferences', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(Icons.calendar_month_rounded, color: AppColors.primary, size: 20),
              const SizedBox(width: 10),
              Text(
                'Date: ${_booking!.scheduledDate ?? 'ASAP / On-demand'}',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.access_time_rounded, color: AppColors.primary, size: 20),
              const SizedBox(width: 10),
              Text(
                'Time Slot: ${_booking!.scheduledTime ?? 'ASAP / Flexible'}',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInspectionDetailsCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFBEB),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFFCD34D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.assignment_late_rounded, color: Color(0xFFD97706), size: 20),
              SizedBox(width: 8),
              Text('Inspection Problem Description', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF92400E))),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            _booking!.problemDescription ?? 'No description provided.',
            style: const TextStyle(fontSize: 13, color: Color(0xFF78350F), height: 1.4),
          ),
          if (_booking!.problemPhotos.isNotEmpty) ...[
            const SizedBox(height: 14),
            const Text('Uploaded Photos:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF92400E))),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _booking!.problemPhotos.map((url) {
                return ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.network(
                    url,
                    width: 70,
                    height: 70,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      width: 70,
                      height: 70,
                      color: Colors.grey[300],
                      child: const Icon(Icons.broken_image_rounded, size: 24, color: Colors.grey),
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNotesCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Customer Notes', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textSecondary)),
          const SizedBox(height: 8),
          Text(
            _booking!.customerNotes!,
            style: const TextStyle(fontSize: 13, color: AppColors.textPrimary, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceSummaryCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text('Estimated Price', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
          Text(
            '₹${_booking!.estimatedPrice?.toStringAsFixed(0) ?? '0'}',
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: AppColors.primary),
          ),
        ],
      ),
    );
  }

  Widget _buildViewQuotationsCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFBFDBFE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.request_quote_rounded, color: Color(0xFF2563EB), size: 22),
              SizedBox(width: 10),
              Text(
                'Worker Quotations',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF1E40AF)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Review, compare, and inspect custom price quotations submitted by interested workers.',
            style: TextStyle(fontSize: 12, color: Color(0xFF3B82F6), height: 1.3),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () async {
                final accepted = await Navigator.push<bool>(
                  context,
                  MaterialPageRoute(
                    builder: (context) => CustomerQuotationsScreen(
                      bookingId: _booking!.id,
                      bookingNumber: _booking!.bookingNumber,
                    ),
                  ),
                );
                if (accepted == true && mounted) {
                  _fetchBookingById(_booking!.id);
                }
              },
              icon: const Icon(Icons.list_alt_rounded, size: 18),
              label: const Text('View Received Quotations'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
