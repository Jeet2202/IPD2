import 'dart:async';
import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/worker_dashboard_model.dart';
import '../../services/worker_dashboard_service.dart';
import '../../widgets/notification_bell.dart';
import '../../l10n/app_translations.dart';
import '../../widgets/language_selector_widget.dart';
import '../applications/worker_applications_screen.dart';
import '../marketplace/widgets/marketplace_booking_card.dart';
import '../marketplace/widgets/marketplace_booking_detail_modal.dart';
import '../widgets/worker_bottom_navigation_bar.dart';

class WorkerDashboardScreen extends StatefulWidget {
  final VoidCallback? onNavigateToMarketplace;

  const WorkerDashboardScreen({
    super.key,
    this.onNavigateToMarketplace,
  });

  @override
  State<WorkerDashboardScreen> createState() => _WorkerDashboardScreenState();
}

class _WorkerDashboardScreenState extends State<WorkerDashboardScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  WorkerDashboardData? _dashboardData;
  bool _isTogglingAvailability = false;
  Timer? _autoRefreshTimer;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _loadDashboardData(isSilent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadDashboardData({bool isSilent = false}) async {
    if (!mounted) return;

    if (!isSilent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final data = await WorkerDashboardService.instance.fetchDashboardData();
      if (!mounted) return;

      setState(() {
        _dashboardData = data;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _handleAvailabilityToggle(bool value) async {
    if (_dashboardData == null || _isTogglingAvailability) return;

    final targetStatus = value ? 'available' : 'offline';

    setState(() {
      _isTogglingAvailability = true;
    });

    try {
      await WorkerDashboardService.instance.updateAvailability(targetStatus);
      if (!mounted) return;

      await _loadDashboardData();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update availability: ${e.toString()}'),
          backgroundColor: const Color(0xFFEF4444),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isTogglingAvailability = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.build_circle_rounded, color: Color(0xFF2563EB), size: 24),
            const SizedBox(width: 8),
            Text(
              'worker_dashboard'.tr(context),
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF64748B)),
            onPressed: _loadDashboardData,
            tooltip: 'Refresh Dashboard',
          ),
          const NotificationBell(),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          color: const Color(0xFF2563EB),
          onRefresh: _loadDashboardData,
          child: _buildBody(),
        ),
      ),
      bottomNavigationBar: const WorkerBottomNavigationBar(currentIndex: 0),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF2563EB)),
      );
    }

    if (_errorMessage != null) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.25),
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.cloud_off_rounded, size: 52, color: Color(0xFFEF4444)),
                  const SizedBox(height: 16),
                  const Text(
                    'Failed to Load Dashboard',
                    style: TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _errorMessage!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: _loadDashboardData,
                    icon: const Icon(Icons.refresh_rounded, size: 18),
                    label: const Text('Retry Loading'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    final data = _dashboardData!;

    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Welcome Banner
          _buildHeaderWelcome(data),

          const SizedBox(height: 20),

          // Section 1: Availability Card
          _buildAvailabilityCard(data),

          const SizedBox(height: 20),

          // Section 2: Marketplace Statistics Grid
          _buildStatisticsSection(data),

          const SizedBox(height: 24),

          // Section 3: Recommended Jobs Section
          _buildRecommendedJobsSection(data),

          const SizedBox(height: 24),

          // Section 4: My Applications Summary Card
          _buildApplicationsSummaryCard(data),

          const SizedBox(height: 24),

          // Section 5: Marketplace Preview Section
          _buildMarketplacePreviewSection(data),

          const SizedBox(height: 28),
        ],
      ),
    );
  }

  Widget _buildHeaderWelcome(WorkerDashboardData data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${'hello_worker'.tr(context)}, ${data.workerName}',
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: Color(0xFF0F172A),
            letterSpacing: -0.4,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'discover_jobs_subtitle'.tr(context),
          style: const TextStyle(
            fontSize: 13,
            color: Color(0xFF64748B),
          ),
        ),
      ],
    );
  }

  Widget _buildAvailabilityCard(WorkerDashboardData data) {
    final isAvailable = data.isAvailable;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: isAvailable ? const Color(0xFFEFF6FF) : const Color(0xFFFFF1F2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isAvailable ? const Color(0xFFBFDBFE) : const Color(0xFFFECDD3),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(
              isAvailable ? Icons.sensors_rounded : Icons.sensors_off_rounded,
              color: isAvailable ? const Color(0xFF2563EB) : const Color(0xFFE11D48),
              size: 26,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      isAvailable ? 'available_for_jobs'.tr(context) : 'offline_unavailable'.tr(context),
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: isAvailable ? const Color(0xFF1E40AF) : const Color(0xFF9F1239),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '${'working_radius'.tr(context)}: ${data.workingRadiusKm.toStringAsFixed(0)} km',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: isAvailable,
            onChanged: _isTogglingAvailability ? null : _handleAvailabilityToggle,
            activeColor: const Color(0xFF2563EB),
          ),
        ],
      ),
    );
  }

  Widget _buildStatisticsSection(WorkerDashboardData data) {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            title: 'available_jobs'.tr(context),
            value: data.stats.availableJobs.toString(),
            icon: Icons.work_outline_rounded,
            color: const Color(0xFF2563EB),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            title: 'recommended'.tr(context),
            value: data.stats.recommendedJobs.toString(),
            icon: Icons.star_rounded,
            color: const Color(0xFFD97706),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            title: 'applications'.tr(context),
            value: data.stats.activeApplications.toString(),
            icon: Icons.assignment_outlined,
            color: const Color(0xFF059669),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Color(0xFF64748B),
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendedJobsSection(WorkerDashboardData data) {
    final jobs = data.recommendedJobs;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.auto_awesome_rounded, color: Color(0xFFD97706), size: 20),
            const SizedBox(width: 8),
            Text(
              'recommended_for_you'.tr(context),
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (jobs.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Text(
              'no_recommended_jobs'.tr(context),
              style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
          )
        else
          Column(
            children: jobs.map((item) {
              return MarketplaceBookingCard(
                booking: item,
                onTap: () => MarketplaceBookingDetailModal.show(context, item.id),
              );
            }).toList(),
          ),
      ],
    );
  }

  Widget _buildApplicationsSummaryCard(WorkerDashboardData data) {
    final appSummary = data.applicationsSummary;

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
              Row(
                children: [
                  const Icon(Icons.assignment_rounded, color: Color(0xFF2563EB), size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'my_applications'.tr(context),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                ],
              ),
              TextButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (ctx) => const WorkerApplicationsScreen(),
                    ),
                  );
                },
                child: Text('view_all'.tr(context)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildAppCountTile('total'.tr(context), appSummary.total, const Color(0xFF3B82F6)),
              _buildAppCountTile('pending'.tr(context), appSummary.pending, const Color(0xFFD97706)),
              _buildAppCountTile('accepted'.tr(context), appSummary.accepted, const Color(0xFF059669)),
              _buildAppCountTile('rejected'.tr(context), appSummary.rejected, const Color(0xFFDC2626)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAppCountTile(String label, int count, Color color) {
    return Column(
      children: [
        Text(
          count.toString(),
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: color,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: Color(0xFF64748B),
          ),
        ),
      ],
    );
  }

  Widget _buildMarketplacePreviewSection(WorkerDashboardData data) {
    final jobs = data.recentJobs;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'latest_marketplace_jobs'.tr(context),
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            TextButton(
              onPressed: () {
                if (widget.onNavigateToMarketplace != null) {
                  widget.onNavigateToMarketplace!();
                } else {
                  Navigator.pushNamed(context, AppRoutes.workerMarketplace);
                }
              },
              child: Text('view_all_jobs'.tr(context)),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (jobs.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Text(
              'no_marketplace_jobs'.tr(context),
              style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
          )
        else
          Column(
            children: jobs.map((item) {
              return MarketplaceBookingCard(
                booking: item,
                onTap: () => MarketplaceBookingDetailModal.show(context, item.id),
              );
            }).toList(),
          ),
      ],
    );
  }
}
