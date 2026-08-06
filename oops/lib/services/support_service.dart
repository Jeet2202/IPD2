// File: lib/services/support_service.dart

import '../constants/api_endpoints.dart';
import '../models/support_model.dart';
import 'api_service.dart';

class SupportService {
  SupportService._();
  static final SupportService instance = SupportService._();

  final ApiService _apiService = ApiService.instance;

  /// Fetch FAQs
  Future<List<FAQModel>> fetchFAQs({
    String? category,
    bool popular = false,
    String? search,
  }) async {
    final params = <String, String>{};
    if (category != null && category.isNotEmpty) {
      params['category'] = category;
    }
    if (popular) {
      params['popular'] = 'true';
    }
    if (search != null && search.isNotEmpty) {
      params['search'] = search;
    }

    final res = await _apiService.get(
      ApiEndpoints.helpFaqs,
      params: params.isNotEmpty ? params : null,
    );

    if (res is List) {
      return res.map((e) => FAQModel.fromJson(e as Map<String, dynamic>)).toList();
    }
    return [];
  }

  /// Fetch Help Articles
  Future<List<HelpArticleModel>> fetchHelpArticles({
    String? category,
    String role = 'customer',
    String? search,
  }) async {
    final params = <String, String>{'role': role};
    if (category != null && category.isNotEmpty) {
      params['category'] = category;
    }
    if (search != null && search.isNotEmpty) {
      params['search'] = search;
    }

    final res = await _apiService.get(
      ApiEndpoints.helpArticles,
      params: params,
    );

    if (res is List) {
      return res
          .map((e) => HelpArticleModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  /// Fetch Support Categories
  Future<Map<String, List<String>>> fetchSupportCategories() async {
    final res = await _apiService.get(ApiEndpoints.helpCategories);
    if (res is Map<String, dynamic>) {
      return {
        'categories': (res['categories'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ??
            [],
        'faq_categories': (res['faq_categories'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ??
            [],
        'ticket_categories': (res['ticket_categories'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ??
            [],
      };
    }
    return {'categories': [], 'faq_categories': [], 'ticket_categories': []};
  }

  /// Fetch user support tickets
  Future<List<SupportTicketModel>> fetchUserTickets({
    String? status,
  }) async {
    final params = <String, String>{};
    if (status != null && status.isNotEmpty) {
      params['status'] = status;
    }

    final res = await _apiService.get(
      ApiEndpoints.supportTickets,
      params: params.isNotEmpty ? params : null,
    );

    if (res is List) {
      return res
          .map((e) => SupportTicketModel.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  /// Fetch single support ticket by ID
  Future<SupportTicketModel> fetchTicketById(String ticketId) async {
    final res = await _apiService.get('${ApiEndpoints.supportTickets}/$ticketId');
    return SupportTicketModel.fromJson(res as Map<String, dynamic>);
  }

  /// Create support ticket
  Future<SupportTicketModel> createTicket({
    required String subject,
    required String description,
    required String category,
    String priority = 'medium',
    String? bookingId,
    List<String> attachments = const [],
  }) async {
    final body = {
      'subject': subject,
      'description': description,
      'category': category,
      'priority': priority.toLowerCase(),
      if (bookingId != null && bookingId.isNotEmpty) 'booking_id': bookingId,
      if (attachments.isNotEmpty)
        'attachments': attachments.map((url) => {'url': url}).toList(),
    };

    final res = await _apiService.post(ApiEndpoints.supportTickets, body);
    return SupportTicketModel.fromJson(res as Map<String, dynamic>);
  }

  /// Reply to ticket (Customer to Admin thread)
  Future<SupportTicketModel> replyToTicket({
    required String ticketId,
    required String message,
    List<String> attachments = const [],
  }) async {
    final body = {
      'reply': {
        'message': message,
        if (attachments.isNotEmpty) 'attachments': attachments,
      }
    };

    final res = await _apiService.put('${ApiEndpoints.supportTickets}/$ticketId', body);
    return SupportTicketModel.fromJson(res as Map<String, dynamic>);
  }

  /// Fetch Contact Info
  Future<ContactInfoModel> fetchContactInfo() async {
    final res = await _apiService.get(ApiEndpoints.supportContact);
    return ContactInfoModel.fromJson(res as Map<String, dynamic>);
  }

  /// Fetch SOS Emergency Config
  Future<SOSConfigModel> fetchSOSConfig() async {
    final res = await _apiService.get(ApiEndpoints.supportSos);
    return SOSConfigModel.fromJson(res as Map<String, dynamic>);
  }

  /// Submit App Feedback
  Future<bool> submitFeedback({
    required String message,
    String category = 'app_feedback',
    int? rating,
  }) async {
    final body = {
      'message': message,
      'category': category,
      if (rating != null) 'rating': rating,
    };
    await _apiService.post(ApiEndpoints.supportFeedback, body);
    return true;
  }
}
