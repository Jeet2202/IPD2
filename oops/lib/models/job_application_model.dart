// File: lib/models/job_application_model.dart

class JobApplicationItem {
  final String id;
  final String bookingId;
  final String workerId;
  final String applicationStatus;
  final String? coverLetter;
  final double? proposedPrice;
  final String bookingNumber;
  final String serviceName;
  final String categorySlug;
  final String bookingType;
  final String bookingStatus;
  final String? scheduledDate;
  final double? estimatedPrice;
  final DateTime appliedAt;

  JobApplicationItem({
    required this.id,
    required this.bookingId,
    required this.workerId,
    required this.applicationStatus,
    this.coverLetter,
    this.proposedPrice,
    required this.bookingNumber,
    required this.serviceName,
    required this.categorySlug,
    required this.bookingType,
    required this.bookingStatus,
    this.scheduledDate,
    this.estimatedPrice,
    required this.appliedAt,
  });

  factory JobApplicationItem.fromJson(Map<String, dynamic> json) {
    return JobApplicationItem(
      id: json['id'] as String? ?? '',
      bookingId: json['booking_id'] as String? ?? '',
      workerId: json['worker_id'] as String? ?? '',
      applicationStatus: json['application_status'] as String? ?? 'pending',
      coverLetter: json['cover_letter'] as String?,
      proposedPrice: (json['proposed_price'] as num?)?.toDouble(),
      bookingNumber: json['booking_number'] as String? ?? '',
      serviceName: json['service_name'] as String? ?? 'Service',
      categorySlug: json['category_slug'] as String? ?? '',
      bookingType: json['booking_type'] as String? ?? 'normal_service',
      bookingStatus: json['booking_status'] as String? ?? 'pending',
      scheduledDate: json['scheduled_date'] as String?,
      estimatedPrice: (json['estimated_price'] as num?)?.toDouble(),
      appliedAt: json['applied_at'] != null
          ? DateTime.tryParse(json['applied_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  bool get isPending => applicationStatus == 'pending';
  bool get isAccepted => applicationStatus == 'accepted';
  bool get isRejected => applicationStatus == 'rejected';
}

class JobApplicationPaginatedResult {
  final List<JobApplicationItem> items;
  final int total;
  final int page;
  final int pageSize;
  final int totalPages;

  JobApplicationPaginatedResult({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
  });

  factory JobApplicationPaginatedResult.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List? ?? [];
    final items = rawItems
        .map((e) => JobApplicationItem.fromJson(e as Map<String, dynamic>))
        .toList();

    return JobApplicationPaginatedResult(
      items: items,
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 20,
      totalPages: json['total_pages'] as int? ?? 0,
    );
  }
}
