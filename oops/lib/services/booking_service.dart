import '../models/booking_model.dart';
import '../constants/api_endpoints.dart';
import 'api_service.dart';

class BookingService {
  BookingService._();
  static final BookingService instance = BookingService._();

  Future<List<BookingModel>> getBookings({String? status}) async {
    final params = status != null ? {'status': status} : null;
    final res = await ApiService.instance.get(ApiEndpoints.bookings, params: params);
    final list = res['bookings'] as List;
    return list.map((e) => BookingModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<BookingModel> getBookingById(String id) async {
    final res = await ApiService.instance.get(ApiEndpoints.bookingDetail.replaceFirst(':id', id));
    return BookingModel.fromJson(res['booking'] as Map<String, dynamic>);
  }

  Future<BookingModel> createBooking(Map<String, dynamic> payload) async {
    final res = await ApiService.instance.post(ApiEndpoints.bookings, payload);
    return BookingModel.fromJson(res['booking'] as Map<String, dynamic>);
  }

  Future<void> cancelBooking(String id, {String? reason}) async {
    await ApiService.instance.post(
      ApiEndpoints.cancelBooking.replaceFirst(':id', id),
      {'reason': reason ?? ''},
    );
  }

  Future<void> rateBooking(String id, {required double rating, String? review}) async {
    await ApiService.instance.post(
      ApiEndpoints.rateBooking.replaceFirst(':id', id),
      {'rating': rating, 'review': review ?? ''},
    );
  }
}
