// File: lib/worker/work/worker_booking_detail_screen.dart

import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../models/booking_model.dart';
import '../../models/review_model.dart';
import '../../services/booking_service.dart';
import '../../services/review_service.dart';
import '../../widgets/booking_lifecycle_stepper.dart';
import '../../widgets/booking_timeline_widget.dart';
import 'dart:async';
import 'package:geolocator/geolocator.dart';
import '../../widgets/review_display_card.dart';
import '../../widgets/booking_communication_section.dart';
import '../../services/socket_service.dart';
import 'worker_complete_job_dialog.dart';

class WorkerBookingDetailScreen extends StatefulWidget {
  final BookingModel booking;

  const WorkerBookingDetailScreen({super.key, required this.booking});

  @override
  State<WorkerBookingDetailScreen> createState() =>
      _WorkerBookingDetailScreenState();
}

class _WorkerBookingDetailScreenState
    extends State<WorkerBookingDetailScreen> {
  late BookingModel _booking;
  ReviewModel? _customerReview;
  bool _isActionLoading = false;
  final SocketService _socketService = SocketService();

  StreamSubscription<Position>? _positionStream;
  bool _isLocationSharing = false;
  double? _distanceMeters;
  int? _etaMinutes;

  @override
  void initState() {
    super.initState();
    _booking = widget.booking;
    _setupTracking();
    _fetchReviewIfCompleted();
  }

  void _setupTracking() {
    _socketService.joinBookingTracking(_booking.id);
    _socketService.onBookingStatusUpdated(_onBookingStatusUpdated);
    _checkLocationSharing();
  }

  void _checkLocationSharing() {
    final shouldShare = _booking.isWorkerEnRoute || _booking.isArrived || _booking.isInProgress;
    if (shouldShare && !_isLocationSharing) {
      _startLocationSharing();
    } else if (!shouldShare && _isLocationSharing) {
      _stopLocationSharing();
    }
  }

  Future<void> _startLocationSharing() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }
    if (permission == LocationPermission.deniedForever) return;

    setState(() => _isLocationSharing = true);

    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    ).listen((Position position) {
      if (!mounted || _booking.addressSnapshot.latitude == null || _booking.addressSnapshot.longitude == null) return;

      final customerLat = _booking.addressSnapshot.latitude!;
      final customerLng = _booking.addressSnapshot.longitude!;
      
      final distance = Geolocator.distanceBetween(
        position.latitude, position.longitude, customerLat, customerLng
      );
      
      // Assume 30 km/h average speed (8.33 m/s)
      final eta = (distance / 8.33 / 60).round();

      setState(() {
        _distanceMeters = distance;
        _etaMinutes = eta;
      });

      _socketService.emitWorkerLocation(
        _booking.id,
        position.latitude,
        position.longitude,
        distance,
        eta,
      );
    });
  }

  void _stopLocationSharing() {
    _positionStream?.cancel();
    _positionStream = null;
    if (mounted) setState(() => _isLocationSharing = false);
  }

  void _onBookingStatusUpdated(dynamic data) async {
    if (data is Map && data['booking_id'] == _booking.id) {
      // Re-fetch to get latest status (e.g., customer confirmation)
      try {
        final updated = await BookingService.instance.getWorkerBooking(_booking.id);
        if (mounted) {
          setState(() {
            _booking = updated;
          });
          _checkLocationSharing();
          _fetchReviewIfCompleted();
        }
      } catch (e) {
        // Handle error silently or log
      }
    }
  }

  @override
  void dispose() {
    _stopLocationSharing();
    _socketService.leaveBookingTracking(_booking.id);
    _socketService.offBookingStatusUpdated(_onBookingStatusUpdated);
    super.dispose();
  }

  Future<void> _fetchReviewIfCompleted() async {
    if (_booking.isCustomerConfirmed || _booking.status == 'completed') {
      final rev = await ReviewService().getReviewByBooking(_booking.id);
      if (mounted && rev != null) {
        setState(() => _customerReview = rev);
      }
    }
  }

  Future<void> _performAction(Future<BookingModel> Function() action) async {
    setState(() => _isActionLoading = true);
    try {
      final updated = await action();
      if (!mounted) return;
      setState(() {
        _booking = updated;
        _isActionLoading = false;
      });
      _checkLocationSharing();
      _fetchReviewIfCompleted();
      _socketService.emitBookingStatusUpdate(updated.id, updated.status);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Status updated to ${updated.status.toUpperCase().replaceAll('_', ' ')}'),
          backgroundColor: Colors.green,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isActionLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_friendlyError(e.toString())),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  String _friendlyError(String raw) {
    if (raw.contains('INVALID_STATUS_TRANSITION')) return 'Invalid status transition.';
    if (raw.contains('BOOKING_TERMINATED')) return 'This booking is already closed.';
    if (raw.contains('BOOKING_ACCESS_DENIED')) return 'You are not the assigned worker.';
    if (raw.contains('BOOKING_NOT_FOUND')) return 'Booking not found.';
    return raw.length > 120 ? '${raw.substring(0, 120)}...' : raw;
  }

  void _handleStartTravel() {
    _performAction(() => BookingService.instance.startTravel(_booking.id));
  }

  void _handleArrived() {
    _performAction(() => BookingService.instance.markArrived(_booking.id));
  }

  void _handleStartWork() {
    _performAction(() => BookingService.instance.startWork(_booking.id));
  }

  void _handleCompleteWork() async {
    await WorkerCompleteJobDialog.show(
      context,
      onConfirm: (notes, summary) async {
        await _performAction(
          () => BookingService.instance.completeWork(
            _booking.id,
            notes: notes,
            summary: summary,
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final hasAction = _booking.isAssigned ||
        _booking.isWorkerEnRoute ||
        _booking.isArrived ||
        _booking.isInProgress;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) Navigator.of(context).pop(true);
      },
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          backgroundColor: AppColors.surface,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded, color: AppColors.textPrimary),
            onPressed: () => Navigator.of(context).pop(true),
          ),
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _booking.bookingNumber,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                ),
              ),
              Text(
                _booking.serviceSnapshot.name,
                style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh_rounded, color: Color(0xFF64748B)),
              onPressed: _fetchReviewIfCompleted,
            ),
          ],
        ),
        body: ListView(
          padding: EdgeInsets.fromLTRB(16, 16, 16, hasAction ? 100 : 24),
          children: [
            // ── Lifecycle Stepper ─────────────────────────────────
            BookingLifecycleStepper(booking: _booking),
            const SizedBox(height: 16),

            // ── Customer Rating & Review (if available) ───────────
            if (_customerReview != null) ...[
              ReviewDisplayCard(
                review: _customerReview!,
                titleText: 'Customer Rating & Review',
              ),
              const SizedBox(height: 16),
            ],

            // ── Customer & Address Card ────────────────────────────
            _buildCustomerAddressCard(),
            const SizedBox(height: 16),

            // ── Location Sharing Status ────────────────────────────
            if (_booking.isWorkerEnRoute || _booking.isArrived || _booking.isInProgress) ...[
              _buildLocationSharingCard(),
              const SizedBox(height: 16),
            ],

            // ── Communication Section ────────────────────────────
            BookingCommunicationSection(
              booking: _booking,
              currentUserId: _booking.workerId ?? '',
              isWorker: true,
            ),
            const SizedBox(height: 16),

            // ── Service & Price Card ──────────────────────────────
            _buildServiceCard(),
            const SizedBox(height: 16),

            // ── Completion Summary & Photos ───────────────────────
            if (_booking.isWorkCompleted ||
                _booking.isCustomerConfirmed) ...[
              _buildCompletionCard(),
              const SizedBox(height: 16),
            ],

            // ── Timeline Audit Log ─────────────────────────────────
            if (_booking.timeline.isNotEmpty) ...[
              BookingTimelineWidget(events: _booking.timeline),
              const SizedBox(height: 16),
            ],
          ],
        ),

        // ── Sticky Lifecycle Action Footer ────────────────────────
        bottomNavigationBar: hasAction
            ? _buildActionFooter()
            : _booking.isWorkCompleted
                ? _buildWaitingFooter()
                : _booking.isCustomerConfirmed
                    ? _buildCompletedFooter()
                    : null,
      ),
    );
  }

  Widget _buildCustomerAddressCard() {
    final addr = _booking.addressSnapshot;
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.person_rounded, color: Color(0xFF2563EB), size: 18),
                const SizedBox(width: 8),
                const Text(
                  'Customer & Location',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
                ),
              ],
            ),
            const Divider(height: 16),
            _infoRow(Icons.person_outline_rounded, addr.fullName),
            const SizedBox(height: 6),
            _infoRow(Icons.phone_outlined, addr.phone),
            const SizedBox(height: 6),
            _infoRow(Icons.location_on_outlined, addr.shortAddress),
            if (addr.landmark != null && addr.landmark!.isNotEmpty) ...[
              const SizedBox(height: 4),
              _infoRow(Icons.flag_outlined, 'Landmark: ${addr.landmark}'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLocationSharingCard() {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _isLocationSharing ? Icons.gps_fixed_rounded : Icons.gps_off_rounded,
                  color: _isLocationSharing ? Colors.green : const Color(0xFF94A3B8),
                  size: 18,
                ),
                const SizedBox(width: 8),
                Text(
                  'Location Sharing',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _isLocationSharing ? Colors.green.shade50 : const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _isLocationSharing ? 'Enabled' : 'Disabled',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: _isLocationSharing ? Colors.green.shade700 : const Color(0xFF64748B),
                    ),
                  ),
                ),
              ],
            ),
            if (_isLocationSharing) ...[
              const Divider(height: 24),
              if (_distanceMeters != null)
                _infoRow(Icons.route_outlined, 'Distance to Customer: ${(_distanceMeters! / 1000).toStringAsFixed(1)} km'),
              const SizedBox(height: 8),
              if (_etaMinutes != null)
                _infoRow(Icons.timer_outlined, 'Estimated Time of Arrival: $_etaMinutes min'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildServiceCard() {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.build_rounded, color: Color(0xFF2563EB), size: 18),
                const SizedBox(width: 8),
                const Text(
                  'Service Details',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
                ),
              ],
            ),
            const Divider(height: 16),
            _infoRow(Icons.home_repair_service_outlined, _booking.serviceSnapshot.name),
            const SizedBox(height: 6),
            _infoRow(
              Icons.attach_money_rounded,
              'Est. Price: ₹${(_booking.estimatedPrice ?? _booking.serviceSnapshot.baseMarketPrice).toStringAsFixed(0)}',
            ),
            const SizedBox(height: 6),
            _infoRow(
              Icons.timer_outlined,
              'Est. Duration: ${_booking.serviceSnapshot.estimatedDurationMinutes} min',
            ),
            if (_booking.customerNotes != null && _booking.customerNotes!.isNotEmpty) ...[
              const SizedBox(height: 6),
              _infoRow(Icons.notes_rounded, 'Customer Note: ${_booking.customerNotes}'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCompletionCard() {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.task_alt_rounded, color: Colors.green, size: 18),
                const SizedBox(width: 8),
                const Text(
                  'Completion Summary',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
                ),
              ],
            ),
            const Divider(height: 16),
            if (_booking.completionNotes != null) ...[
              _infoRow(Icons.notes_rounded, 'Notes: ${_booking.completionNotes}'),
              const SizedBox(height: 6),
            ],
            if (_booking.workSummary != null) ...[
              _infoRow(Icons.summarize_outlined, 'Summary: ${_booking.workSummary}'),
              const SizedBox(height: 8),
            ],
            if (_booking.afterPhotos.isNotEmpty) ...[
              const Text(
                'After Photos',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 80,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: _booking.afterPhotos.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 8),
                  itemBuilder: (_, i) => ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: Image.network(
                      _booking.afterPhotos[i],
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
            ],
          ],
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String text) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 15, color: const Color(0xFF64748B)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(fontSize: 13, color: Color(0xFF334155)),
          ),
        ),
      ],
    );
  }

  Widget _buildActionFooter() {
    String label;
    IconData icon;
    Color color;
    VoidCallback action;

    if (_booking.isAssigned) {
      label = 'Start Travel';
      icon = Icons.directions_car_rounded;
      color = const Color(0xFF2563EB);
      action = _handleStartTravel;
    } else if (_booking.isWorkerEnRoute) {
      label = 'Mark Arrived';
      icon = Icons.location_on_rounded;
      color = Colors.purple;
      action = _handleArrived;
    } else if (_booking.isArrived) {
      label = 'Start Work';
      icon = Icons.build_circle_rounded;
      color = Colors.amber.shade800;
      action = _handleStartWork;
    } else {
      label = 'Complete Work';
      icon = Icons.task_alt_rounded;
      color = Colors.teal;
      action = _handleCompleteWork;
    }

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 12, offset: Offset(0, -4))],
      ),
      child: SizedBox(
        width: double.infinity,
        height: 52,
        child: ElevatedButton.icon(
          onPressed: _isActionLoading ? null : action,
          icon: _isActionLoading
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : Icon(icon, size: 20),
          label: Text(
            _isActionLoading ? 'Updating...' : label,
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            elevation: 0,
          ),
        ),
      ),
    );
  }

  Widget _buildWaitingFooter() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 12, offset: Offset(0, -4))],
      ),
      child: Container(
        width: double.infinity,
        height: 52,
        decoration: BoxDecoration(
          color: Colors.teal.shade50,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: Colors.teal.shade200),
        ),
        alignment: Alignment.center,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.hourglass_top_rounded, color: Colors.teal.shade700, size: 18),
            const SizedBox(width: 8),
            Text(
              'Waiting for Customer Confirmation',
              style: TextStyle(
                fontWeight: FontWeight.w700,
                color: Colors.teal.shade700,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompletedFooter() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 12, offset: Offset(0, -4))],
      ),
      child: Container(
        width: double.infinity,
        height: 52,
        decoration: BoxDecoration(
          color: Colors.green.shade50,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: Colors.green.shade200),
        ),
        alignment: Alignment.center,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.verified_rounded, color: Colors.green.shade700, size: 18),
            const SizedBox(width: 8),
            Text(
              _booking.isCancelled ? 'Booking Cancelled' : 'Booking Completed',
              style: TextStyle(
                fontWeight: FontWeight.w700,
                color: _booking.isCancelled ? Colors.red.shade700 : Colors.green.shade700,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
