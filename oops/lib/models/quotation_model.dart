// File: lib/models/quotation_model.dart

class QuotationItem {
  final String id;
  final String quotationNumber;
  final String bookingId;
  final String workerId;
  final String applicationId;
  final String quotationStatus;
  final double labourCost;
  final double materialCost;
  final double inspectionCharge;
  final double additionalCharges;
  final double taxAmount;
  final double discountAmount;
  final double totalAmount;
  final String estimatedDuration;
  final String validityDate;
  final String? workStartDate;
  final String? workDescription;
  final String? termsAndConditions;
  final String? notes;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? submittedAt;

  QuotationItem({
    required this.id,
    required this.quotationNumber,
    required this.bookingId,
    required this.workerId,
    required this.applicationId,
    required this.quotationStatus,
    required this.labourCost,
    required this.materialCost,
    required this.inspectionCharge,
    required this.additionalCharges,
    required this.taxAmount,
    required this.discountAmount,
    required this.totalAmount,
    required this.estimatedDuration,
    required this.validityDate,
    this.workStartDate,
    this.workDescription,
    this.termsAndConditions,
    this.notes,
    required this.createdAt,
    required this.updatedAt,
    this.submittedAt,
  });

  factory QuotationItem.fromJson(Map<String, dynamic> json) {
    return QuotationItem(
      id: json['id'] as String? ?? '',
      quotationNumber: json['quotation_number'] as String? ?? '',
      bookingId: json['booking_id'] as String? ?? '',
      workerId: json['worker_id'] as String? ?? '',
      applicationId: json['application_id'] as String? ?? '',
      quotationStatus: json['quotation_status'] as String? ?? 'draft',
      labourCost: (json['labour_cost'] as num?)?.toDouble() ?? 0.0,
      materialCost: (json['material_cost'] as num?)?.toDouble() ?? 0.0,
      inspectionCharge: (json['inspection_charge'] as num?)?.toDouble() ?? 0.0,
      additionalCharges: (json['additional_charges'] as num?)?.toDouble() ?? 0.0,
      taxAmount: (json['tax_amount'] as num?)?.toDouble() ?? 0.0,
      discountAmount: (json['discount_amount'] as num?)?.toDouble() ?? 0.0,
      totalAmount: (json['total_amount'] as num?)?.toDouble() ?? 0.0,
      estimatedDuration: json['estimated_duration'] as String? ?? '',
      validityDate: json['validity_date'] as String? ?? '',
      workStartDate: json['work_start_date'] as String?,
      workDescription: json['work_description'] as String?,
      termsAndConditions: json['terms_and_conditions'] as String?,
      notes: json['notes'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String) ?? DateTime.now()
          : DateTime.now(),
      submittedAt: json['submitted_at'] != null
          ? DateTime.tryParse(json['submitted_at'] as String)
          : null,
    );
  }

  bool get isDraft => quotationStatus == 'draft';
  bool get isSubmitted => quotationStatus == 'submitted';
  bool get isAccepted => quotationStatus == 'accepted';
  bool get isRejected => quotationStatus == 'rejected';
}

class WorkerSummary {
  final String id;
  final String fullName;
  final String? profilePhotoUrl;
  final double rating;
  final double experienceYears;
  final List<String> skills;

  WorkerSummary({
    required this.id,
    required this.fullName,
    this.profilePhotoUrl,
    this.rating = 5.0,
    this.experienceYears = 0.0,
    this.skills = const [],
  });

  factory WorkerSummary.fromJson(Map<String, dynamic> json) {
    final rawSkills = json['skills'] as List? ?? [];
    final skillsList = rawSkills.map((e) => e.toString()).toList();

    return WorkerSummary(
      id: json['id'] as String? ?? '',
      fullName: json['full_name'] as String? ?? 'Professional Worker',
      profilePhotoUrl: json['profile_photo_url'] as String?,
      rating: (json['rating'] as num?)?.toDouble() ?? 5.0,
      experienceYears: (json['experience_years'] as num?)?.toDouble() ?? 0.0,
      skills: skillsList,
    );
  }
}

class CustomerQuotationItem {
  final QuotationItem quotation;
  final WorkerSummary worker;

  CustomerQuotationItem({
    required this.quotation,
    required this.worker,
  });

  factory CustomerQuotationItem.fromJson(Map<String, dynamic> json) {
    final item = QuotationItem.fromJson(json);
    final workerData = json['worker'] as Map<String, dynamic>? ?? {};

    return CustomerQuotationItem(
      quotation: item,
      worker: WorkerSummary.fromJson(workerData),
    );
  }
}

class QuotationHistoryLogItem {
  final String id;
  final String quotationId;
  final String bookingId;
  final String workerId;
  final String actorId;
  final String actorRole;
  final String eventType;
  final String? previousStatus;
  final String newStatus;
  final Map<String, dynamic>? previousSnapshot;
  final Map<String, dynamic> newSnapshot;
  final DateTime createdAt;
  final String? notes;

  QuotationHistoryLogItem({
    required this.id,
    required this.quotationId,
    required this.bookingId,
    required this.workerId,
    required this.actorId,
    required this.actorRole,
    required this.eventType,
    this.previousStatus,
    required this.newStatus,
    this.previousSnapshot,
    required this.newSnapshot,
    required this.createdAt,
    this.notes,
  });

  factory QuotationHistoryLogItem.fromJson(Map<String, dynamic> json) {
    return QuotationHistoryLogItem(
      id: json['id'] as String? ?? '',
      quotationId: json['quotation_id'] as String? ?? '',
      bookingId: json['booking_id'] as String? ?? '',
      workerId: json['worker_id'] as String? ?? '',
      actorId: json['actor_id'] as String? ?? '',
      actorRole: json['actor_role'] as String? ?? 'user',
      eventType: json['event_type'] as String? ?? 'event',
      previousStatus: json['previous_status'] as String?,
      newStatus: json['new_status'] as String? ?? 'draft',
      previousSnapshot: json['previous_snapshot'] as Map<String, dynamic>?,
      newSnapshot: (json['new_snapshot'] as Map<String, dynamic>?) ?? {},
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      notes: json['notes'] as String?,
    );
  }
}
