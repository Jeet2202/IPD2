import 'dart:convert';
import 'package:http/http.dart' as http;
import '../app/config/app_config.dart';
import '../constants/api_endpoints.dart';
import '../utils/token_storage.dart';

class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  final http.Client _client = http.Client();

  Map<String, String> get _headers => {
        'Content-Type':  'application/json',
        'Authorization': 'Bearer ${TokenStorage.accessToken}',
      };

  Uri _uri(String path, [Map<String, String>? params]) {
    final uri = Uri.parse('${AppConfig.baseUrl}$path');
    return params != null ? uri.replace(queryParameters: params) : uri;
  }

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, String>? params,
  }) async {
    final res = await _client
        .get(_uri(path, params), headers: _headers)
        .timeout(AppConfig.apiTimeout);
    return _handle(res);
  }

  Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body,
  ) async {
    final res = await _client
        .post(_uri(path), headers: _headers, body: jsonEncode(body))
        .timeout(AppConfig.apiTimeout);
    return _handle(res);
  }

  Future<Map<String, dynamic>> put(
    String path,
    Map<String, dynamic> body,
  ) async {
    final res = await _client
        .put(_uri(path), headers: _headers, body: jsonEncode(body))
        .timeout(AppConfig.apiTimeout);
    return _handle(res);
  }

  Future<Map<String, dynamic>> delete(String path) async {
    final res = await _client
        .delete(_uri(path), headers: _headers)
        .timeout(AppConfig.apiTimeout);
    return _handle(res);
  }

  Map<String, dynamic> _handle(http.Response res) {
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 200 && res.statusCode < 300) return body;
    throw ApiException(
      statusCode: res.statusCode,
      message:    body['message'] as String? ?? 'Unknown error',
    );
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;
  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
