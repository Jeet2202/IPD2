// File: lib/config/app_config.dart

import 'environment.dart';

class AppConfig {
  AppConfig._();

  static const String appName = 'KaamSetu';
  static const String appVersion = '1.0.0';

  /// Centralized API Base URL obtained from EnvironmentConfig / flutter_dotenv
  static String get baseUrl => EnvironmentConfig.baseUrl;

  static const Duration apiTimeout = Duration(seconds: 30);

  // Map Defaults
  static const double defaultLat = 20.5937;
  static const double defaultLng = 78.9629;
  static const double defaultZoom = 13.0;

  // Pagination Defaults
  static const int defaultPageSize = 20;

  // OTP Config
  static const int otpLength = 6;
  static const int otpResendSeconds = 60;

  // Search Config
  static const Duration searchDebounce = Duration(milliseconds: 400);

  // Misc Config
  static const int splashDurationMs = 2500;
  static const double minBookingDistance = 50.0; // km
}
