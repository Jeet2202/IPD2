// File: lib/models/worker_dashboard_model.dart

import 'marketplace_booking_model.dart';

class MarketplaceStats {
  final int availableJobs;
  final int recommendedJobs;
  final int activeApplications;

  MarketplaceStats({
    required this.availableJobs,
    required this.recommendedJobs,
    required this.activeApplications,
  });

  factory MarketplaceStats.fromJson(Map<String, dynamic> json) {
    return MarketplaceStats(
      availableJobs: json['available_jobs'] as int? ?? 0,
      recommendedJobs: json['recommended_jobs'] as int? ?? 0,
      activeApplications: json['active_applications'] as int? ?? 0,
    );
  }
}

class ApplicationsSummary {
  final int total;
  final int pending;
  final int accepted;
  final int rejected;

  ApplicationsSummary({
    required this.total,
    required this.pending,
    required this.accepted,
    required this.rejected,
  });

  factory ApplicationsSummary.fromJson(Map<String, dynamic> json) {
    return ApplicationsSummary(
      total: json['total'] as int? ?? 0,
      pending: json['pending'] as int? ?? 0,
      accepted: json['accepted'] as int? ?? 0,
      rejected: json['rejected'] as int? ?? 0,
    );
  }
}

class WorkerDashboardData {
  final String workerId;
  final String workerName;
  final String availability;
  final double workingRadiusKm;
  final bool profileCompleted;
  final MarketplaceStats stats;
  final ApplicationsSummary applicationsSummary;
  final List<MarketplaceBookingItem> recommendedJobs;
  final List<MarketplaceBookingItem> recentJobs;

  WorkerDashboardData({
    required this.workerId,
    required this.workerName,
    required this.availability,
    required this.workingRadiusKm,
    required this.profileCompleted,
    required this.stats,
    required this.applicationsSummary,
    required this.recommendedJobs,
    required this.recentJobs,
  });

  bool get isAvailable => availability == 'available';

  factory WorkerDashboardData.fromJson(Map<String, dynamic> json) {
    final rawRec = json['recommended_jobs'] as List? ?? [];
    final recJobs = rawRec
        .map((e) => MarketplaceBookingItem.fromJson(e as Map<String, dynamic>))
        .toList();

    final rawRecent = json['recent_jobs'] as List? ?? [];
    final recentJobs = rawRecent
        .map((e) => MarketplaceBookingItem.fromJson(e as Map<String, dynamic>))
        .toList();

    return WorkerDashboardData(
      workerId: json['worker_id'] as String? ?? '',
      workerName: json['worker_name'] as String? ?? 'Worker',
      availability: json['availability'] as String? ?? 'available',
      workingRadiusKm: (json['working_radius_km'] as num?)?.toDouble() ?? 10.0,
      profileCompleted: json['profile_completed'] as bool? ?? false,
      stats: MarketplaceStats.fromJson(
          json['stats'] as Map<String, dynamic>? ?? {}),
      applicationsSummary: ApplicationsSummary.fromJson(
          json['applications_summary'] as Map<String, dynamic>? ?? {}),
      recommendedJobs: recJobs,
      recentJobs: recentJobs,
    );
  }
}
