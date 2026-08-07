import 'dart:async';
import 'package:flutter/material.dart';
import '../../../app/theme/app_colors.dart';
import '../../../models/booking_model.dart';
import '../../../models/review_model.dart';
import '../../../services/api_service.dart';
import '../../../services/booking_service.dart';
import '../../../services/review_service.dart';
import '../../../services/razorpay_service.dart';
import '../../../widgets/booking_lifecycle_stepper.dart';
import '../../../widgets/booking_timeline_widget.dart';
import '../../../widgets/review_dialog.dart';
import '../../../widgets/review_display_card.dart';
import '../../../widgets/booking_communication_section.dart';
import '../../../widgets/live_tracking_map_widget.dart';
import '../../../services/socket_service.dart';
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
  final RazorpayService _razorpayService = RazorpayService();

  BookingModel? _booking;
  ReviewModel? _existingReview;
  bool _isLoading = true;
  String? _errorMessage;
  bool _isConfirming = false;
  bool _isProcessingPayment = false;
  final SocketService _socketService = SocketService();

  // Tracking data
  double? _workerLat;
  double? _workerLng;
  int? _etaMinutes;
  double? _distanceMeters;
  String? _lastUpdated;
  Timer? _autoRefreshTimer;

  @override
  void initState() {
    super.initState();
    _booking = widget.booking;

    _razorpayService.init(
      onSuccess: _onRazorpaySuccess,
      onFailure: _onRazorpayFailure,
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_booking == null) {
        _extractArgsAndFetch();
      } else {
        setState(() => _isLoading = false);
        _setupTracking();
        _fetchReviewIfCompleted(_booking!.id);
      }
    });

    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      if (!mounted) return;
      if (_booking != null) {
        _fetchBookingById(_booking!.id, isSilentRefresh: true);
      } else if (widget.bookingId != null) {
        _fetchBookingById(widget.bookingId!, isSilentRefresh: true);
      }
    });
  }

  Future<void> _onRazorpaySuccess() async {
    if (!mounted || _booking == null) return;
    setState(() {
      _isProcessingPayment = false;
    });

    // Refresh booking details to get payment_status: PAID
    await _fetchBookingById(_booking!.id, isSilentRefresh: true);
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Payment successful! Proceeding to service completion & review...'),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );

    _handleConfirmCompletion();
  }

  void _onRazorpayFailure(String message) {
    if (!mounted) return;
    setState(() {
      _isProcessingPayment = false;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Payment cancelled or failed: $message'),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  Future<void> _handlePaymentAndCompletion() async {
    if (_booking == null || _isProcessingPayment || _isConfirming) return;

    final double amount = _booking!.finalPrice ?? _booking!.estimatedPrice ?? 0.0;

    if (amount <= 0 || _booking!.isPaid) {
      _handleConfirmCompletion();
      return;
    }

    setState(() => _isProcessingPayment = true);

    try {
      await _razorpayService.openServicePayment(
        bookingId: _booking!.id,
        amountRupees: amount,
        description: 'Payment for ${_booking!.serviceSnapshot.name} (${_booking!.bookingNumber})',
        customerName: _booking!.addressSnapshot.fullName,
        customerPhone: _booking!.addressSnapshot.phone,
        customerEmail: 'customer@ally.com',
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isProcessingPayment = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not open payment window: ${e.toString()}'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  void _setupTracking() {
    if (_booking == null) return;
    _socketService.joinBookingTracking(_booking!.id);
    _socketService.onBookingStatusUpdated(_onBookingStatusUpdated);
    _socketService.onWorkerLocationUpdated(_onWorkerLocationUpdated);
  }

  void _onWorkerLocationUpdated(dynamic data) {
    if (data is Map && data['booking_id'] == _booking?.id) {
      if (!mounted) return;
      setState(() {
        _workerLat = (data['lat'] as num?)?.toDouble();
        _workerLng = (data['lng'] as num?)?.toDouble();
        _distanceMeters = (data['distance'] as num?)?.toDouble();
        _etaMinutes = (data['eta'] as num?)?.toInt();
        
        if (data['timestamp'] != null) {
          final dt = DateTime.tryParse(data['timestamp']);
          if (dt != null) {
            _lastUpdated = '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
          }
        }
      });
    }
  }

  void _onBookingStatusUpdated(dynamic data) {
    if (data is Map && data['booking_id'] == _booking?.id) {
      // Re-fetch booking from backend to get fresh timeline and status
      _fetchBookingById(_booking!.id, isSilentRefresh: true);
    }
  }

  @override
  void dispose() {
    _razorpayService.dispose();
    _autoRefreshTimer?.cancel();
    if (_booking != null) {
      _socketService.leaveBookingTracking(_booking!.id);
      _socketService.offBookingStatusUpdated(_onBookingStatusUpdated);
      _socketService.offWorkerLocationUpdated(_onWorkerLocationUpdated);
    }
    super.dispose();
  }

  void _extractArgsAndFetch() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic>) {
      if (args['booking'] is BookingModel) {
        final b = args['booking'] as BookingModel;
        setState(() {
          _booking = b;
          _isLoading = false;
        });
        _setupTracking();
        _fetchReviewIfCompleted(b.id);
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
      _setupTracking();
      _fetchReviewIfCompleted(args.id);
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

  Future<void> _fetchReviewIfCompleted(String bookingId) async {
    if (_booking == null) return;
    if (_booking!.isCustomerConfirmed || _booking!.status == 'completed') {
      final rev = await ReviewService().getReviewByBooking(bookingId);
      if (mounted && rev != null) {
        setState(() => _existingReview = rev);
      }
    }
  }

  Future<void> _fetchBookingById(String id, {bool isSilentRefresh = false}) async {
    if (!isSilentRefresh) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final b = await _bookingService.getBookingById(id);
      ReviewModel? rev;
      if (b.isCustomerConfirmed || b.status == 'completed') {
        rev = await ReviewService().getReviewByBooking(b.id);
      }
      if (!mounted) return;
      
      final bool isFirstLoad = _booking == null;
      setState(() {
        _booking = b;
        _existingReview = rev;
        _isLoading = false;
      });
      
      if (isFirstLoad) {
        _setupTracking();
      }
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

  Future<void> _handleConfirmCompletion() async {
    if (_booking == null || _isConfirming) return;

    // Strict Payment Gate: If work is completed and unpaid, trigger payment modal first
    final double payableAmount = _booking!.finalPrice ?? _booking!.estimatedPrice ?? 0.0;
    if (_booking!.isWorkCompleted && !_booking!.isPaid && payableAmount > 0) {
      await _handlePaymentAndCompletion();
      return;
    }

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Confirm Service Completion', style: TextStyle(fontWeight: FontWeight.w800)),
        content: Text(
          _booking!.isPaid
              ? 'Payment of ₹${payableAmount.toStringAsFixed(0)} verified! Are you satisfied with the completed work? Confirming will mark the service as completed.'
              : 'Are you satisfied with the completed work? Confirming will mark the service as officially accepted.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0D9488),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: const Text('Confirm & Accept', style: TextStyle(fontWeight: FontWeight.w800)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    setState(() => _isConfirming = true);

    try {
      final updated = await _bookingService.confirmCompletion(_booking!.id);
      if (!mounted) return;

      setState(() {
        _booking = updated;
        _isConfirming = false;
      });

      _socketService.emitBookingStatusUpdate(updated.id, updated.status);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Service completion accepted successfully!'),
          backgroundColor: Colors.green,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );

      _promptReviewDialog();
    } catch (e) {
      if (!mounted) return;
      setState(() => _isConfirming = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to confirm completion: ${e.toString()}'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  void _promptReviewDialog() {
    if (_booking == null) return;
    ReviewDialog.show(
      context,
      bookingId: _booking!.id,
      onSubmit: (overall, punctuality, quality, professionalism, communication, title, comment, recommend) async {
        try {
          final review = await ReviewService().createReview(
            bookingId: _booking!.id,
            overallRating: overall,
            punctualityRating: punctuality,
            qualityRating: quality,
            professionalismRating: professionalism,
            communicationRating: communication,
            title: title,
            comment: comment,
            wouldRecommend: recommend,
          );
          if (!mounted) return;
          setState(() {
            _existingReview = review;
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text('Thank you for rating your service experience!'),
              backgroundColor: Colors.green,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          );
        } catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to submit review: ${e.toString()}'),
              backgroundColor: Colors.red,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          );
        }
      },
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return const Color(0xFFD97706);
      case 'assigned':
      case 'accepted':
        return const Color(0xFF2563EB);
      case 'worker_en_route':
        return const Color(0xFF6366F1);
      case 'arrived':
        return const Color(0xFF8B5CF6);
      case 'in_progress':
        return const Color(0xFF4F46E5);
      case 'work_completed':
        return const Color(0xFF0D9488);
      case 'customer_confirmed':
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
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Booking Details',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF64748B)),
            onPressed: () {
              if (_booking != null) _fetchBookingById(_booking!.id);
            },
          ),
        ],
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

                            const SizedBox(height: 16),

                            // ── Booking Lifecycle Stepper ───────────────────
                            BookingLifecycleStepper(booking: _booking!),

                            const SizedBox(height: 20),

                            // ── Work Completion Review Card (If Work Completed) ──
                            if (_booking!.isWorkCompleted) ...[
                              _buildCompletionReviewCard(),
                              const SizedBox(height: 20),
                            ],

                            // ── Submitted Review Display (If Review Exists) ────
                            if (_existingReview != null) ...[
                              ReviewDisplayCard(
                                review: _existingReview!,
                                titleText: 'Your Submitted Rating & Review',
                              ),
                              const SizedBox(height: 20),
                            ] else if (_booking!.isCustomerConfirmed || _booking!.status == 'completed') ...[
                              _buildConfirmedBanner(),
                              const SizedBox(height: 20),
                            ],

                            // ── Communication Section ──────────────────────────
                            BookingCommunicationSection(
                              booking: _booking!,
                              currentUserId: _booking!.customerId,
                            ),
                            const SizedBox(height: 20),

                            // ── Live Worker Location ───────────────────────────
                            if (_booking!.isWorkerEnRoute || _booking!.isInProgress || _booking!.isArrived) ...[
                              LiveTrackingMapWidget(
                                customerLat: _booking!.addressSnapshot.latitude ?? 0.0,
                                customerLng: _booking!.addressSnapshot.longitude ?? 0.0,
                                workerLat: _workerLat,
                                workerLng: _workerLng,
                                distanceMeters: _distanceMeters,
                                etaMinutes: _etaMinutes,
                                lastUpdated: _lastUpdated,
                              ),
                              const SizedBox(height: 20),
                            ],

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

                            // ── Payment Status Card ────────────────────────
                            _buildPaymentStatusCard(),

                            const SizedBox(height: 20),

                            // ── Worker Quotations Button Card ───────────────
                            _buildViewQuotationsCard(),

                            const SizedBox(height: 20),

                            // ── Timeline Audit Log ──────────────────────────
                            if (_booking!.timeline.isNotEmpty) ...[
                              BookingTimelineWidget(events: _booking!.timeline),
                              const SizedBox(height: 20),
                            ],

                            const SizedBox(height: 80),
                          ],
                        ),
                      ),
      ),
      bottomNavigationBar: (_booking != null && _booking!.isWorkCompleted)
          ? Container(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
              decoration: const BoxDecoration(
                color: Colors.white,
                boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 12, offset: Offset(0, -4))],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: (!_booking!.isPaid && (_booking!.finalPrice ?? _booking!.estimatedPrice ?? 0.0) > 0)
                    ? ElevatedButton.icon(
                        onPressed: (_isProcessingPayment || _isConfirming) ? null : _handlePaymentAndCompletion,
                        icon: _isProcessingPayment
                            ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                            : const Icon(Icons.payment_rounded, size: 20),
                        label: Text(
                          _isProcessingPayment
                              ? 'Opening Razorpay...'
                              : 'Pay ₹${(_booking!.finalPrice ?? _booking!.estimatedPrice ?? 0.0).toStringAsFixed(0)} & Rate Worker',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          elevation: 0,
                        ),
                      )
                    : ElevatedButton.icon(
                        onPressed: _isConfirming ? null : _handleConfirmCompletion,
                        icon: _isConfirming
                            ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                            : const Icon(Icons.verified_rounded, size: 20),
                        label: Text(
                          _isConfirming ? 'Confirming...' : 'Confirm Service Completion',
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0D9488),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          elevation: 0,
                        ),
                      ),
              ),
            )
          : (_booking != null && (_booking!.isCustomerConfirmed || _booking!.status == 'completed'))
              ? Container(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 12, offset: Offset(0, -4))],
                  ),
                  child: _existingReview != null
                      ? Container(
                          height: 52,
                          alignment: Alignment.center,
                          decoration: BoxDecoration(
                            color: const Color(0xFFF1F5F9),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.check_circle_rounded, color: Color(0xFF10B981), size: 20),
                              SizedBox(width: 8),
                              Text(
                                'Review Submitted (Thank You!)',
                                style: TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF334155), fontSize: 14),
                              ),
                            ],
                          ),
                        )
                      : SizedBox(
                          width: double.infinity,
                          height: 52,
                          child: OutlinedButton.icon(
                            onPressed: _promptReviewDialog,
                            icon: const Icon(Icons.star_rounded, size: 20, color: Colors.amber),
                            label: const Text(
                              'Rate & Review Worker',
                              style: TextStyle(fontWeight: FontWeight.w800, fontSize: 15, color: Color(0xFF0F172A)),
                            ),
                            style: OutlinedButton.styleFrom(
                              side: const BorderSide(color: Color(0xFFCBD5E1), width: 1.5),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ),
                )
              : null,
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
              style: const TextStyle(fontSize: 14),
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
              _booking!.isCustomerConfirmed || _booking!.status == 'completed'
                  ? Icons.check_circle_rounded
                  : _booking!.isCancelled
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
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: statusColor.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        _booking!.status.toUpperCase().replaceAll('_', ' '),
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: statusColor),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  _booking!.bookingType == 'inspection_request' ? 'Site Inspection Request' : 'Direct Service Booking',
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionReviewCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF0FDF4),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF86EFAC), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF16A34A).withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.assignment_turned_in_rounded, color: Color(0xFF15803D), size: 22),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Work Marked Completed!',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF166534)),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Worker finished execution. Please review and confirm.',
                      style: TextStyle(fontSize: 12, color: Color(0xFF15803D)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(color: Color(0xFFBBF7D0), height: 1),
          const SizedBox(height: 12),

          if (_booking!.completionNotes != null && _booking!.completionNotes!.isNotEmpty) ...[
            const Text(
              'Worker Completion Notes:',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF166534)),
            ),
            const SizedBox(height: 4),
            Text(
              _booking!.completionNotes!,
              style: const TextStyle(fontSize: 13, color: Color(0xFF14532D)),
            ),
            const SizedBox(height: 10),
          ],

          if (_booking!.workSummary != null && _booking!.workSummary!.isNotEmpty) ...[
            const Text(
              'Work Summary:',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF166534)),
            ),
            const SizedBox(height: 4),
            Text(
              _booking!.workSummary!,
              style: const TextStyle(fontSize: 13, color: Color(0xFF14532D)),
            ),
            const SizedBox(height: 10),
          ],

          if (_booking!.afterPhotos.isNotEmpty) ...[
            const Text(
              'Completion Photos:',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF166534)),
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 80,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _booking!.afterPhotos.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (_, i) => ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.network(
                    _booking!.afterPhotos[i],
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      width: 80,
                      height: 80,
                      color: Colors.grey.shade200,
                      child: const Icon(Icons.broken_image_outlined),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 14),
          ],
          Text(
            _booking!.isPaid
                ? 'Tap the button below to confirm service completion and submit worker review.'
                : 'Please complete payment via Razorpay to confirm service completion and rate the worker.',
            style: const TextStyle(fontSize: 12, color: Color(0xFF15803D), fontStyle: FontStyle.italic),
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmedBanner() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF0FDF4),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF86EFAC)),
      ),
      child: Row(
        children: [
          const Icon(Icons.verified_rounded, color: Color(0xFF16A34A), size: 24),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Service Officially Confirmed',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF166534)),
                ),
                SizedBox(height: 2),
                Text(
                  'You have verified and accepted the completed work.',
                  style: TextStyle(fontSize: 12, color: Color(0xFF15803D)),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.star_rounded, color: Colors.amber, size: 28),
            onPressed: _promptReviewDialog,
            tooltip: 'Rate & Review',
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
          const Text('Service Information', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
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
                    Text(svc.name, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                    const SizedBox(height: 2),
                    Text('Category: ${svc.categorySlug}', style: const TextStyle(fontSize: 12)),
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
              Text('Base Market Price', style: const TextStyle(fontSize: 13)),
              Text('₹${svc.baseMarketPrice.toStringAsFixed(0)}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Estimated Duration', style: const TextStyle(fontSize: 13)),
              Text('${svc.estimatedDurationMinutes} mins', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
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
          const Text('Service Address', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(Icons.location_on_rounded, color: AppColors.primary, size: 22),
              const SizedBox(width: 10),
              Text(addr.label, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
            ],
          ),
          const SizedBox(height: 8),
          Text(addr.fullName, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
          Text(addr.phone, style: const TextStyle(fontSize: 12)),
          const SizedBox(height: 6),
          Text(
            '${addr.addressLine1}${addr.addressLine2 != null ? ', ${addr.addressLine2}' : ''}\n${addr.landmark != null ? 'Landmark: ${addr.landmark}\n' : ''}${addr.city}, ${addr.state} - ${addr.postalCode}',
            style: const TextStyle(fontSize: 12, height: 1.4),
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
          const Text('Schedule Preferences', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(Icons.calendar_month_rounded, color: AppColors.primary, size: 20),
              const SizedBox(width: 10),
              Text(
                'Date: ${_booking!.scheduledDate ?? 'ASAP / On-demand'}',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
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
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
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
          const Text('Customer Notes', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          Text(
            _booking!.customerNotes!,
            style: const TextStyle(fontSize: 13, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceSummaryCard() {
    final effectivePrice = _booking!.finalPrice ?? _booking!.estimatedPrice;
    final isAgreed = _booking!.finalPrice != null;

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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isAgreed ? 'Agreed Quotation Price' : 'Estimated Price',
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
              ),
              Text(
                '₹${effectivePrice?.toStringAsFixed(0) ?? '0'}',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: AppColors.primary),
              ),
            ],
          ),
          if (isAgreed) ...[
            const SizedBox(height: 6),
            const Row(
              children: [
                Icon(Icons.check_circle_rounded, size: 14, color: Color(0xFF10B981)),
                SizedBox(width: 4),
                Text(
                  'Accepted Worker Quotation',
                  style: TextStyle(fontSize: 11, color: Color(0xFF10B981), fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPaymentStatusCard() {
    final isPaid = _booking!.isPaid;
    final effectivePrice = _booking!.finalPrice ?? _booking!.estimatedPrice ?? 0.0;
    final paymentColor = isPaid ? const Color(0xFF16A34A) : const Color(0xFFD97706);

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: isPaid ? const Color(0xFFF0FDF4) : const Color(0xFFFFFBEB),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isPaid ? const Color(0xFF86EFAC) : const Color(0xFFFCD34D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    isPaid ? Icons.payment_rounded : Icons.pending_actions_rounded,
                    color: paymentColor,
                    size: 22,
                  ),
                  const SizedBox(width: 10),
                  const Text(
                    'Payment Status',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: paymentColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  isPaid ? 'PAID' : 'PENDING PAYMENT',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: paymentColor),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isPaid ? 'Amount Paid' : 'Amount Payable',
                style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
              ),
              Text(
                '₹${effectivePrice.toStringAsFixed(0)}',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: paymentColor),
              ),
            ],
          ),
          if (isPaid && _booking!.paymentId != null && _booking!.paymentId!.isNotEmpty) ...[
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Razorpay Ref ID', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                Text(
                  _booking!.paymentId!,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, fontFamily: 'monospace'),
                ),
              ],
            ),
          ],
          if (!isPaid && _booking!.isWorkCompleted && effectivePrice > 0) ...[
            const SizedBox(height: 14),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isProcessingPayment ? null : _handlePaymentAndCompletion,
                icon: _isProcessingPayment
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.payment_rounded, size: 18),
                label: Text(
                  _isProcessingPayment ? 'Opening Checkout...' : 'Pay ₹${effectivePrice.toStringAsFixed(0)} via Razorpay',
                  style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 11),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
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
