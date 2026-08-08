// File: lib/worker/jobs/incoming_jobs/incoming_jobs_screen.dart

import 'package:flutter/material.dart';
import '../../../models/marketplace_booking_model.dart';
import '../../../services/api_service.dart';
import '../../../services/marketplace_service.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';
import '../../widgets/worker_bottom_navigation_bar.dart';

class WorkerIncomingJobsScreen extends StatefulWidget {
  const WorkerIncomingJobsScreen({super.key});

  @override
  State<WorkerIncomingJobsScreen> createState() =>
      _WorkerIncomingJobsScreenState();
}

class _WorkerIncomingJobsScreenState extends State<WorkerIncomingJobsScreen> {
  String _selectedFilter = 'All';
  String _searchQuery = '';
  final List<String> _filters = ['All', 'Nearby', 'High Paying', 'Inspection', 'Scheduled'];

  bool _isLoading = false;
  String? _errorMessage;
  List<MarketplaceBookingItem> _jobs = [];

  @override
  void initState() {
    super.initState();
    _fetchJobs();
  }

  String? _sortByParam() {
    switch (_selectedFilter) {
      case 'Nearby':
        return 'recommended'; // Recommendation engine sorts by distance
      case 'High Paying':
        return 'price_desc';
      default:
        return 'newest';
    }
  }

  String? _bookingTypeParam() {
    if (_selectedFilter == 'Inspection') return 'inspection_request';
    return null;
  }

  Future<void> _fetchJobs() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      final result = await MarketplaceService.instance.fetchMarketplaceBookings(
        query: _searchQuery.isNotEmpty ? _searchQuery : null,
        sortBy: _sortByParam() ?? 'newest',
        bookingType: _bookingTypeParam(),
        pageSize: 30,
      );
      if (!mounted) return;
      setState(() {
        _jobs = result.items;
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
        _errorMessage = 'failed_to_load_jobs'.tr(context);
        _isLoading = false;
      });
    }
  }

  Future<void> _applyForJob(MarketplaceBookingItem job) async {
    try {
      await ApiService.instance.post(
        '/worker/marketplace/${job.id}/apply',
        {},
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${'applied_for_prefix'.tr(context)}${job.serviceName}${'applied_successfully_suffix'.tr(context)}'),
          backgroundColor: const Color(0xFF10B981),
          behavior: SnackBarBehavior.floating,
        ),
      );
      _fetchJobs(); // Refresh to update hasApplied
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.message),
          backgroundColor: const Color(0xFFEF4444),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  Color _badgeColor(MarketplaceBookingItem job) {
    if (job.isInspection) return const Color(0xFF8B5CF6);
    final price = job.estimatedPrice ?? 0;
    if (price > 1000) return const Color(0xFF10B981);
    final dist = job.distanceKm ?? 99;
    if (dist < 3) return const Color(0xFF2563EB);
    return const Color(0xFF64748B);
  }

  String _badgeLabel(MarketplaceBookingItem job) {
    if (job.isInspection) return 'inspection'.tr(context);
    final price = job.estimatedPrice ?? 0;
    if (price > 1000) return 'high_paying_filter'.tr(context);
    final dist = job.distanceKm ?? 99;
    if (dist < 3) return 'nearby_filter'.tr(context);
    return 'standard'.tr(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            } else {
              Navigator.pushReplacementNamed(context, '/worker/dashboard');
            }
          },
        ),
        title: Text(
          'incoming_jobs'.tr(context),
          style: const TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.w700, fontSize: 18),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF2563EB)),
            onPressed: _fetchJobs,
          ),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _fetchJobs,
          color: const Color(0xFF2563EB),
          child: Column(
            children: [
              // ── Search Bar ─────────────────────────────────────────────
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
                child: TextField(
                  onChanged: (val) {
                    _searchQuery = val;
                    if (val.isEmpty || val.length > 2) _fetchJobs();
                  },
                  decoration: InputDecoration(
                    hintText: 'search_by_service_type'.tr(context),
                    hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 14),
                    prefixIcon: const Icon(Icons.search_rounded, color: Color(0xFF64748B)),
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                    contentPadding: const EdgeInsets.symmetric(vertical: 14),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    ),
                  ),
                ),
              ),

              // ── Filter Chips ───────────────────────────────────────────
              SizedBox(
                height: 44,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: _filters.length,
                  itemBuilder: (ctx, idx) {
                    final filter = _filters[idx];
                    final isSelected = _selectedFilter == filter;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: FilterChip(
                        label: Text(
                          filter == 'All' ? 'all_filter'.tr(context) :
                          filter == 'Nearby' ? 'nearby_filter'.tr(context) :
                          filter == 'High Paying' ? 'high_paying_filter'.tr(context) :
                          filter == 'Inspection' ? 'inspection'.tr(context) :
                          filter == 'Scheduled' ? 'scheduled'.tr(context) : filter,
                        ),
                        selected: isSelected,
                        selectedColor: const Color(0xFFEFF6FF),
                        backgroundColor: const Color(0xFFF8FAFC),
                        labelStyle: TextStyle(
                          fontSize: 12,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                          color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF475569),
                        ),
                        side: BorderSide(
                          color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
                        ),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        onSelected: (_) {
                          setState(() => _selectedFilter = filter);
                          _fetchJobs();
                        },
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 12),

              // ── Content ────────────────────────────────────────────────
              Expanded(
                child: _buildContent(),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const WorkerBottomNavigationBar(currentIndex: 1),
    );
  }

  Widget _buildContent() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)));
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off_rounded, size: 56, color: Color(0xFF94A3B8)),
              const SizedBox(height: 16),
              Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF64748B))),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _fetchJobs,
                icon: const Icon(Icons.refresh_rounded),
                label: Text('retry'.tr(context)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (_jobs.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
        children: [
          const SizedBox(height: 80),
          Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                    child: const Icon(Icons.work_outline_rounded, size: 48, color: Color(0xFF2563EB)),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'no_jobs_available'.tr(context),
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'no_open_job_requests'.tr(context),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.5),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
      itemCount: _jobs.length,
      itemBuilder: (ctx, idx) => _buildJobCard(_jobs[idx]),
    );
  }

  Widget _buildJobCard(MarketplaceBookingItem job) {
    final badgeColor = _badgeColor(job);
    final badgeLabel = _badgeLabel(job);
    final distText = job.distanceKm != null ? '${job.distanceKm!.toStringAsFixed(1)} km' : '--';
    final priceText = job.estimatedPrice != null ? '₹${job.estimatedPrice!.toStringAsFixed(0)}' : '₹${job.baseMarketPrice.toStringAsFixed(0)}';
    final timeText = job.scheduledDate != null
        ? '${job.scheduledDate}${job.scheduledTime != null ? ' • ${job.scheduledTime}' : ''}'
        : 'ASAP';

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: job.hasApplied ? const Color(0xFF10B981).withOpacity(0.4) : const Color(0xFFF1F5F9),
          width: job.hasApplied ? 1.5 : 1,
        ),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header: Badge + Distance + Applied ──────────────────────
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: badgeColor.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(badgeLabel, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: badgeColor)),
                  ),
                  if (job.hasApplied) ...[
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFD1FAE5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('applied'.tr(context), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF065F46))),
                    ),
                  ],
                ],
              ),
              Row(
                children: [
                  const Icon(Icons.near_me_rounded, size: 14, color: Color(0xFF2563EB)),
                  const SizedBox(width: 4),
                  Text(distText, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
                ],
              ),
            ],
          ),

          const SizedBox(height: 12),

          // ── Service name ─────────────────────────────────────────────
          Text(
            job.serviceName,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A), letterSpacing: -0.4),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              const Icon(Icons.location_on_outlined, size: 15, color: Color(0xFF64748B)),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  job.address.approximateLocation,
                  style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // ── Earnings & Time ──────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(14)),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('est_earnings'.tr(context), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Color(0xFF64748B))),
                      const SizedBox(height: 2),
                      Text(priceText, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF10B981))),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('scheduled'.tr(context), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Color(0xFF64748B))),
                      const SizedBox(height: 2),
                      Text(timeText, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)), overflow: TextOverflow.ellipsis),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // ── Action Buttons ───────────────────────────────────────────
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/worker/jobs/details', arguments: {'booking_id': job.id});
                  },
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFCBD5E1), width: 1.5),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: Text('view_details'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF475569))),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: job.hasApplied ? null : () => _applyForJob(job),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: job.hasApplied ? const Color(0xFF10B981) : const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: const Color(0xFF10B981),
                    disabledForegroundColor: Colors.white,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: Text(
                    job.hasApplied ? 'applied_check'.tr(context) : 'apply_now'.tr(context),
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
