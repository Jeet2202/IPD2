class AppRoutes {
  AppRoutes._();

  // ── Customer ──────────────────────────────────────────
  static const String customerSplash        = '/customer/splash';
  static const String customerOnboarding    = '/customer/onboarding';

  // Auth
  static const String customerLogin         = '/customer/auth/login';
  static const String customerRegister      = '/customer/auth/register';
  static const String customerOtp           = '/customer/auth/otp';
  static const String customerForgotPwd     = '/customer/auth/forgot-password';
  static const String customerCompleteProfile = '/customer/auth/complete-profile';
  static const String customerLocationPerm  = '/customer/auth/location-permission';

  // Main
  static const String customerHome          = '/customer/home';
  static const String customerSearch        = '/customer/search';
  static const String customerCategories    = '/customer/categories';
  static const String customerServices      = '/customer/services';

  // Normal Booking
  static const String serviceSelection      = '/customer/booking/service-selection';
  static const String bookingDetails        = '/customer/booking/details';
  static const String bookingAddress        = '/customer/booking/address';
  static const String bookingSchedule       = '/customer/booking/schedule';
  static const String priceEstimation       = '/customer/booking/price-estimation';
  static const String bookingSummary        = '/customer/booking/summary';
  static const String searchingWorker       = '/customer/booking/searching-worker';
  static const String workerAssigned        = '/customer/booking/worker-assigned';
  static const String liveTracking          = '/customer/booking/live-tracking';
  static const String workInProgress        = '/customer/booking/work-in-progress';
  static const String bookingPayment        = '/customer/booking/payment';
  static const String bookingReview         = '/customer/booking/review';

  // Inspection Booking
  static const String inspectionIntro       = '/customer/inspection/intro';
  static const String problemDetails        = '/customer/inspection/problem-details';
  static const String uploadImages          = '/customer/inspection/upload-images';
  static const String inspectionAddress     = '/customer/inspection/address';
  static const String inspectionSchedule    = '/customer/inspection/schedule';
  static const String inspectionSummary     = '/customer/inspection/summary';
  static const String searchingProfessional = '/customer/inspection/searching-professional';
  static const String professionalAssigned  = '/customer/inspection/professional-assigned';
  static const String inspectionTracking    = '/customer/inspection/tracking';
  static const String inspectionInProgress  = '/customer/inspection/in-progress';
  static const String inspectionReport      = '/customer/inspection/report';
  static const String quotation             = '/customer/inspection/quotation';
  static const String priceComparison       = '/customer/inspection/price-comparison';
  static const String quotationReview       = '/customer/inspection/quotation-review';
  static const String quotationDecision     = '/customer/inspection/quotation-decision';
  static const String negotiationChat       = '/customer/inspection/negotiation-chat';
  static const String revisedQuotation      = '/customer/inspection/revised-quotation';
  static const String repairConfirmation     = '/customer/inspection/repair-confirmation';
  static const String repairTracking         = '/customer/inspection/repair-tracking';
  static const String inspectionCompleted    = '/customer/inspection/completed';

  // Bookings Management
  static const String customerBookings      = '/customer/bookings';
  static const String myBookings            = '/customer/bookings/my-bookings';
  static const String rescheduleBooking     = '/customer/bookings/reschedule';
  static const String cancelBooking         = '/customer/bookings/cancel';
  static const String bookingHistory        = '/customer/bookings/history';

  // Profile & Wallet
  static const String customerProfile       = '/customer/profile';
  static const String editProfile           = '/customer/profile/edit';
  static const String savedAddresses        = '/customer/profile/saved-addresses';
  static const String paymentMethods        = '/customer/profile/payment-methods';
  static const String customerWallet        = '/customer/wallet';

  // Engagement & Support
  static const String notifications         = '/customer/notifications';
  static const String offers                = '/customer/offers';
  static const String referAndEarn          = '/customer/refer-and-earn';
  static const String favoriteProfessionals  = '/customer/favorites';
  static const String recentlyViewed        = '/customer/recently-viewed';

  // Help & Settings
  static const String customerSupport       = '/customer/support';
  static const String helpSupport           = '/customer/support/help';
  static const String liveChat              = '/customer/support/live-chat';
  static const String raiseComplaint        = '/customer/support/raise-complaint';
  static const String customerSettings      = '/customer/settings';
  static const String privacyPolicy         = '/customer/legal/privacy-policy';
  static const String termsConditions        = '/customer/legal/terms-conditions';
  static const String aboutUs               = '/customer/about';
  static const String noInternet            = '/customer/system/no-internet';
  static const String systemStatus          = '/customer/system/status';

  // Other Customer
  static const String customerChat          = '/customer/chat';
  static const String customerReviews       = '/customer/reviews';

  // ── Worker ────────────────────────────────────────────
  static const String workerSplash          = '/worker/splash';
  static const String workerAuth            = '/worker/auth';
  static const String workerKyc             = '/worker/kyc';
  static const String workerDashboard       = '/worker/dashboard';
  static const String workerIncomingJobs    = '/worker/incoming-jobs';
  static const String workerInspectionReqs  = '/worker/inspection-requests';
  static const String workerActiveJobs      = '/worker/active-jobs';
  static const String workerCompletedJobs   = '/worker/completed-jobs';
  static const String workerInspectionReport = '/worker/inspection-report';
  static const String workerEarnings        = '/worker/earnings';
  static const String workerWithdrawals     = '/worker/withdrawals';
  static const String workerWallet          = '/worker/wallet';
  static const String workerRatings         = '/worker/ratings';
  static const String workerNotifications   = '/worker/notifications';
  static const String workerChat            = '/worker/chat';
  static const String workerProfile         = '/worker/profile';
  static const String workerDocuments       = '/worker/documents';
  static const String workerSupport         = '/worker/support';
  static const String workerSettings        = '/worker/settings';

  // ── Admin ─────────────────────────────────────────────
  static const String adminAuth             = '/admin/auth';
  static const String adminDashboard        = '/admin/dashboard';
  static const String adminCustomers        = '/admin/customers';
  static const String adminWorkers          = '/admin/workers';
  static const String adminCategories       = '/admin/categories';
  static const String adminServices         = '/admin/services';
  static const String adminBookings         = '/admin/bookings';
  static const String adminInspections      = '/admin/inspections';
  static const String adminQuotations       = '/admin/quotations';
  static const String adminPayments         = '/admin/payments';
  static const String adminDisputes         = '/admin/disputes';
  static const String adminNotifications    = '/admin/notifications';
  static const String adminAnalytics        = '/admin/analytics';
  static const String adminReports          = '/admin/reports';
  static const String adminCms              = '/admin/cms';
  static const String adminSettings         = '/admin/settings';
}
