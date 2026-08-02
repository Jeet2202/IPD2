// File: lib/config/environment.dart

import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

enum AppEnvironment {
  development,
  staging,
  production,
}

class EnvironmentConfig {
  EnvironmentConfig._();

  static const String _environmentDefine = String.fromEnvironment(
    'ENVIRONMENT',
    defaultValue: '',
  );

  static const String _baseUrlDefine = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  static AppEnvironment _currentEnvironment = _resolveEnvironment(
    _environmentDefine.isNotEmpty
        ? _environmentDefine
        : (kReleaseMode ? 'production' : 'development'),
  );

  static Future<void> initialize({String? envFileName}) async {
    _currentEnvironment = _resolveEnvironment(
      _environmentDefine.isNotEmpty
          ? _environmentDefine
          : (kReleaseMode ? 'production' : 'development'),
    );

    final fileName = envFileName ?? _fileNameFor(_currentEnvironment);
    await dotenv.load(fileName: fileName);

    final fileEnvironment = dotenv.env['ENVIRONMENT'];
    if (_environmentDefine.isEmpty &&
        fileEnvironment != null &&
        fileEnvironment.trim().isNotEmpty) {
      _currentEnvironment = _resolveEnvironment(fileEnvironment);
    }

    _validateBaseUrl(baseUrl);
    debugPrint(
      'Loaded environment configuration: $environmentName ($fileName)',
    );
  }

  static AppEnvironment get currentEnvironment => _currentEnvironment;

  static String get baseUrl {
    final dartDefineUrl = _baseUrlDefine.trim();
    final dotenvUrl = (dotenv.env['API_BASE_URL'] ?? '').trim();
    final configuredUrl = dartDefineUrl.isNotEmpty ? dartDefineUrl : dotenvUrl;

    if (configuredUrl.isEmpty) {
      throw StateError(
        'API_BASE_URL is required. Set it in the active .env file or pass '
        '--dart-define=API_BASE_URL=<absolute-url>.',
      );
    }

    return _normalizeBaseUrl(configuredUrl);
  }

  static String get environmentName {
    switch (_currentEnvironment) {
      case AppEnvironment.development:
        return 'development';
      case AppEnvironment.staging:
        return 'staging';
      case AppEnvironment.production:
        return 'production';
    }
  }

  static bool get isProduction =>
      _currentEnvironment == AppEnvironment.production;

  static bool get isDevelopment =>
      _currentEnvironment == AppEnvironment.development;

  static AppEnvironment _resolveEnvironment(String value) {
    switch (value.trim().toLowerCase()) {
      case 'prod':
      case 'production':
        return AppEnvironment.production;
      case 'stage':
      case 'staging':
        return AppEnvironment.staging;
      case 'dev':
      case 'development':
      default:
        return AppEnvironment.development;
    }
  }

  static String _fileNameFor(AppEnvironment environment) {
    switch (environment) {
      case AppEnvironment.development:
        return '.env.development';
      case AppEnvironment.staging:
        return '.env.staging';
      case AppEnvironment.production:
        return '.env.production';
    }
  }

  static String _normalizeBaseUrl(String url) {
    var normalized = url.trim();
    while (normalized.endsWith('/')) {
      normalized = normalized.substring(0, normalized.length - 1);
    }
    return normalized;
  }

  static void _validateBaseUrl(String url) {
    final uri = Uri.tryParse(url);
    if (uri == null || !uri.hasScheme || uri.host.isEmpty) {
      throw StateError('API_BASE_URL must be an absolute URL. Received: $url');
    }

    final host = uri.host.toLowerCase();
    if (!kIsWeb &&
        defaultTargetPlatform == TargetPlatform.android &&
        (host == 'localhost' || host == '127.0.0.1')) {
      throw StateError(
        'Android cannot reach the backend through $host. Use your computer '
        'LAN IP for physical devices, or 10.0.2.2 for the Android emulator.',
      );
    }
  }
}
