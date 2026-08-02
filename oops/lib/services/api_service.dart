import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../config/app_config.dart';
import '../config/environment.dart';
import '../models/category_model.dart';
import '../models/home_model.dart';
import '../models/category_model.dart';
import '../utils/token_storage.dart';

MediaType _determineMediaType(String filePath) {
  final ext = filePath.toLowerCase();
  if (ext.endsWith('.png')) {
    return MediaType('image', 'png');
  } else if (ext.endsWith('.webp')) {
    return MediaType('image', 'webp');
  } else if (ext.endsWith('.jpg') || ext.endsWith('.jpeg')) {
    return MediaType('image', 'jpeg');
  }
  return MediaType('image', 'jpeg');
}

class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  final http.Client _client = http.Client();

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${TokenStorage.accessToken}',
      };

  Uri _uri(String path, [Map<String, String>? params]) {
    final uri = Uri.parse('${EnvironmentConfig.baseUrl}$path');
    return params != null ? uri.replace(queryParameters: params) : uri;
  }

  Future<bool> _tryRefresh() async {
    if (TokenStorage.refreshToken.isEmpty) return false;
    try {
      final res = await _client.post(
        _uri('/auth/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh_token': TokenStorage.refreshToken}),
      ).timeout(AppConfig.apiTimeout);

      if (res.statusCode >= 200 && res.statusCode < 300) {
        final body = jsonDecode(res.body) as Map<String, dynamic>;
        final data = body['data'] as Map<String, dynamic>;
        TokenStorage.save(
          access: data['access_token'] as String,
          refresh: data['refresh_token'] as String,
        );
        return true;
      }
    } catch (_) {}
    TokenStorage.clear();
    return false;
  }

  Future<Map<String, dynamic>> _send(
    String method,
    String path,
    Future<http.Response> Function(Uri uri) request, {
    Map<String, String>? params,
  }) async {
    final uri = _uri(path, params);
    final stopwatch = Stopwatch()..start();

    try {
      var res = await request(uri).timeout(AppConfig.apiTimeout);
      _logTiming(method, uri, stopwatch, statusCode: res.statusCode);

      // Automatic Refresh Token Interceptor for HTTP 401 Unauthorized
      if (res.statusCode == 401 &&
          !path.contains('/auth/login') &&
          !path.contains('/auth/refresh') &&
          !path.contains('/auth/register')) {
        final refreshed = await _tryRefresh();
        if (refreshed) {
          // Retry original request with new access token
          res = await request(uri).timeout(AppConfig.apiTimeout);
          _logTiming(method, uri, stopwatch, statusCode: res.statusCode);
        }
      }

      return _handle(res);
    } on TimeoutException {
      _logTiming(method, uri, stopwatch, error: 'TimeoutException');
      throw ApiException(
        statusCode: 408,
        message: 'Network request timed out. Please check your internet connection and try again.',
        errorCode: 'NETWORK_TIMEOUT',
      );
    } on SocketException catch (e) {
      _logTiming(method, uri, stopwatch, error: e);
      throw ApiException(
        statusCode: 503,
        message: 'Server is unavailable or unreachable. Please check your network connection.',
        errorCode: 'SERVER_UNAVAILABLE',
      );
    } on ApiException {
      rethrow;
    } catch (error) {
      _logTiming(method, uri, stopwatch, error: error);
      throw ApiException(
        statusCode: 500,
        message: 'An unexpected network error occurred: $error',
        errorCode: 'UNEXPECTED_ERROR',
      );
    }
  }

  void _logTiming(
    String method,
    Uri uri,
    Stopwatch stopwatch, {
    int? statusCode,
    Object? error,
  }) {
    stopwatch.stop();
    if (!kDebugMode) return;

    final status = statusCode != null ? 'status=$statusCode' : 'error=$error';
    debugPrint(
      'HTTP $method ${uri.path} completed in ${stopwatch.elapsedMilliseconds}ms ($status)',
    );
  }

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, String>? params,
  }) async {
    return _send(
      'GET',
      path,
      (uri) => _client.get(uri, headers: _headers),
      params: params,
    );
  }

  Future<HomeModel> getHomeData() async {
    final res = await get('/home');
    return HomeModel.fromJson(res);
  }

  Future<Map<String, dynamic>> getCategoryServices(
    String categoryId, {
    int page = 1,
    int limit = 10,
    String sortBy = 'display_order',
    bool? isFeatured,
    double? minPrice,
    double? maxPrice,
    int? maxDuration,
  }) async {
    final params = <String, String>{
      'page': page.toString(),
      'limit': limit.toString(),
      'sort_by': sortBy,
    };
    if (isFeatured != null) params['is_featured'] = isFeatured.toString();
    if (minPrice != null) params['min_price'] = minPrice.toString();
    if (maxPrice != null) params['max_price'] = maxPrice.toString();
    if (maxDuration != null) params['max_duration'] = maxDuration.toString();

    return get(
      '/categories/$categoryId/services',
      params: params,
    );
  }

  Future<CategoryModel> getCategoryById(String categoryId) async {
    final res = await get('/categories/$categoryId');
    return CategoryModel.fromJson(res);
  }

  Future<Map<String, dynamic>> fetchServices({
    int page = 1,
    int limit = 10,
    String? categoryId,
    bool? isFeatured,
    double? minPrice,
    double? maxPrice,
    int? maxDuration,
    String? search,
    String sortBy = 'display_order',
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
      'limit': limit.toString(),
      'sort_by': sortBy,
    };
    if (categoryId != null && categoryId.isNotEmpty) {
      queryParams['category_id'] = categoryId;
    }
    if (isFeatured != null) {
      queryParams['is_featured'] = isFeatured.toString();
    }
    if (minPrice != null) {
      queryParams['min_price'] = minPrice.toString();
    }
    if (maxPrice != null) {
      queryParams['max_price'] = maxPrice.toString();
    }
    if (maxDuration != null) {
      queryParams['max_duration'] = maxDuration.toString();
    }
    if (search != null && search.isNotEmpty) {
      queryParams['search'] = search;
    }

    final queryString = Uri(queryParameters: queryParams).query;
    return get('/services?$queryString');
  }

  Future<Map<String, dynamic>> getServiceById(String serviceId) async {
    return get('/services/$serviceId');
  }

  Future<Map<String, dynamic>> searchServices({
    String? query,
    int page = 1,
    int pageSize = 10,
    String? category,
    bool? featured,
    double? minPrice,
    double? maxPrice,
    int? maxDuration,
    String sortBy = 'relevance',
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
      'sort_by': sortBy,
    };
    if (query != null && query.isNotEmpty) {
      queryParams['query'] = query;
    }
    if (category != null && category.isNotEmpty) {
      queryParams['category'] = category;
    }
    if (featured != null) {
      queryParams['featured'] = featured.toString();
    }
    if (minPrice != null) {
      queryParams['min_price'] = minPrice.toString();
    }
    if (maxPrice != null) {
      queryParams['max_price'] = maxPrice.toString();
    }
    if (maxDuration != null) {
      queryParams['max_duration'] = maxDuration.toString();
    }

    final queryString = Uri(queryParameters: queryParams).query;
    return get('/services/search?$queryString');
  }

  Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body,
  ) async {
    return _send(
      'POST',
      path,
      (uri) => _client.post(uri, headers: _headers, body: jsonEncode(body)),
    );
  }

  Future<Map<String, dynamic>> put(
    String path,
    Map<String, dynamic> body,
  ) async {
    return _send(
      'PUT',
      path,
      (uri) => _client.put(uri, headers: _headers, body: jsonEncode(body)),
    );
  }

  Future<Map<String, dynamic>> delete(String path, {Map<String, dynamic>? body}) async {
    return _send(
      'DELETE',
      path,
      (uri) => _client.delete(uri, headers: _headers, body: body != null ? jsonEncode(body) : null),
    );
  }

  Future<Map<String, dynamic>> uploadMultipart(
    String path,
    String filePath, {
    String fileField = 'file',
  }) async {
    final uri = _uri(path);
    final stopwatch = Stopwatch()..start();

    try {
      var request = http.MultipartRequest('POST', uri);
      request.headers.addAll({
        'Authorization': 'Bearer ${TokenStorage.accessToken}',
      });

      final file = await http.MultipartFile.fromPath(
        fileField,
        filePath,
        contentType: _determineMediaType(filePath),
      );
      request.files.add(file);

      final streamedRes = await request.send().timeout(AppConfig.apiTimeout);
      final res = await http.Response.fromStream(streamedRes);
      _logTiming('POST (Multipart)', uri, stopwatch, statusCode: res.statusCode);

      if (res.statusCode == 401) {
        final refreshed = await _tryRefresh();
        if (refreshed) {
          var retryRequest = http.MultipartRequest('POST', uri);
          retryRequest.headers.addAll({
            'Authorization': 'Bearer ${TokenStorage.accessToken}',
          });
          final retryFile = await http.MultipartFile.fromPath(
            fileField,
            filePath,
            contentType: _determineMediaType(filePath),
          );
          retryRequest.files.add(retryFile);
          final retryStreamed = await retryRequest.send().timeout(AppConfig.apiTimeout);
          final retryRes = await http.Response.fromStream(retryStreamed);
          _logTiming('POST (Multipart Retry)', uri, stopwatch, statusCode: retryRes.statusCode);
          return _handle(retryRes);
        }
      }

      return _handle(res);
    } on TimeoutException {
      _logTiming('POST (Multipart)', uri, stopwatch, error: 'TimeoutException');
      throw ApiException(
        statusCode: 408,
        message: 'Image upload timed out. Please check your internet connection.',
        errorCode: 'NETWORK_TIMEOUT',
      );
    } on SocketException catch (e) {
      _logTiming('POST (Multipart)', uri, stopwatch, error: e);
      throw ApiException(
        statusCode: 503,
        message: 'Server is unavailable. Please check your network connection.',
        errorCode: 'SERVER_UNAVAILABLE',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      _logTiming('POST (Multipart)', uri, stopwatch, error: e);
      throw ApiException(
        statusCode: 500,
        message: 'Image upload failed: $e',
        errorCode: 'UPLOAD_ERROR',
      );
    }
  }

  Map<String, dynamic> _handle(http.Response res) {
    Map<String, dynamic> body = {};
    try {
      if (res.body.isNotEmpty) {
        final decoded = jsonDecode(res.body);
        if (decoded is Map<String, dynamic>) {
          body = decoded;
        }
      }
    } catch (_) {
      // Response body is not valid JSON
    }

    if (res.statusCode >= 200 && res.statusCode < 300) return body;

    throw ApiException.fromResponse(statusCode: res.statusCode, body: body);
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  final String? errorCode;
  final List<String>? details;
  final Map<String, String> fieldErrors;

  ApiException({
    required this.statusCode,
    required this.message,
    this.errorCode,
    this.details,
    this.fieldErrors = const {},
  });

  factory ApiException.fromResponse({
    required int statusCode,
    required Map<String, dynamic> body,
  }) {
    String? errorCode = body['error_code'] as String?;
    String message = body['message'] as String? ?? 'An unexpected error occurred';
    List<String>? details;
    if (body['details'] is List) {
      details = (body['details'] as List).map((e) => e.toString()).toList();
    }

    Map<String, String> fieldErrors = {};

    // 1. Parse FastAPI 422 Unprocessable Entity detail array
    if (statusCode == 422 && body['detail'] is List) {
      final detailList = body['detail'] as List;
      for (final item in detailList) {
        if (item is Map<String, dynamic>) {
          final loc = item['loc'] as List?;
          final msg = item['msg'] as String? ?? 'Invalid field';
          if (loc != null && loc.isNotEmpty) {
            final fieldName = loc.last.toString();
            fieldErrors[fieldName] = _cleanFieldErrorMessage(fieldName, msg);
          }
        }
      }
      message = 'Please correct the highlighted errors below.';
    }

    // 2. Map known error codes to field errors and friendly messages
    if (errorCode == 'EMAIL_ALREADY_EXISTS') {
      message = 'An account with this email address already exists.';
      fieldErrors['email'] = message;
    } else if (errorCode == 'PHONE_ALREADY_EXISTS') {
      message = 'An account with this phone number already exists.';
      fieldErrors['phone'] = message;
    } else if (errorCode == 'INVALID_CREDENTIALS') {
      message = 'Invalid email/phone or password.';
    } else if (errorCode == 'EMAIL_NOT_VERIFIED') {
      message = 'Your email address has not been verified yet.';
    } else if (errorCode == 'OTP_EXPIRED') {
      message = 'Verification code has expired. Please request a new code.';
    } else if (errorCode == 'OTP_INVALID' || errorCode == 'INVALID_OTP') {
      message = 'Invalid verification code. Please check and try again.';
    } else if (errorCode == 'OTP_MAX_ATTEMPTS_EXCEEDED') {
      message = 'Maximum OTP verification attempts reached. Please request a new code.';
    } else if (errorCode == 'ACCOUNT_LOCKED') {
      message = body['message'] as String? ?? 'Account is temporarily locked. Please try again later.';
    }

    return ApiException(
      statusCode: statusCode,
      message: message,
      errorCode: errorCode,
      details: details,
      fieldErrors: fieldErrors,
    );
  }

  static String _cleanFieldErrorMessage(String field, String rawMsg) {
    if (rawMsg.contains("pattern mismatch") || rawMsg.contains("match pattern")) {
      if (field == 'phone') return 'Please enter a valid phone number';
      if (field == 'email') return 'Please enter a valid email address';
    }
    return rawMsg;
  }

  @override
  String toString() => 'ApiException($statusCode, $errorCode): $message';
}
