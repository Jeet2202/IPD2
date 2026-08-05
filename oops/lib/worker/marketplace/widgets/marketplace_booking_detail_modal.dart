// File: lib/worker/marketplace/widgets/marketplace_booking_detail_modal.dart

import 'package:flutter/material.dart';
import '../../../../models/marketplace_booking_model.dart';
import '../../../../services/job_application_service.dart';
import '../../../../services/marketplace_service.dart';
import '../../quotations/quotation_form_screen.dart';

class MarketplaceBookingDetailModal extends StatefulWidget {
  final String bookingId;

  const MarketplaceBookingDetailModal({
    super.key,
    required this.bookingId,
  });

  static Future<void> show(BuildContext context, String bookingId) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => MarketplaceBookingDetailModal(bookingId: bookingId),
    );
  }

  @override
  State<MarketplaceBookingDetailModal> createState() =>
      _MarketplaceBookingDetailModalState();
}

class _MarketplaceBookingDetailModalState
    extends State<MarketplaceBookingDetailModal> {
  late Future<MarketplaceBookingDetail> _future;

  @override
  void initState() {
    super.initState();
    _future = MarketplaceService.instance
        .fetchMarketplaceBookingDetail(widget.bookingId);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.85,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Drag handle indicator
          const SizedBox(height: 12),
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: const Color(0xFFCBD5E1),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 12),

          Expanded(
            child: FutureBuilder<MarketplaceBookingDetail>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(
                    child: CircularProgressIndicator(color: Color(0xFF2563EB)),
                  );
                }

                if (snapshot.hasError) {
                  return Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline_rounded,
                            size: 48, color: Color(0xFFEF4444)),
                        const SizedBox(height: 12),
                        Text(
                          'Failed to load booking details',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          snapshot.error.toString(),
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF64748B),
                          ),
                        ),
                      ],
                    ),
                  );
                }

                final detail = snapshot.data!;
                return _buildDetailContent(detail);
              },
            ),
          ),
        ],
      ),
    );
  }

  String? _applicationId;

  Widget _buildDetailContent(MarketplaceBookingDetail detail) {
    if (detail.hasApplied && !_hasApplied) {
      _hasApplied = true;
      if (detail.applicationId != null) {
        _applicationId = detail.applicationId;
      }
    }
    final isInspection = detail.isInspection;
    final primaryColor =
        isInspection ? const Color(0xFF8B5CF6) : const Color(0xFF2563EB);

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Booking Number & Type Badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  isInspection ? 'Inspection Request' : 'Standard Service',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: primaryColor,
                  ),
                ),
              ),
              Text(
                detail.bookingNumber,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Service Title
          Text(
            detail.serviceName,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A),
              letterSpacing: -0.4,
            ),
          ),

          const SizedBox(height: 16),

          // Section 1: Overview Grid
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              children: [
                _buildInfoRow(
                  icon: Icons.location_on_rounded,
                  title: 'Approximate Location',
                  value: detail.address.approximateLocation,
                  subvalue: 'Exact customer address shared upon job assignment',
                ),
                const Divider(height: 20, color: Color(0xFFE2E8F0)),
                _buildInfoRow(
                  icon: Icons.calendar_month_rounded,
                  title: 'Scheduled Date',
                  value: detail.scheduledDate ?? 'On-Demand / Flexible',
                ),
                if (detail.scheduledTime != null) ...[
                  const Divider(height: 20, color: Color(0xFFE2E8F0)),
                  _buildInfoRow(
                    icon: Icons.access_time_filled_rounded,
                    title: 'Preferred Time Window',
                    value: detail.scheduledTime!,
                  ),
                ],
                const Divider(height: 20, color: Color(0xFFE2E8F0)),
                _buildInfoRow(
                  icon: Icons.payments_rounded,
                  title: 'Estimated Price',
                  value: detail.estimatedPrice != null
                      ? '₹ ${detail.estimatedPrice!.toStringAsFixed(0)}'
                      : '₹ ${detail.baseMarketPrice.toStringAsFixed(0)}',
                  valueColor: isInspection ? const Color(0xFF7C3AED) : const Color(0xFF059669),
                ),
                if (detail.estimatedDurationMinutes != null) ...[
                  const Divider(height: 20, color: Color(0xFFE2E8F0)),
                  _buildInfoRow(
                    icon: Icons.timer_rounded,
                    title: 'Expected Duration',
                    value: '${detail.estimatedDurationMinutes} minutes',
                  ),
                ],
              ],
            ),
          ),

          // Section 2: Problem Description (if present)
          if (detail.problemDescription != null &&
              detail.problemDescription!.isNotEmpty) ...[
            const SizedBox(height: 20),
            const Text(
              'Problem Description',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFBEB),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFFDE68A)),
              ),
              child: Text(
                detail.problemDescription!,
                style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF92400E),
                  height: 1.4,
                ),
              ),
            ),
          ],

          // Section 3: Apply for Job Action Section
          const SizedBox(height: 20),
          _buildApplySection(detail),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  bool _isApplying = false;
  bool _hasApplied = false;

  Future<void> _handleApply(MarketplaceBookingDetail detail) async {
    final TextEditingController coverLetterController = TextEditingController();

    final shouldSubmit = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: const Text(
          'Apply for Job',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Express interest in ${detail.serviceName} (${detail.bookingNumber}).',
              style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: coverLetterController,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Optional message to customer (e.g., experience, availability)...',
                hintStyle: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Submit Application'),
          ),
        ],
      ),
    );

    if (shouldSubmit != true) return;

    setState(() {
      _isApplying = true;
    });

    try {
      final appRes = await JobApplicationService.instance.applyForJob(
        bookingId: detail.id,
        coverLetter: coverLetterController.text,
      );

      if (!mounted) return;

      setState(() {
        _isApplying = false;
        _hasApplied = true;
        _applicationId = appRes.id;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Application submitted successfully!'),
          backgroundColor: Color(0xFF059669),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isApplying = false;
      });

      String errorMsg = e.toString();
      if (errorMsg.contains('PROFILE_INCOMPLETE') || errorMsg.contains('incomplete')) {
        errorMsg = 'Please complete your worker profile before applying for jobs.';
      } else if (errorMsg.contains('WORKER_NOT_AVAILABLE') || errorMsg.contains('AVAILABLE')) {
        errorMsg = 'Your status must be set to AVAILABLE to apply for jobs.';
      } else if (errorMsg.contains('OUTSIDE_SERVICE_RADIUS')) {
        errorMsg = 'This job is outside your designated service radius.';
      } else if (errorMsg.contains('DUPLICATE_APPLICATION')) {
        errorMsg = 'You have already submitted an application for this booking.';
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(errorMsg),
          backgroundColor: const Color(0xFFEF4444),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  Widget _buildApplySection(MarketplaceBookingDetail detail) {
    if (_hasApplied) {
      return Column(
        children: [
          Container(
            width: double.infinity,
            height: 48,
            decoration: BoxDecoration(
              color: const Color(0xFFECFDF5),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFA7F3D0)),
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.check_circle_rounded, color: Color(0xFF059669), size: 20),
                SizedBox(width: 8),
                Text(
                  'Application Submitted',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF047857),
                  ),
                ),
              ],
            ),
          ),
          if (_applicationId != null) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => QuotationFormScreen(
                        bookingId: detail.id,
                        applicationId: _applicationId!,
                        bookingNumber: detail.bookingNumber,
                        serviceName: detail.serviceName,
                      ),
                    ),
                  );
                },
                icon: const Icon(Icons.request_quote_rounded, size: 20),
                label: const Text(
                  'Manage / Send Quotation',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 0,
                ),
              ),
            ),
          ],
        ],
      );
    }

    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton(
        onPressed: _isApplying ? null : () => _handleApply(detail),
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF2563EB),
          foregroundColor: Colors.white,
          disabledBackgroundColor: const Color(0xFF93C5FD),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          elevation: 0,
        ),
        child: _isApplying
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : const Text(
                'Apply for Job',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
      ),
    );
  }

  Widget _buildInfoRow({
    required IconData icon,
    required String title,
    required String value,
    String? subvalue,
    Color valueColor = const Color(0xFF0F172A),
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Icon(icon, size: 18, color: const Color(0xFF64748B)),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF64748B),
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: valueColor,
                ),
              ),
              if (subvalue != null) ...[
                const SizedBox(height: 2),
                Text(
                  subvalue,
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF94A3B8),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}
