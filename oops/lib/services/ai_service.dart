// lib/services/ai_service.dart
//
// Ally AI Microservice client — Phase 5.1 to 5.6
// Covers: Recommendations, Search, Pricing, Assistant, Analytics

import 'dart:convert';
import 'package:http/http.dart' as http;

class AIServiceException implements Exception {
  final String message;
  final int? statusCode;
  const AIServiceException(this.message, {this.statusCode});
  @override
  String toString() => 'AIServiceException: $message';
}

class AIService {
  AIService._();
  static final AIService instance = AIService._();

  // AI service runs on a separate port from the main backend
  // For Android emulator use 10.0.2.2; for physical devices use your LAN IP
  static const String _baseUrl = 'http://192.168.29.147:8001';

  final _client = http.Client();

  Map<String, String> get _headers => {'Content-Type': 'application/json'};

  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    try {
      final res = await _client
          .post(Uri.parse('$_baseUrl$path'), headers: _headers, body: jsonEncode(body))
          .timeout(const Duration(seconds: 15));
      if (res.statusCode == 200) return jsonDecode(res.body) as Map<String, dynamic>;
      throw AIServiceException('HTTP ${res.statusCode}', statusCode: res.statusCode);
    } catch (e) {
      if (e is AIServiceException) rethrow;
      throw AIServiceException(e.toString());
    }
  }

  Future<dynamic> _get(String path) async {
    try {
      final res = await _client
          .get(Uri.parse('$_baseUrl$path'), headers: _headers)
          .timeout(const Duration(seconds: 15));
      if (res.statusCode == 200) return jsonDecode(res.body);
      throw AIServiceException('HTTP ${res.statusCode}', statusCode: res.statusCode);
    } catch (e) {
      if (e is AIServiceException) rethrow;
      throw AIServiceException(e.toString());
    }
  }

  // ─── Phase 5.1 — Health ──────────────────────────────────────────────────
  Future<Map<String, dynamic>> health() => _get('/health') as Future<Map<String, dynamic>>;

  // ─── Phase 5.2 — Recommendations ────────────────────────────────────────
  Future<Map<String, dynamic>> getWorkerRecommendations({
    required String bookingId,
    int maxResults = 5,
  }) =>
      _post('/recommendations/workers', {
        'booking_id': bookingId,
        'max_results': maxResults,
      });

  // ─── Phase 5.3 — Search ──────────────────────────────────────────────────
  Future<Map<String, dynamic>> search({
    required String query,
    String? categoryId,
    double? maxPrice,
    double? minRating,
    String? city,
    bool? isVerified,
    int page = 1,
    int pageSize = 10,
  }) =>
      _post('/search', {
        'query': query,
        if (categoryId != null || maxPrice != null || minRating != null || city != null || isVerified != null)
          'filters': {
            if (categoryId != null) 'category_id': categoryId,
            if (maxPrice != null) 'max_price': maxPrice,
            if (minRating != null) 'min_rating': minRating,
            if (city != null) 'city': city,
            if (isVerified != null) 'is_verified': isVerified,
          },
        'page': page,
        'page_size': pageSize,
      });

  Future<List<dynamic>> getSearchSuggestions(String q) async {
    final data = await _get('/search/suggestions?q=${Uri.encodeComponent(q)}');
    return data is List ? data : [];
  }

  Future<List<String>> getTrending() async {
    final data = await _get('/search/trending');
    return (data as List).cast<String>();
  }

  // ─── Phase 5.4 — Pricing ─────────────────────────────────────────────────
  Future<Map<String, dynamic>> getPriceEstimate({
    required String bookingId,
    required String city,
    double estimatedDurationHours = 1.0,
    String urgencyLevel = 'normal',
    String complexityLevel = 'standard',
    String? locality,
    String? bookingNotes,
  }) =>
      _post('/pricing/estimate', {
        'booking_id': bookingId,
        'city': city,
        'estimated_duration_hours': estimatedDurationHours,
        'urgency_level': urgencyLevel,
        'complexity_level': complexityLevel,
        if (locality != null) 'locality': locality,
        if (bookingNotes != null) 'booking_notes': bookingNotes,
      });

  // ─── Phase 5.5 — AI Assistant ────────────────────────────────────────────
  Future<Map<String, dynamic>> chat({
    required String message,
    required String role, // 'customer' | 'worker' | 'admin'
    String? sessionId,
    String? userId,
    String? workerId,
    String? authToken,
  }) =>
      _post('/assistant/chat', {
        'message': message,
        'role': role,
        if (sessionId != null) 'session_id': sessionId,
        if (userId != null) 'user_id': userId,
        if (workerId != null) 'worker_id': workerId,
        if (authToken != null) 'auth_token': authToken,
      });
}
