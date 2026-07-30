/// Asset path constants — single source of truth for all asset references.
class AppAssets {
  AppAssets._();

  // ── Images ──────────────────────────────────────────────
  static const String _imgBase = 'assets/images';

  // Logos
  static const String logoFull    = '$_imgBase/logos/logo_full.png';
  static const String logoIcon    = '$_imgBase/logos/logo_icon.png';
  static const String logoWhite   = '$_imgBase/logos/logo_white.png';

  // Onboarding
  static const String onboarding1 = '$_imgBase/onboarding/onboarding_1.png';
  static const String onboarding2 = '$_imgBase/onboarding/onboarding_2.png';
  static const String onboarding3 = '$_imgBase/onboarding/onboarding_3.png';

  // Banners
  static const String banner1     = '$_imgBase/banners/banner_1.png';
  static const String banner2     = '$_imgBase/banners/banner_2.png';

  // Profile
  static const String defaultAvatar = '$_imgBase/profile/default_avatar.png';

  // ── Lottie Animations ───────────────────────────────────
  static const String _lottieBase = 'assets/lottie';
  static const String lottieLoading       = '$_lottieBase/loading.json';
  static const String lottieSuccess       = '$_lottieBase/success.json';
  static const String lottieError         = '$_lottieBase/error.json';
  static const String lottieEmpty         = '$_lottieBase/empty.json';
  static const String lottieSearching     = '$_lottieBase/searching.json';
  static const String lottieWorkerFound   = '$_lottieBase/worker_found.json';
  static const String lottieTracking      = '$_lottieBase/tracking.json';
  static const String lottiePaymentDone   = '$_lottieBase/payment_done.json';
  static const String lottieNoInternet    = '$_lottieBase/no_internet.json';

  // ── Icons ───────────────────────────────────────────────
  static const String _iconBase = 'assets/icons';
  static const String iconHome        = '$_iconBase/home.svg';
  static const String iconBookings    = '$_iconBase/bookings.svg';
  static const String iconChat        = '$_iconBase/chat.svg';
  static const String iconProfile     = '$_iconBase/profile.svg';
  static const String iconNotification = '$_iconBase/notification.svg';
  static const String iconLocation    = '$_iconBase/location.svg';
  static const String iconStar        = '$_iconBase/star.svg';
  static const String iconWallet      = '$_iconBase/wallet.svg';

  // ── Illustrations ────────────────────────────────────────
  static const String _illuBase = 'assets/illustrations';
  static const String illuNoBookings   = '$_illuBase/no_bookings.svg';
  static const String illuNoInternet   = '$_illuBase/no_internet.svg';
  static const String illuEmptySearch  = '$_illuBase/empty_search.svg';
  static const String illuError        = '$_illuBase/error.svg';
}
