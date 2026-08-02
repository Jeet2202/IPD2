class ApiEndpoints {
  ApiEndpoints._();

  // ── Auth ──────────────────────────────────────────────
  static const String register                = '/auth/register';
  static const String login                   = '/auth/login';
  static const String verifyEmail             = '/auth/verify-email';
  static const String resendEmailOtp          = '/auth/resend-email-otp';
  static const String refreshToken            = '/auth/refresh';
  static const String logout                  = '/auth/logout';
  static const String logoutAll               = '/auth/logout-all';
  static const String me                      = '/auth/me';
  static const String forgotPassword          = '/auth/forgot-password';
  static const String verifyPasswordResetOtp  = '/auth/verify-password-reset-otp';
  static const String resetPassword           = '/auth/reset-password';
  static const String sessions                = '/auth/sessions';
  static const String changePassword          = '/auth/change-password';
  static const String deleteAccount           = '/auth/delete-account';

  // ── Customer ──────────────────────────────────────────
  static const String customerProfile       = '/customer/profile';
  static const String customerProfilePhoto  = '/customer/profile/photo';
  static const String customerAddresses     = '/customer/addresses';
  static const String customerBookings      = '/customer/bookings';
  static const String customerWallet        = '/customer/wallet';
  static const String customerNotifications = '/customer/notifications';

  // ── Services / Categories ─────────────────────────────
  static const String categories      = '/categories';
  static const String services        = '/services';
  static const String serviceDetail   = '/services/:id';

  // ── Bookings ──────────────────────────────────────────
  static const String bookings        = '/bookings';
  static const String bookingDetail   = '/bookings/:id';
  static const String cancelBooking   = '/bookings/:id/cancel';
  static const String rateBooking     = '/bookings/:id/rate';

  // ── Inspection ────────────────────────────────────────
  static const String inspections      = '/inspections';
  static const String inspectionDetail = '/inspections/:id';
  static const String inspectionReport = '/inspections/:id/report';
  static const String quotations       = '/inspections/:id/quotation';
  static const String approveQuotation = '/inspections/:id/approve';

  // ── Worker ────────────────────────────────────────────
  static const String workerProfile      = '/worker/profile';
  static const String workerProfilePhoto = '/worker/profile/photo';
  static const String workerJobs         = '/worker/jobs';
  static const String workerEarnings  = '/worker/earnings';
  static const String workerKyc       = '/worker/kyc';
  static const String workerWithdraw  = '/worker/withdraw';

  // ── Chat ──────────────────────────────────────────────
  static const String chatRooms       = '/chat/rooms';
  static const String chatMessages    = '/chat/rooms/:id/messages';

  // ── Admin ─────────────────────────────────────────────
  static const String adminStats      = '/admin/stats';
  static const String adminUsers      = '/admin/users';
  static const String adminWorkers    = '/admin/workers';
  static const String adminBookings   = '/admin/bookings';
  static const String adminPayments   = '/admin/payments';
}
