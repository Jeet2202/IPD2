// File: lib/worker/work/worker_work_screen.dart
//
// Worker Work Module — displays all bookings assigned to the worker,
// segmented by lifecycle status, with lifecycle action capabilities.

import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../models/booking_model.dart';
import '../../services/booking_service.dart';
import '../../l10n/app_translations.dart';
import '../../widgets/language_selector_widget.dart';
import '../widgets/worker_bottom_navigation_bar.dart';
import 'worker_booking_detail_screen.dart';

class WorkerWorkScreen extends StatefulWidget {
  const WorkerWorkScreen({super.key});

  @override
  State<WorkerWorkScreen> createState() => _WorkerWorkScreenState();
}

class _WorkerWorkScreenState extends State<WorkerWorkScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  bool _isLoading = true;
  String? _error;
  List<BookingModel> _allBookings = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadBookings();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadBookings() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final bookings = await BookingService.instance.fetchWorkerBookings(pageSize: 50);
      if (!mounted) return;
      setState(() {
        _allBookings = bookings;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  List<BookingModel> get _activeBookings => _allBookings
      .where((b) => !b.isCustomerConfirmed && !b.isCancelled)
      .toList();

  List<BookingModel> get _waitingBookings =>
      _allBookings.where((b) => b.isWorkCompleted).toList();

  List<BookingModel> get _completedBookings =>
      _allBookings.where((b) => b.isCustomerConfirmed || b.isCancelled).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(
        title: Row(
          children: [
            const Icon(Icons.work_rounded, color: AppColors.primary, size: 22),
            const SizedBox(width: 8),
            Text(
              'work'.tr(context),
              style: const TextStyle(
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
        backgroundColor: AppColors.surface,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: AppColors.primary),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _loadBookings,
            tooltip: 'Refresh',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textHint,
          indicatorColor: AppColors.primary,
          labelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          tabs: [
            Tab(text: '${'active_bookings'.tr(context)} (${_activeBookings.length})'),
            Tab(text: '${'pending'.tr(context)} (${_waitingBookings.length})'),
            Tab(text: '${'completed'.tr(context)} (${_completedBookings.length})'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.cloud_off_rounded, size: 48, color: AppColors.error),
                      const SizedBox(height: 12),
                      Text(
                        _error!,
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Pull to refresh or try again.',
                        style: TextStyle(fontSize: 12),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _loadBookings,
                        icon: const Icon(Icons.refresh_rounded),
                        label: const Text('Retry'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  color: AppColors.primary,
                  onRefresh: _loadBookings,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildList(_activeBookings, 'No active jobs assigned yet.'),
                      _buildList(_waitingBookings, 'No jobs waiting for confirmation.'),
                      _buildList(_completedBookings, 'No completed jobs yet.'),
                    ],
                  ),
                ),
      bottomNavigationBar: const WorkerBottomNavigationBar(currentIndex: 2),
    );
  }

  Widget _buildList(List<BookingModel> bookings, String emptyMessage) {
    if (bookings.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.20),
          Center(
            child: Column(
              children: [
                const Icon(Icons.work_off_outlined, size: 56, color: Color(0xFFCBD5E1)),
                const SizedBox(height: 16),
                Text(
                  emptyMessage,
                  style: const TextStyle(fontSize: 14, color: Color(0xFF94A3B8)),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ],
      );
    }

    return ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      itemCount: bookings.length,
      itemBuilder: (context, index) {
        return _WorkerBookingCard(
          booking: bookings[index],
          onTap: () async {
            final updated = await Navigator.push<bool>(
              context,
              MaterialPageRoute(
                builder: (_) => WorkerBookingDetailScreen(booking: bookings[index]),
              ),
            );
            if (updated == true) _loadBookings();
          },
        );
      },
    );
  }
}

class _WorkerBookingCard extends StatelessWidget {
  final BookingModel booking;
  final VoidCallback onTap;

  const _WorkerBookingCard({required this.booking, required this.onTap});

  Color get _statusColor {
    if (booking.isCancelled) return Colors.red;
    if (booking.isCustomerConfirmed) return Colors.green;
    if (booking.isWorkCompleted) return Colors.teal;
    if (booking.isInProgress) return Colors.amber.shade800;
    if (booking.isArrived) return Colors.purple;
    if (booking.isWorkerEnRoute) return Colors.indigo;
    if (booking.isAssigned) return Colors.blue;
    return Colors.grey;
  }

  String get _statusLabel {
    if (booking.isCancelled) return 'CANCELLED';
    if (booking.isCustomerConfirmed) return 'COMPLETED';
    if (booking.isWorkCompleted) return 'AWAITING CONFIRMATION';
    if (booking.isInProgress) return 'IN PROGRESS';
    if (booking.isArrived) return 'ARRIVED';
    if (booking.isWorkerEnRoute) return 'EN ROUTE';
    if (booking.isAssigned) return 'ASSIGNED';
    return booking.status.toUpperCase();
  }

  String get _nextAction {
    if (booking.isAssigned) return 'Tap to Start Travel →';
    if (booking.isWorkerEnRoute) return 'Tap to Mark Arrived →';
    if (booking.isArrived) return 'Tap to Start Work →';
    if (booking.isInProgress) return 'Tap to Complete Work →';
    if (booking.isWorkCompleted) return 'Waiting for customer confirmation';
    if (booking.isCustomerConfirmed) return 'View customer rating & review →';
    return '';
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            // Status Header Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: _statusColor.withValues(alpha: 0.08),
                borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    booking.bookingNumber,
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                      fontSize: 13,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                    decoration: BoxDecoration(
                      color: _statusColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      _statusLabel,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: _statusColor,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Card Body
            Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    booking.serviceSnapshot.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 15,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, size: 14, color: Color(0xFF64748B)),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          booking.addressSnapshot.shortAddress,
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  if (booking.scheduledDate != null) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.calendar_today_outlined, size: 14, color: Color(0xFF64748B)),
                        const SizedBox(width: 4),
                        Text(
                          '${booking.scheduledDate}${booking.scheduledTime != null ? '  ${booking.scheduledTime}' : ''}',
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (booking.estimatedPrice != null)
                        Text(
                          '₹${booking.estimatedPrice!.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontWeight: FontWeight.w800,
                            fontSize: 15,
                            color: Color(0xFF2563EB),
                          ),
                        ),
                      if (_nextAction.isNotEmpty)
                        Expanded(
                          child: Text(
                            _nextAction,
                            textAlign: TextAlign.end,
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: booking.isWorkCompleted ? Colors.teal : const Color(0xFF2563EB),
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
