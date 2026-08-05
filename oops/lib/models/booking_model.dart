// File: lib/models/booking_model.dart

/// Data model representing a customer Booking response from the backend.
/// Maps 1-to-1 with app/booking/schemas.py (BookingResponse).

class ServiceSnapshotModel {
  final String serviceId;
  final String name;
  final String categoryId;
  final String categorySlug;
  final double baseMarketPrice;
  final int estimatedDurationMinutes;
  final bool isInspectionRequired;

  const ServiceSnapshotModel({
    required this.serviceId,
    required this.name,
    required this.categoryId,
    required this.categorySlug,
    required this.baseMarketPrice,
    required this.estimatedDurationMinutes,
    required this.isInspectionRequired,
  });

  factory ServiceSnapshotModel.fromJson(Map<String, dynamic> json) {
    return ServiceSnapshotModel(
      serviceId: json['service_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      categoryId: json['category_id'] as String? ?? '',
      categorySlug: json['category_slug'] as String? ?? '',
      baseMarketPrice: (json['base_market_price'] as num?)?.toDouble() ?? 0.0,
      estimatedDurationMinutes: (json['estimated_duration_minutes'] as num?)?.toInt() ?? 0,
      isInspectionRequired: json['is_inspection_required'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'service_id': serviceId,
        'name': name,
        'category_id': categoryId,
        'category_slug': categorySlug,
        'base_market_price': baseMarketPrice,
        'estimated_duration_minutes': estimatedDurationMinutes,
        'is_inspection_required': isInspectionRequired,
      };
}

class AddressSnapshotModel {
  final String addressId;
  final String label;
  final String fullName;
  final String phone;
  final String addressLine1;
  final String? addressLine2;
  final String? landmark;
  final String city;
  final String state;
  final String country;
  final String postalCode;
  final double? latitude;
  final double? longitude;

  const AddressSnapshotModel({
    required this.addressId,
    required this.label,
    required this.fullName,
    required this.phone,
    required this.addressLine1,
    this.addressLine2,
    this.landmark,
    required this.city,
    required this.state,
    required this.country,
    required this.postalCode,
    this.latitude,
    this.longitude,
  });

  factory AddressSnapshotModel.fromJson(Map<String, dynamic> json) {
    return AddressSnapshotModel(
      addressId: json['address_id'] as String? ?? '',
      label: json['label'] as String? ?? 'Home',
      fullName: json['full_name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      addressLine1: json['address_line_1'] as String? ?? '',
      addressLine2: json['address_line_2'] as String?,
      landmark: json['landmark'] as String?,
      city: json['city'] as String? ?? '',
      state: json['state'] as String? ?? '',
      country: json['country'] as String? ?? 'India',
      postalCode: json['postal_code'] as String? ?? '',
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'address_id': addressId,
        'label': label,
        'full_name': fullName,
        'phone': phone,
        'address_line_1': addressLine1,
        'address_line_2': addressLine2,
        'landmark': landmark,
        'city': city,
        'state': state,
        'country': country,
        'postal_code': postalCode,
        'latitude': latitude,
        'longitude': longitude,
      };

  String get shortAddress {
    final parts = <String>[addressLine1];
    if (addressLine2 != null && addressLine2!.isNotEmpty) parts.add(addressLine2!);
    parts.addAll([city, '$state - $postalCode']);
    return parts.join(', ');
  }
}

class BookingTimelineEventModel {
  final String eventId;
  final String eventType;
  final String status;
  final String? previousStatus;
  final String? newStatus;
  final String title;
  final String? description;
  final String actorId;
  final String actorRole;
  final String timestamp;
  final Map<String, dynamic> metadata;

  const BookingTimelineEventModel({
    required this.eventId,
    this.eventType = 'STATUS_CHANGE',
    required this.status,
    this.previousStatus,
    this.newStatus,
    required this.title,
    this.description,
    required this.actorId,
    required this.actorRole,
    required this.timestamp,
    this.metadata = const {},
  });

  factory BookingTimelineEventModel.fromJson(Map<String, dynamic> json) {
    return BookingTimelineEventModel(
      eventId: json['event_id'] as String? ?? '',
      eventType: json['event_type'] as String? ?? 'STATUS_CHANGE',
      status: json['status'] as String? ?? '',
      previousStatus: json['previous_status'] as String?,
      newStatus: json['new_status'] as String?,
      title: json['title'] as String? ?? '',
      description: json['description'] as String?,
      actorId: json['actor_id'] as String? ?? '',
      actorRole: json['actor_role'] as String? ?? '',
      timestamp: json['timestamp'] as String? ?? '',
      metadata: json['metadata'] as Map<String, dynamic>? ?? {},
    );
  }
}

class BookingModel {
  final String id;
  final String bookingNumber;
  final String customerId;
  final String bookingType;
  final String status;
  final ServiceSnapshotModel serviceSnapshot;
  final AddressSnapshotModel addressSnapshot;
  final double? latitude;
  final double? longitude;
  final String? scheduledDate;
  final String? scheduledTime;
  final double? estimatedPrice;
  final int? estimatedDurationMinutes;
  final String? customerNotes;
  final String? problemDescription;
  final List<String> problemPhotos;
  final String? workerId;
  final String? workerName;
  final String? workerPhone;
  final String? assignedAt;
  final String? enRouteAt;
  final String? arrivedAt;
  final String? startedAt;
  final String? completedAt;
  final String? cancelledAt;
  final String? cancellationReason;
  final double? finalPrice;
  final String? inspectionId;
  final String? quotationId;
  final String? paymentId;
  final String? completionNotes;
  final String? workSummary;
  final List<String> beforePhotos;
  final List<String> afterPhotos;
  final List<BookingTimelineEventModel> timeline;
  final String createdAt;
  final String updatedAt;
  final int applicantCount;

  const BookingModel({
    required this.id,
    required this.bookingNumber,
    required this.customerId,
    required this.bookingType,
    required this.status,
    required this.serviceSnapshot,
    required this.addressSnapshot,
    this.latitude,
    this.longitude,
    this.scheduledDate,
    this.scheduledTime,
    this.estimatedPrice,
    this.estimatedDurationMinutes,
    this.customerNotes,
    this.problemDescription,
    this.problemPhotos = const [],
    this.workerId,
    this.workerName,
    this.workerPhone,
    this.assignedAt,
    this.enRouteAt,
    this.arrivedAt,
    this.startedAt,
    this.completedAt,
    this.cancelledAt,
    this.cancellationReason,
    this.finalPrice,
    this.inspectionId,
    this.quotationId,
    this.paymentId,
    this.completionNotes,
    this.workSummary,
    this.beforePhotos = const [],
    this.afterPhotos = const [],
    this.timeline = const [],
    required this.createdAt,
    required this.updatedAt,
    this.applicantCount = 0,
  });

  bool get isPending => status == 'pending';
  bool get isAssigned => status == 'assigned' || status == 'accepted';
  bool get isWorkerEnRoute => status == 'worker_en_route';
  bool get isArrived => status == 'arrived';
  bool get isInProgress => status == 'in_progress';
  bool get isWorkCompleted => status == 'work_completed';
  bool get isCustomerConfirmed => status == 'customer_confirmed' || status == 'completed';
  bool get isCancelled => status == 'cancelled';

  factory BookingModel.fromJson(Map<String, dynamic> json) {
    final raw = (json['data'] is Map<String, dynamic>) ? json['data'] as Map<String, dynamic> : json;

    return BookingModel(
      id: raw['id'] as String? ?? '',
      bookingNumber: raw['booking_number'] as String? ?? '',
      customerId: raw['customer_id'] as String? ?? '',
      bookingType: raw['booking_type'] as String? ?? 'normal_service',
      status: raw['status'] as String? ?? 'pending',
      serviceSnapshot: ServiceSnapshotModel.fromJson(raw['service_snapshot'] as Map<String, dynamic>? ?? {}),
      addressSnapshot: AddressSnapshotModel.fromJson(raw['address_snapshot'] as Map<String, dynamic>? ?? {}),
      latitude: (raw['latitude'] as num?)?.toDouble(),
      longitude: (raw['longitude'] as num?)?.toDouble(),
      scheduledDate: raw['scheduled_date'] as String?,
      scheduledTime: raw['scheduled_time'] as String?,
      estimatedPrice: (raw['estimated_price'] as num?)?.toDouble(),
      estimatedDurationMinutes: (raw['estimated_duration_minutes'] as num?)?.toInt(),
      customerNotes: raw['customer_notes'] as String?,
      problemDescription: raw['problem_description'] as String?,
      problemPhotos: (raw['problem_photos'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      workerId: raw['worker_id'] as String?,
      workerName: raw['worker_name'] as String?,
      workerPhone: raw['worker_phone'] as String?,
      assignedAt: raw['assigned_at'] as String?,
      enRouteAt: raw['en_route_at'] as String?,
      arrivedAt: raw['arrived_at'] as String?,
      startedAt: raw['started_at'] as String?,
      completedAt: raw['completed_at'] as String?,
      cancelledAt: raw['cancelled_at'] as String?,
      cancellationReason: raw['cancellation_reason'] as String?,
      finalPrice: (raw['final_price'] as num?)?.toDouble(),
      inspectionId: raw['inspection_id'] as String?,
      quotationId: raw['quotation_id'] as String?,
      paymentId: raw['payment_id'] as String?,
      completionNotes: raw['completion_notes'] as String?,
      workSummary: raw['work_summary'] as String?,
      beforePhotos: (raw['before_photos'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      afterPhotos: (raw['after_photos'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      timeline: (raw['timeline'] as List<dynamic>?)
              ?.map((e) => BookingTimelineEventModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      createdAt: raw['created_at'] as String? ?? '',
      updatedAt: raw['updated_at'] as String? ?? '',
      applicantCount: (raw['applicant_count'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'booking_number': bookingNumber,
        'customer_id': customerId,
        'booking_type': bookingType,
        'status': status,
        'service_snapshot': serviceSnapshot.toJson(),
        'address_snapshot': addressSnapshot.toJson(),
        'latitude': latitude,
        'longitude': longitude,
        'scheduled_date': scheduledDate,
        'scheduled_time': scheduledTime,
        'estimated_price': estimatedPrice,
        'estimated_duration_minutes': estimatedDurationMinutes,
        'customer_notes': customerNotes,
        'problem_description': problemDescription,
        'problem_photos': problemPhotos,
        'worker_id': workerId,
        'worker_name': workerName,
        'worker_phone': workerPhone,
        'assigned_at': assignedAt,
        'en_route_at': enRouteAt,
        'arrived_at': arrivedAt,
        'started_at': startedAt,
        'completed_at': completedAt,
        'cancelled_at': cancelledAt,
        'cancellation_reason': cancellationReason,
        'final_price': finalPrice,
        'inspection_id': inspectionId,
        'quotation_id': quotationId,
        'payment_id': paymentId,
        'completion_notes': completionNotes,
        'work_summary': workSummary,
        'before_photos': beforePhotos,
        'after_photos': afterPhotos,
        'created_at': createdAt,
        'updated_at': updatedAt,
        'applicant_count': applicantCount,
      };
}

/// Payload sent to POST /customer/bookings (CreateBookingRequest schema)
class CreateBookingPayload {
  final String serviceId;
  final String addressId;
  final String bookingType; // 'normal_service' or 'inspection_request'
  final String? scheduledDate; // YYYY-MM-DD
  final String? scheduledTime; // e.g. '10:00-12:00'
  final String? customerNotes;
  final String? problemDescription;
  final List<String> problemPhotos;

  const CreateBookingPayload({
    required this.serviceId,
    required this.addressId,
    this.bookingType = 'normal_service',
    this.scheduledDate,
    this.scheduledTime,
    this.customerNotes,
    this.problemDescription,
    this.problemPhotos = const [],
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'service_id': serviceId,
      'address_id': addressId,
      'booking_type': bookingType,
    };
    if (scheduledDate != null && scheduledDate!.isNotEmpty) {
      map['scheduled_date'] = scheduledDate;
    }
    if (scheduledTime != null && scheduledTime!.isNotEmpty) {
      map['scheduled_time'] = scheduledTime;
    }
    if (customerNotes != null && customerNotes!.trim().isNotEmpty) {
      map['customer_notes'] = customerNotes!.trim();
    }
    if (problemDescription != null && problemDescription!.trim().isNotEmpty) {
      map['problem_description'] = problemDescription!.trim();
    }
    if (problemPhotos.isNotEmpty) {
      map['problem_photos'] = problemPhotos;
    }
    return map;
  }
}

/// DTO for an individual booking time slot returned by backend scheduling API
class TimeSlotModel {
  final String slotId;
  final String startTime;
  final String endTime;
  final bool isAvailable;
  final String? reason;

  const TimeSlotModel({
    required this.slotId,
    required this.startTime,
    required this.endTime,
    required this.isAvailable,
    this.reason,
  });

  factory TimeSlotModel.fromJson(Map<String, dynamic> json) {
    return TimeSlotModel(
      slotId: json['slot_id'] as String? ?? '',
      startTime: json['start_time'] as String? ?? '',
      endTime: json['end_time'] as String? ?? '',
      isAvailable: json['is_available'] as bool? ?? true,
      reason: json['reason'] as String?,
    );
  }
}

/// DTO for available slots response returned by GET /customer/bookings/slots
class AvailableSlotsModel {
  final String date;
  final bool isDateAvailable;
  final List<TimeSlotModel> slots;

  const AvailableSlotsModel({
    required this.date,
    required this.isDateAvailable,
    required this.slots,
  });

  factory AvailableSlotsModel.fromJson(Map<String, dynamic> json) {
    final raw = (json['data'] is Map<String, dynamic>) ? json['data'] as Map<String, dynamic> : json;
    final slotList = raw['slots'] as List<dynamic>? ?? [];

    return AvailableSlotsModel(
      date: raw['date'] as String? ?? '',
      isDateAvailable: raw['is_date_available'] as bool? ?? true,
      slots: slotList.map((e) => TimeSlotModel.fromJson(e as Map<String, dynamic>)).toList(),
    );
  }
}
