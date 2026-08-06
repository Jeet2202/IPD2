// File: lib/models/marketplace_booking_model.dart

class MarketplaceAddress {
  final String city;
  final String state;
  final String postalCode;
  final double? latitude;
  final double? longitude;

  MarketplaceAddress({
    required this.city,
    required this.state,
    required this.postalCode,
    this.latitude,
    this.longitude,
  });

  factory MarketplaceAddress.fromJson(Map<String, dynamic> json) {
    return MarketplaceAddress(
      city: json['city'] as String? ?? '',
      state: json['state'] as String? ?? '',
      postalCode: json['postal_code'] as String? ?? '',
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );
  }

  String get approximateLocation => '$city, $postalCode';
}

class MarketplaceBookingItem {
  final String id;
  final String bookingNumber;
  final String bookingType;
  final String status;
  final String serviceName;
  final String categorySlug;
  final double baseMarketPrice;
  final MarketplaceAddress address;
  final String? scheduledDate;
  final String? scheduledTime;
  final double? estimatedPrice;
  final int? estimatedDurationMinutes;
  final double? distanceKm;
  final bool isRecommended;
  final bool hasApplied;
  final String? applicationId;
  final DateTime createdAt;

  final String? problemDescription;
  final List<String> problemPhotos;
  final String? customTitle;
  final String? customDescription;
  final double? customBudget;
  final String? customerNotes;
  final double? inspectionCharge;
  final String? inspectionStatus;
  final String? paymentStatus;

  MarketplaceBookingItem({
    required this.id,
    required this.bookingNumber,
    required this.bookingType,
    required this.status,
    required this.serviceName,
    required this.categorySlug,
    required this.baseMarketPrice,
    required this.address,
    this.scheduledDate,
    this.scheduledTime,
    this.estimatedPrice,
    this.estimatedDurationMinutes,
    this.distanceKm,
    this.isRecommended = false,
    this.hasApplied = false,
    this.applicationId,
    required this.createdAt,
    this.problemDescription,
    this.problemPhotos = const [],
    this.customTitle,
    this.customDescription,
    this.customBudget,
    this.customerNotes,
    this.inspectionCharge,
    this.inspectionStatus,
    this.paymentStatus,
  });

  factory MarketplaceBookingItem.fromJson(Map<String, dynamic> json) {
    final svcSnap = json['service_snapshot'] as Map<String, dynamic>? ?? {};
    final addrSnap = json['address'] as Map<String, dynamic>? ?? {};

    final photosRaw = json['problem_photos'] as List?;
    final photos = photosRaw != null ? photosRaw.map((e) => e.toString()).toList() : <String>[];

    return MarketplaceBookingItem(
      id: json['id'] as String? ?? '',
      bookingNumber: json['booking_number'] as String? ?? '',
      bookingType: json['booking_type'] as String? ?? 'normal_service',
      status: json['status'] as String? ?? 'pending',
      serviceName: svcSnap['name'] as String? ?? json['custom_title'] as String? ?? 'Service',
      categorySlug: svcSnap['category_slug'] as String? ?? json['category_slug'] as String? ?? '',
      baseMarketPrice: (svcSnap['base_market_price'] as num?)?.toDouble() ?? 0.0,
      address: MarketplaceAddress.fromJson(addrSnap),
      scheduledDate: json['scheduled_date'] as String?,
      scheduledTime: json['scheduled_time'] as String?,
      estimatedPrice: (json['estimated_price'] as num?)?.toDouble() ?? (json['inspection_charge'] as num?)?.toDouble(),
      estimatedDurationMinutes: (json['estimated_duration_minutes'] as num?)?.toInt(),
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
      isRecommended: json['is_recommended'] as bool? ?? false,
      hasApplied: json['has_applied'] as bool? ?? false,
      applicationId: json['application_id'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      problemDescription: json['problem_description'] as String?,
      problemPhotos: photos,
      customTitle: json['custom_title'] as String?,
      customDescription: json['custom_description'] as String?,
      customBudget: (json['custom_budget'] as num?)?.toDouble(),
      customerNotes: json['customer_notes'] as String?,
      inspectionCharge: (json['inspection_charge'] as num?)?.toDouble(),
      inspectionStatus: json['inspection_status'] as String?,
      paymentStatus: json['payment_status'] as String?,
    );
  }

  bool get isInspection => bookingType == 'inspection_request';
}

class MarketplaceBookingDetail extends MarketplaceBookingItem {
  MarketplaceBookingDetail({
    required super.id,
    required super.bookingNumber,
    required super.bookingType,
    required super.status,
    required super.serviceName,
    required super.categorySlug,
    required super.baseMarketPrice,
    required super.address,
    super.scheduledDate,
    super.scheduledTime,
    super.estimatedPrice,
    super.estimatedDurationMinutes,
    super.distanceKm,
    super.isRecommended,
    super.hasApplied,
    super.applicationId,
    required super.createdAt,
    super.problemDescription,
    super.problemPhotos,
    super.customTitle,
    super.customDescription,
    super.customBudget,
    super.customerNotes,
    super.inspectionCharge,
    super.inspectionStatus,
    super.paymentStatus,
  });

  factory MarketplaceBookingDetail.fromJson(Map<String, dynamic> json) {
    final item = MarketplaceBookingItem.fromJson(json);
    return MarketplaceBookingDetail(
      id: item.id,
      bookingNumber: item.bookingNumber,
      bookingType: item.bookingType,
      status: item.status,
      serviceName: item.serviceName,
      categorySlug: item.categorySlug,
      baseMarketPrice: item.baseMarketPrice,
      address: item.address,
      scheduledDate: item.scheduledDate,
      scheduledTime: item.scheduledTime,
      estimatedPrice: item.estimatedPrice,
      estimatedDurationMinutes: item.estimatedDurationMinutes,
      distanceKm: item.distanceKm,
      isRecommended: item.isRecommended,
      hasApplied: item.hasApplied,
      applicationId: item.applicationId,
      createdAt: item.createdAt,
      problemDescription: item.problemDescription,
      problemPhotos: item.problemPhotos,
      customTitle: item.customTitle,
      customDescription: item.customDescription,
      customBudget: item.customBudget,
      customerNotes: item.customerNotes,
      inspectionCharge: item.inspectionCharge,
      inspectionStatus: item.inspectionStatus,
      paymentStatus: item.paymentStatus,
    );
  }
}

class MarketplacePaginatedResult {
  final List<MarketplaceBookingItem> items;
  final int total;
  final int page;
  final int pageSize;
  final int totalPages;

  MarketplacePaginatedResult({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
  });

  factory MarketplacePaginatedResult.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List? ?? [];
    final items = rawItems
        .map((e) => MarketplaceBookingItem.fromJson(e as Map<String, dynamic>))
        .toList();

    return MarketplacePaginatedResult(
      items: items,
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      pageSize: json['page_size'] as int? ?? 20,
      totalPages: json['total_pages'] as int? ?? 0,
    );
  }
}
