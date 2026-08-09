// File: lib/services/job_application_service.dart

import '../models/job_application_model.dart';
import 'api_service.dart';

class JobApplicationService {
  JobApplicationService._();
  static final JobApplicationService instance = JobApplicationService._();

  Future<JobApplicationItem> applyForJob({
    required String bookingId,
    String? coverLetter,
    double? proposedPrice,
  }) async {
    final body = <String, dynamic>{
      'booking_id': bookingId,
    };
    if (coverLetter != null && coverLetter.trim().isNotEmpty) {
      body['cover_letter'] = coverLetter.trim();
    }
    if (proposedPrice != null) {
      body['proposed_price'] = proposedPrice;
    }

    final res = await ApiService.instance.post(
      '/worker/applications',
      body,
    );

    return JobApplicationItem.fromJson(res);
  }

  Future<JobApplicationPaginatedResult> fetchWorkerApplications({
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
    };
    if (status != null && status.isNotEmpty) {
      queryParams['status'] = status;
    }

    final res = await ApiService.instance.get(
      '/worker/applications',
      params: queryParams,
    );

    return JobApplicationPaginatedResult.fromJson(res);
  }

  Future<JobApplicationItem> fetchApplicationDetail(String applicationId) async {
    final res = await ApiService.instance.get('/worker/applications/$applicationId');
    return JobApplicationItem.fromJson(res);
  }

  /// Fetch all worker applicants for a customer's booking
  Future<Map<String, dynamic>> fetchBookingApplicants(String bookingId) async {
    final res = await ApiService.instance.get('/customer/bookings/$bookingId/applicants');
    return res as Map<String, dynamic>;
  }

  /// Accept a worker applicant for a customer's booking
  Future<Map<String, dynamic>> acceptApplicant(String bookingId, String applicationId) async {
    final res = await ApiService.instance.post('/customer/bookings/$bookingId/applicants/$applicationId/accept', {});
    return res as Map<String, dynamic>;
  }
}
