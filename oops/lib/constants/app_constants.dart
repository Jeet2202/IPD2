class AppConstants {
  AppConstants._();

  // Shared Preferences / SecureStorage Keys
  static const String keyAccessToken    = 'access_token';
  static const String keyRefreshToken   = 'refresh_token';
  static const String keyUserId         = 'user_id';
  static const String keyUserRole       = 'user_role';
  static const String keyIsOnboarded    = 'is_onboarded';
  static const String keyFcmToken       = 'fcm_token';
  static const String keyLanguage       = 'language';

  // User Roles
  static const String roleCustomer      = 'customer';
  static const String roleWorker        = 'worker';
  static const String roleAdmin         = 'admin';

  // Booking Status
  static const String statusPending     = 'pending';
  static const String statusAccepted    = 'accepted';
  static const String statusOnWay       = 'on_way';
  static const String statusInProgress  = 'in_progress';
  static const String statusCompleted   = 'completed';
  static const String statusCancelled   = 'cancelled';

  // Payment Methods
  static const String paymentCash       = 'cash';
  static const String paymentCard       = 'card';
  static const String paymentWallet     = 'wallet';
  static const String paymentUpi        = 'upi';

  // Regex
  static final RegExp emailRegex  = RegExp(r'^[\w.+-]+@[\w-]+\.[a-z]{2,}$');
  static final RegExp phoneRegex  = RegExp(r'^[6-9]\d{9}$');
  static final RegExp pinRegex    = RegExp(r'^\d{6}$');
}
