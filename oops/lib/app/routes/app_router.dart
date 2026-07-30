import 'package:flutter/material.dart';

import 'app_routes.dart';

// ── Screen imports ─────────────────────────────────────────────────────────────
import '../../customer/splash/splash_screen.dart';
import '../../customer/onboarding/onboarding_screen1.dart';
import '../../customer/onboarding/onboarding_screen2.dart';
import '../../customer/onboarding/onboarding_screen3.dart';
import '../../customer/authentication/login/login_screen.dart';
import '../../customer/authentication/register/register_screen.dart';
import '../../customer/authentication/otp/otp_screen.dart';
import '../../customer/authentication/complete_profile/complete_profile_screen.dart';
import '../../customer/authentication/location_permission/location_permission_screen.dart';
import '../../customer/home/home_screen.dart';
import '../../customer/search/search_screen.dart';
import '../../customer/categories/category_screen.dart';
import '../../customer/services/service_details_screen.dart';
import '../../customer/services/service_faq_screen.dart';
import '../../customer/address/select_address_screen.dart';
import '../../customer/chat/chat_screen.dart';
import '../../customer/payment/payment_screen.dart';
import '../../customer/payment/invoice_screen.dart';
import '../../customer/reviews/review_screen.dart';
import '../../customer/normal_booking/service_selection/service_selection_screen.dart';
import '../../customer/normal_booking/booking_details/booking_details_screen.dart';
import '../../customer/normal_booking/schedule/schedule_screen.dart';
import '../../customer/normal_booking/price_estimation/price_estimation_screen.dart';
import '../../customer/normal_booking/booking_summary/booking_summary_screen.dart';
import '../../customer/normal_booking/searching_worker/searching_worker_screen.dart';
import '../../customer/normal_booking/worker_assigned/worker_assigned_screen.dart';
import '../../customer/normal_booking/live_tracking/live_tracking_screen.dart';
import '../../customer/normal_booking/booking_status/booking_status_screen.dart';
import '../../customer/normal_booking/work_in_progress/work_in_progress_screen.dart';
import '../../customer/normal_booking/work_completed/work_completed_screen.dart';

// Inspection Booking Imports
import '../../customer/inspection_booking/inspection_intro/inspection_intro_screen.dart';
import '../../customer/inspection_booking/inspection_details/inspection_details_screen.dart';
import '../../customer/inspection_booking/inspection_schedule/inspection_schedule_screen.dart';
import '../../customer/inspection_booking/inspector_assigned/inspector_assigned_screen.dart';
import '../../customer/inspection_booking/live_inspection_tracking/live_inspection_tracking_screen.dart';
import '../../customer/inspection_booking/inspection_in_progress/inspection_in_progress_screen.dart';
import '../../customer/inspection_booking/inspection_report/inspection_report_screen.dart';
import '../../customer/inspection_booking/market_price_comparison/market_price_comparison_screen.dart';
import '../../customer/inspection_booking/quotation_review/quotation_review_screen.dart';
import '../../customer/inspection_booking/quotation_decision/quotation_decision_screen.dart';
import '../../customer/inspection_booking/negotiation_chat/negotiation_chat_screen.dart';
import '../../customer/inspection_booking/revised_quotation/revised_quotation_screen.dart';
import '../../customer/inspection_booking/repair_confirmation/repair_confirmation_screen.dart';
import '../../customer/inspection_booking/repair_tracking/repair_tracking_screen.dart';
import '../../customer/inspection_booking/inspection_booking_completed/inspection_booking_completed_screen.dart';

// Bookings Management Imports
import '../../customer/bookings/my_bookings/my_bookings_screen.dart';
import '../../customer/bookings/reschedule_booking/reschedule_booking_screen.dart';
import '../../customer/bookings/cancel_booking/cancel_booking_screen.dart';
import '../../customer/bookings/booking_history/booking_history_screen.dart';

// Profile & Wallet Imports
import '../../customer/profile/profile_screen.dart';
import '../../customer/profile/edit_profile/edit_profile_screen.dart';
import '../../customer/profile/saved_addresses/saved_addresses_screen.dart';
import '../../customer/profile/payment_methods/payment_methods_screen.dart';
import '../../customer/profile/wallet/wallet_screen.dart';

// Engagement & Retention Imports
import '../../customer/notifications/notifications_screen.dart';
import '../../customer/offers/offers_screen.dart';
import '../../customer/refer_earn/refer_earn_screen.dart';
import '../../customer/favorites/favorite_professionals_screen.dart';
import '../../customer/recently_viewed/recently_viewed_screen.dart';

// Support & Settings Imports
import '../../customer/support/help_support/help_support_screen.dart';
import '../../customer/support/live_chat/live_chat_screen.dart';
import '../../customer/support/raise_complaint/raise_complaint_screen.dart';
import '../../customer/settings/settings_screen.dart';
import '../../customer/settings/privacy_security/privacy_security_screen.dart';

// About & Legal & System Imports
import '../../customer/about/about_screen.dart';
import '../../customer/legal/terms_conditions/terms_conditions_screen.dart';
import '../../customer/legal/privacy_policy/privacy_policy_screen.dart';
import '../../customer/system/no_internet/no_internet_screen.dart';
import '../../customer/system/system_status/system_status_screen.dart';

class AppRouter {
  AppRouter._();

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {

      // ── Splash ──────────────────────────────────────────────────────────────
      case AppRoutes.customerSplash:
        return _build(const SplashScreen(), settings);

      // ── Onboarding ──────────────────────────────────────────────────────────
      case AppRoutes.customerOnboarding:
      case '/customer/onboarding/1':
        return _build(const OnboardingPage1(), settings);

      case '/customer/onboarding/2':
        return _build(const OnboardingPage2(), settings);

      case '/customer/onboarding/3':
        return _build(const OnboardingPage3(), settings);

      // ── Auth ────────────────────────────────────────────────────────────────
      case AppRoutes.customerLogin:
        return _build(const LoginScreen(), settings);

      case AppRoutes.customerRegister:
        return _build(const RegisterScreen(), settings);

      case AppRoutes.customerOtp:
        return _build(const OtpScreen(), settings);

      case AppRoutes.customerCompleteProfile:
        return _build(const CompleteProfileScreen(), settings);

      case AppRoutes.customerLocationPerm:
        return _build(const LocationPermissionScreen(), settings);

      // ── Main & Search ───────────────────────────────────────────────────────
      case AppRoutes.customerHome:
        return _build(const HomeScreen(), settings);

      case AppRoutes.customerSearch:
        return _build(const SearchScreen(), settings);

      case AppRoutes.customerCategories:
        return _build(const CategoryScreen(), settings);

      case AppRoutes.customerServices:
        return _build(const ServiceDetailsScreen(), settings);

      case '/customer/services/faq':
        return _build(const ServiceFaqScreen(), settings);

      // ── About & Legal Module ─────────────────────────────────────────────────
      case AppRoutes.aboutUs:
        return _build(const AboutScreen(), settings);

      case AppRoutes.termsConditions:
        return _build(const TermsConditionsScreen(), settings);

      case AppRoutes.privacyPolicy:
        return _build(const PrivacyPolicyScreen(), settings);

      case '/customer/system/no-internet':
        return _build(const NoInternetScreen(), settings);

      case '/customer/system/status':
        return _build(const SystemStatusScreen(), settings);

      // ── Support & Settings Module ───────────────────────────────────────────
      case AppRoutes.helpSupport:
        return _build(const HelpSupportScreen(), settings);

      case AppRoutes.liveChat:
        return _build(const LiveChatScreen(), settings);

      case AppRoutes.raiseComplaint:
        return _build(const RaiseComplaintScreen(), settings);

      case AppRoutes.customerSettings:
        return _build(const SettingsScreen(), settings);

      // ── Engagement & Retention Module ──────────────────────────────────────
      case AppRoutes.notifications:
        return _build(const NotificationsScreen(), settings);

      case AppRoutes.offers:
        return _build(const OffersScreen(), settings);

      case AppRoutes.referAndEarn:
        return _build(const ReferEarnScreen(), settings);

      case AppRoutes.favoriteProfessionals:
        return _build(const FavoriteProfessionalsScreen(), settings);

      case AppRoutes.recentlyViewed:
        return _build(const RecentlyViewedScreen(), settings);

      // ── Profile & Wallet Module ─────────────────────────────────────────────
      case AppRoutes.customerProfile:
        return _build(const ProfileScreen(), settings);

      case AppRoutes.editProfile:
        return _build(const EditProfileScreen(), settings);

      case AppRoutes.savedAddresses:
        return _build(const SavedAddressesScreen(), settings);

      case AppRoutes.paymentMethods:
        return _build(const PaymentMethodsScreen(), settings);

      case AppRoutes.customerWallet:
        return _build(const WalletScreen(), settings);

      // ── Address & Chat & Payment & Review ──────────────────────────────────
      case AppRoutes.bookingAddress:
        return _build(const SelectAddressScreen(), settings);

      case AppRoutes.customerChat:
        return _build(const ChatScreen(), settings);

      case AppRoutes.bookingPayment:
        return _build(const PaymentScreen(), settings);

      case '/customer/payment/invoice':
        return _build(const InvoiceScreen(), settings);

      case AppRoutes.customerReviews:
      case AppRoutes.bookingReview:
        return _build(const ReviewScreen(), settings);

      // ── Bookings Management Flow ──────────────────────────────────────────
      case AppRoutes.myBookings:
        return _build(const MyBookingsScreen(), settings);

      case AppRoutes.rescheduleBooking:
        return _build(const RescheduleBookingScreen(), settings);

      case AppRoutes.cancelBooking:
        return _build(const CancelBookingScreen(), settings);

      case AppRoutes.bookingHistory:
        return _build(const BookingHistoryScreen(), settings);

      // ── Inspection Booking Flow (USP of KaamSetu) ────────────────────────────
      case '/customer/inspection/intro':
        return _build(const InspectionIntroScreen(), settings);

      case AppRoutes.problemDetails:
        return _build(const InspectionDetailsScreen(), settings);

      case AppRoutes.inspectionSchedule:
        return _build(const InspectionScheduleScreen(), settings);

      case AppRoutes.professionalAssigned:
        return _build(const InspectorAssignedScreen(), settings);

      case AppRoutes.inspectionTracking:
        return _build(const LiveInspectionTrackingScreen(), settings);

      case '/customer/inspection/in-progress':
        return _build(const InspectionInProgressScreen(), settings);

      case AppRoutes.inspectionReport:
        return _build(const InspectionReportScreen(), settings);

      case AppRoutes.priceComparison:
        return _build(const MarketPriceComparisonScreen(), settings);

      case AppRoutes.quotationReview:
        return _build(const QuotationReviewScreen(), settings);

      case AppRoutes.quotationDecision:
        return _build(const QuotationDecisionScreen(), settings);

      case AppRoutes.negotiationChat:
        return _build(const NegotiationChatScreen(), settings);

      case AppRoutes.revisedQuotation:
        return _build(const RevisedQuotationScreen(), settings);

      case AppRoutes.repairConfirmation:
        return _build(const RepairConfirmationScreen(), settings);

      case AppRoutes.repairTracking:
        return _build(const RepairTrackingScreen(), settings);

      case AppRoutes.inspectionCompleted:
        return _build(const InspectionBookingCompletedScreen(), settings);

      // ── Normal Booking Flow ─────────────────────────────────────────────────
      case AppRoutes.serviceSelection:
        return _build(const ServiceSelectionScreen(), settings);

      case AppRoutes.bookingDetails:
        return _build(const BookingDetailsScreen(), settings);

      case AppRoutes.bookingSchedule:
        return _build(const ScheduleScreen(), settings);

      case AppRoutes.priceEstimation:
        return _build(const PriceEstimationScreen(), settings);

      case AppRoutes.bookingSummary:
        return _build(const BookingSummaryScreen(), settings);

      case AppRoutes.searchingWorker:
        return _build(const SearchingWorkerScreen(), settings);

      case AppRoutes.workerAssigned:
        return _build(const WorkerAssignedScreen(), settings);

      case AppRoutes.liveTracking:
        return _build(const LiveTrackingScreen(), settings);

      case '/customer/booking/work-in-progress':
        return _build(const WorkInProgressScreen(), settings);

      case '/customer/booking/work-completed':
        return _build(const WorkCompletedScreen(), settings);

      case AppRoutes.workInProgress:
        return _build(const BookingStatusScreen(), settings);

      // ── Fallback ────────────────────────────────────────────────────────────
      default:
        return _build(
          Scaffold(
            backgroundColor: Colors.white,
            body: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.map_outlined, size: 48, color: Color(0xFFCBD5E1)),
                  const SizedBox(height: 16),
                  const Text(
                    'Page not found',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'No route for "${settings.name}"',
                    style: const TextStyle(
                      fontSize: 13,
                      color: Color(0xFF64748B),
                    ),
                  ),
                ],
              ),
            ),
          ),
          settings,
        );
    }
  }

  /// Helper: wraps a widget in a [PageRouteBuilder] with a smooth fade transition.
  static Route<dynamic> _build(Widget page, RouteSettings settings) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (_, __, ___) => page,
      transitionsBuilder: (_, anim, __, child) {
        return FadeTransition(
          opacity: CurvedAnimation(parent: anim, curve: Curves.easeIn),
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 250),
    );
  }
}
