// File: lib/services/booking_service.dart

import '../constants/api_endpoints.dart';
import '../models/booking_model.dart';
import 'api_service.dart';

class BookingService {
  BookingService._();
  static final BookingService instance = BookingService._();

  final ApiService _apiService = ApiService.instance;

  /// Create a new customer booking via POST /customer/bookings
  Future<BookingModel> createBooking(CreateBookingPayload payload) async {
    final res = await _apiService.post(
      ApiEndpoints.customerBookings,
      payload.toJson(),
    );
    return BookingModel.fromJson(res);
  }

  /// List customer's bookings via GET /customer/bookings
  Future<List<BookingModel>> fetchBookings({
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    final params = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };
    if (status != null && status.isNotEmpty) {
      params['status'] = status;
    }

    final res = await _apiService.get(
      ApiEndpoints.customerBookings,
      params: params,
    );

    final rawData = res['data'] ?? res;
    final List items = rawData is Map<String, dynamic>
        ? (rawData['bookings'] as List? ?? [])
        : (res['bookings'] as List? ?? []);

    return items
        .map((e) => BookingModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// List worker's assigned bookings via GET /worker/bookings
  Future<List<BookingModel>> fetchWorkerBookings({
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    final params = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };
    if (status != null && status.isNotEmpty) {
      params['status'] = status;
    }

    final res = await _apiService.get(
      '/worker/bookings',
      params: params,
    );

    final rawData = res['data'] ?? res;
    final List items = rawData is Map<String, dynamic>
        ? (rawData['bookings'] as List? ?? [])
        : (res['bookings'] as List? ?? []);

    return items
        .map((e) => BookingModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Fetch single booking by ID via GET /customer/bookings/{id}
  Future<BookingModel> getBookingById(String bookingId) async {
    final res = await _apiService.get('${ApiEndpoints.customerBookings}/$bookingId');
    return BookingModel.fromJson(res);
  }

  /// Fetch available time slots for a specified date via GET /customer/bookings/slots?date=YYYY-MM-DD
  Future<AvailableSlotsModel> fetchAvailableSlots(String dateStr) async {
    final res = await _apiService.get(
      '${ApiEndpoints.customerBookings}/slots',
      params: {'date': dateStr},
    );
    return AvailableSlotsModel.fromJson(res);
  }

  /// Worker updates booking execution status via PUT /worker/bookings/{id}/status
  Future<BookingModel> updateWorkerBookingStatus(
    String bookingId,
    String newStatus, {
    String? notes,
  }) async {
    final body = <String, dynamic>{
      'status': newStatus,
    };
    if (notes != null && notes.trim().isNotEmpty) {
      body['notes'] = notes.trim();
    }
    final res = await _apiService.put(
      '/worker/bookings/$bookingId/status',
      body,
    );
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Get status details and next allowed transitions via GET /bookings/{id}/status
  Future<Map<String, dynamic>> getBookingStatus(String bookingId) async {
    final res = await _apiService.get('/bookings/$bookingId/status');
    return res as Map<String, dynamic>;
  }

  /// Fetch single assigned booking for worker via GET /worker/bookings/{id}
  Future<BookingModel> getWorkerBooking(String bookingId) async {
    final res = await _apiService.get('/worker/bookings/$bookingId');
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Worker starts travel via PUT /worker/bookings/{id}/start-travel
  Future<BookingModel> startTravel(String bookingId) async {
    final res = await _apiService.put('/worker/bookings/$bookingId/start-travel', {});
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Worker marks arrived via PUT /worker/bookings/{id}/arrive
  Future<BookingModel> markArrived(String bookingId) async {
    final res = await _apiService.put('/worker/bookings/$bookingId/arrive', {});
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Worker starts work via PUT /worker/bookings/{id}/start-work
  Future<BookingModel> startWork(String bookingId) async {
    final res = await _apiService.put('/worker/bookings/$bookingId/start-work', {});
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Worker completes work via PUT /worker/bookings/{id}/complete
  Future<BookingModel> completeWork(
    String bookingId, {
    String? notes,
    String? summary,
    List<String>? beforePhotos,
    List<String>? afterPhotos,
  }) async {
    final body = <String, dynamic>{
      'completion_notes': notes,
      'work_summary': summary,
      'before_photos': beforePhotos ?? [],
      'after_photos': afterPhotos ?? [],
    };
    final res = await _apiService.put('/worker/bookings/$bookingId/complete', body);
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Customer fetches completion review payload via GET /customer/bookings/{id}/completion
  Future<Map<String, dynamic>> getCompletionReview(String bookingId) async {
    final res = await _apiService.get('/customer/bookings/$bookingId/completion');
    return res as Map<String, dynamic>;
  }

  /// Customer confirms completion via PUT /customer/bookings/{id}/confirm
  Future<BookingModel> confirmCompletion(String bookingId, {String? notes}) async {
    final body = <String, dynamic>{};
    if (notes != null && notes.trim().isNotEmpty) {
      body['notes'] = notes.trim();
    }
    final res = await _apiService.put('/customer/bookings/$bookingId/confirm', body);
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Fetch paginated booking timeline audit events via GET /bookings/{id}/timeline
  Future<Map<String, dynamic>> getBookingTimeline(
    String bookingId, {
    int page = 1,
    int pageSize = 50,
  }) async {
    final res = await _apiService.get(
      '/bookings/$bookingId/timeline',
      params: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
      },
    );
    return res as Map<String, dynamic>;
  }

  /// Worker accepts an inspection visit request via POST /bookings/{id}/inspection/accept
  Future<BookingModel> acceptInspection(String bookingId) async {
    final res = await _apiService.post('/bookings/$bookingId/inspection/accept', {});
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Worker schedules inspection visit date/time via POST /bookings/{id}/inspection/schedule
  Future<BookingModel> scheduleInspection(String bookingId, DateTime scheduledAt) async {
    final res = await _apiService.post('/bookings/$bookingId/inspection/schedule', {
      'scheduled_at': scheduledAt.toUtc().toIso8601String(),
    });
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }

  /// Worker marks inspection visit as completed via POST /bookings/{id}/inspection/complete
  Future<BookingModel> completeInspection(String bookingId) async {
    final res = await _apiService.post('/bookings/$bookingId/inspection/complete', {});
    return BookingModel.fromJson(res as Map<String, dynamic>);
  }
}
