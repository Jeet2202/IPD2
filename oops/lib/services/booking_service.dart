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
}
