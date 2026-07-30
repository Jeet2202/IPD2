class AppConfig {
  AppConfig._();

  static const String appName    = 'HireMe';
  static const String appVersion = '1.0.0';

  // API
  static const String baseUrl         = 'https://api.hireme.com/v1';
  static const Duration apiTimeout    = Duration(seconds: 30);

  // Map
  static const double defaultLat      = 20.5937;
  static const double defaultLng      = 78.9629;
  static const double defaultZoom     = 13.0;

  // Pagination
  static const int defaultPageSize    = 20;

  // OTP
  static const int otpLength          = 6;
  static const int otpResendSeconds   = 60;

  // Search
  static const Duration searchDebounce = Duration(milliseconds: 400);

  // Misc
  static const int splashDurationMs  = 2500;
  static const double minBookingDistance = 50.0; // km
}
