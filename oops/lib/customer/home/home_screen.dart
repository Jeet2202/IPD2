import 'dart:async';
import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/category_model.dart';
import '../../shared/utils/category_helper.dart';
import '../../models/home_model.dart';
import '../../models/service_model.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../widgets/notification_bell.dart';
import '../../widgets/language_selector_widget.dart';
import '../../l10n/app_translations.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentNavIndex = 0;
  final PageController _bannerController = PageController();
  int _currentBannerIndex = 0;
  Timer? _autoRefreshTimer;

  bool _isLoading = true;
  String? _errorMessage;
  HomeModel? _homeModel;
  String? _profilePicUrl;

  // Promos / Promotional Banners
  final List<Map<String, dynamic>> _banners = [
    {
      'titleKey': 'summer_ac_offer',
      'subKey': 'summer_ac_sub',
      'code': 'USE: COOL30',
      'bgGradient': [const Color(0xFF1E40AF), const Color(0xFF3B82F6)],
      'icon': Icons.ac_unit_rounded,
    },
    {
      'titleKey': 'inspection_before_repair',
      'subKey': 'diagnosis_at_99',
      'code': 'BOOK NOW',
      'bgGradient': [const Color(0xFF0F766E), const Color(0xFF14B8A6)],
      'icon': Icons.verified_rounded,
    },
    {
      'titleKey': 'home_deep_cleaning_offer',
      'subKey': 'home_deep_cleaning_sub',
      'code': '20% DISCOUNT',
      'bgGradient': [const Color(0xFF6D28D9), const Color(0xFF8B5CF6)],
      'icon': Icons.cleaning_services_rounded,
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchHomeData();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _fetchHomeData(isSilent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _bannerController.dispose();
    super.dispose();
  }

  Future<void> _fetchHomeData({bool isSilent = false}) async {
    if (!isSilent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final homeData = await ApiService.instance.getHomeData();
      String? picUrl;
      try {
        final profile = await AuthService.instance.fetchCustomerProfile();
        picUrl = profile['profile_photo_url'] as String?;
      } catch (_) {}

      if (mounted) {
        setState(() {
          _homeModel = homeData;
          _profilePicUrl = picUrl;
          _isLoading = false;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.message;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Failed to load home screen. Please try again.';
          _isLoading = false;
        });
      }
    }
  }

  void _onBottomNavTapped(int index) async {
    if (index == 0) {
      setState(() => _currentNavIndex = 0);
      return;
    }
    setState(() => _currentNavIndex = index);
    switch (index) {
      case 1:
        await Navigator.pushNamed(context, AppRoutes.myBookings);
        break;
      case 2:
        await Navigator.pushNamed(context, AppRoutes.helpSupport);
        break;
      case 3:
        await Navigator.pushNamed(context, AppRoutes.customerProfile);
        break;
    }
    if (mounted) {
      setState(() => _currentNavIndex = 0);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _fetchHomeData,
          color: const Color(0xFF2563EB),
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(
              parent: BouncingScrollPhysics(),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Header Section ─────────────────────────────────────
                _buildHeader(),

                SizedBox(height: 16),

                // ── Search Bar ─────────────────────────────────────────
                _buildSearchBar(),

                SizedBox(height: 20),

                // ── Banner Carousel ────────────────────────────────────
                _buildBannerCarousel(),

                SizedBox(height: 24),

                // ── Body Content (Loading / Error / Success) ───────────
                if (_isLoading)
                  _buildLoadingShimmer()
                else if (_errorMessage != null)
                  _buildErrorView()
                else
                  _buildHomeSections(),

                SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),

      // ── Bottom Navigation Bar ──────────────────────────────────────
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentNavIndex,
          onTap: _onBottomNavTapped,
          type: BottomNavigationBarType.fixed,          selectedItemColor: const Color(0xFF2563EB),
          unselectedItemColor: const Color(0xFF94A3B8),
          selectedFontSize: 12,
          unselectedFontSize: 12,
          elevation: 0,
          items: [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded),
              activeIcon: Icon(Icons.home_rounded),
              label: 'home'.tr(context),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_rounded),
              activeIcon: Icon(Icons.calendar_today_rounded),
              label: 'my_bookings'.tr(context),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.headset_mic_rounded),
              activeIcon: Icon(Icons.headset_mic_rounded),
              label: 'support'.tr(context),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded),
              activeIcon: Icon(Icons.person_rounded),
              label: 'profile'.tr(context),
            ),
          ],
        ),
      ),
      // ── AI Assistant Floating Button ──────────────────────────────────
      floatingActionButton: Padding(
        padding: EdgeInsets.only(bottom: 8),
        child: FloatingActionButton(
          onPressed: () => Navigator.pushNamed(context, AppRoutes.customerAIAssistant),
          backgroundColor: Colors.transparent,
          elevation: 0,
          child: Container(
            width: 58,
            height: 58,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF7C3AED), Color(0xFF2563EB)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(18),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF7C3AED).withOpacity(0.35),
                  blurRadius: 16,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: Icon(Icons.auto_awesome_rounded, color: Colors.white, size: 24),
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    );
  }

  // ── 1. Header Section ──────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Padding(
      padding: EdgeInsets.fromLTRB(20, 16, 20, 0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              GestureDetector(
                onTap: () => Navigator.pushNamed(context, AppRoutes.customerProfile),
                child: Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFFDBEAFE),
                    border: Border.all(color: const Color(0xFF2563EB), width: 1.5),
                  ),
                  child: _profilePicUrl != null && _profilePicUrl!.isNotEmpty
                      ? ClipOval(
                          child: Image.network(
                            _profilePicUrl!,
                            width: 48,
                            height: 48,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) => Icon(Icons.person_rounded, color: Color(0xFF2563EB), size: 28),
                          ),
                        )
                      : const ClipOval(
                          child: Icon(Icons.person_rounded, color: Color(0xFF2563EB), size: 28),
                        ),
                ),
              ),
              SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.location_on_rounded, size: 10, color: Color(0xFF2563EB)),
                            SizedBox(width: 2),
                            Text('mumbai'.tr(context),
                              style: TextStyle(fontSize: 10, color: Color(0xFF334155), fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 2),
                  Text('welcometoally'.tr(context).tr(context),
                    style: TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                ],
              ),
            ],
          ),
          Row(
            children: [
              IconButton(
                icon: Icon(Icons.language_rounded, color: Color(0xFF2563EB), size: 24),
                tooltip: 'Select Language',
                onPressed: () => LanguageSelectorWidget.show(context),
              ),
              SizedBox(width: 4),
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: NotificationBell(
                  iconColor: const Color(0xFF334155),
                  iconSize: 22.0,
                  onBellPressed: () {
                    Navigator.pushNamed(context, AppRoutes.notifications);
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── 2. Search Bar ──────────────────────────────────────────────────────────
  Widget _buildSearchBar() {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 20),
      child: GestureDetector(
        onTap: () => Navigator.pushNamed(context, AppRoutes.customerSearch),
        child: Container(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Icon(Icons.search_rounded, color: Color(0xFF94A3B8), size: 22),
              SizedBox(width: 12),
              Expanded(
                child: Text('searchplaceholder'.tr(context).tr(context),
                  style: TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 14,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── 3. Banner Carousel ─────────────────────────────────────────────────────
  Widget _buildBannerCarousel() {
    return Column(
      children: [
        SizedBox(
          height: 140,
          child: PageView.builder(
            controller: _bannerController,
            onPageChanged: (index) => setState(() => _currentBannerIndex = index),
            itemCount: _banners.length,
            itemBuilder: (context, index) {
              final banner = _banners[index];
              return Container(
                margin: EdgeInsets.symmetric(horizontal: 20),
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: banner['bgGradient'] as List<Color>,
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: (banner['bgGradient'] as List<Color>)[0].withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            (banner['titleKey'] as String).tr(context),
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 6),
                          Text(
                            (banner['subKey'] as String).tr(context),
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.9),
                              fontSize: 12,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          SizedBox(height: 10),
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.25),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              banner['code'] as String,
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      banner['icon'] as IconData,
                      size: 64,
                      color: Colors.white.withOpacity(0.3),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        SizedBox(height: 10),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            _banners.length,
            (index) => AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              margin: EdgeInsets.symmetric(horizontal: 3),
              width: _currentBannerIndex == index ? 20 : 6,
              height: 6,
              decoration: BoxDecoration(
                color: _currentBannerIndex == index
                    ? const Color(0xFF2563EB)
                    : const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionCards() {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: () => Navigator.pushNamed(
                context,
                AppRoutes.createBookingDetails,
                arguments: {'booking_type': 'custom_service'},
              ),
              child: Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF2563EB).withValues(alpha: 0.3),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.add_task_rounded, color: Colors.white, size: 28),
                    SizedBox(height: 12),
                    Text('booknewservice'.tr(context).tr(context),
                      style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 2),
                    Text('customservicerequest'.tr(context).tr(context),
                      style: TextStyle(color: Colors.white70, fontSize: 11),
                    ),
                  ],
                ),
              ),
            ),
          ),
          SizedBox(width: 14),
          Expanded(
            child: GestureDetector(
              onTap: () => Navigator.pushNamed(
                context,
                AppRoutes.problemDetails,
                arguments: {'booking_type': 'inspection_request'},
              ),
              child: Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0F766E), Color(0xFF0D9488)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF0F766E).withValues(alpha: 0.3),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.search_rounded, color: Colors.white, size: 28),
                    SizedBox(height: 12),
                    Text('inspectionvisit'.tr(context).tr(context),
                      style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 2),
                    Text('unsurewhatisbroken'.tr(context).tr(context),
                      style: TextStyle(color: Colors.white70, fontSize: 11),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── 4. Main Home Sections ──────────────────────────────────────────────────
  Widget _buildHomeSections() {
    final model = _homeModel ?? const HomeModel();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildQuickActionCards(),
        SizedBox(height: 24),

        // ── Featured Categories ──────────────────────────────────────────────
        _buildSectionHeader(
          'featured_categories'.tr(context),
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerCategories),
        ),
        SizedBox(height: 12),
        _buildCategoriesList(model.featuredCategories),

        SizedBox(height: 28),

        // ── Featured Services ────────────────────────────────────────────────
        _buildSectionHeader(
          'featured_services'.tr(context),
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        SizedBox(height: 12),
        _buildHorizontalServicesList(model.featuredServices, emptyMessage: 'No featured services available'),

        SizedBox(height: 28),

        // ── Popular Services ─────────────────────────────────────────────────
        _buildSectionHeader(
          'popular_services'.tr(context),
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        SizedBox(height: 12),
        _buildHorizontalServicesList(model.popularServices, emptyMessage: 'No popular services found'),

        SizedBox(height: 28),

        // ── Recommended Services ─────────────────────────────────────────────
        _buildSectionHeader(
          'recommended_for_you'.tr(context),
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        SizedBox(height: 12),
        _buildHorizontalServicesList(model.recommendedServices, emptyMessage: 'No recommendations at this moment'),

        SizedBox(height: 28),

        // ── Recently Added Services ──────────────────────────────────────────
        _buildSectionHeader(
          'recently_added_services'.tr(context),
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        SizedBox(height: 12),
        _buildHorizontalServicesList(model.recentServices, emptyMessage: 'No recent services found'),
      ],
    );
  }

  // ── Section Header Widget ──────────────────────────────────────────────────
  Widget _buildSectionHeader(String title, {VoidCallback? onViewAll}) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0F172A),
            ),
          ),
          if (onViewAll != null)
            GestureDetector(
              onTap: onViewAll,
              child: Text('viewall'.tr(context).tr(context),
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2563EB),
                ),
              ),
            ),
        ],
      ),
    );
  }

  // ── Categories List Widget ─────────────────────────────────────────────────
  Widget _buildCategoriesList(List<CategoryModel> categories) {
    if (categories.isEmpty) {
      return _buildEmptySectionPlaceholder('No categories available');
    }

    return SizedBox(
      height: 95,
      child: ListView.builder(
        padding: EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final cat = categories[index];
          return Padding(
            padding: EdgeInsets.symmetric(horizontal: 6),
            child: GestureDetector(
              onTap: () => Navigator.pushNamed(
                context,
                AppRoutes.customerCategories,
                arguments: {'category_id': cat.id, 'category_name': cat.name},
              ),
              child: SizedBox(
                width: 76,
                child: Column(
                  children: [
                    Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: cat.resolvedBgLight,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: cat.resolvedColor.withValues(alpha: 0.2)),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: Image.network(
                          cat.resolvedImage,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => Icon(
                            cat.resolvedIcon,
                            color: cat.resolvedColor,
                            size: 28,
                          ),
                        ),
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      AppTranslations.getLocalizedName(context, cat.name),
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF334155),
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Reusable Horizontal Service List ───────────────────────────────────────
  Widget _buildHorizontalServicesList(
    List<ServiceModel> services, {
    required String emptyMessage,
  }) {
    if (services.isEmpty) {
      return _buildEmptySectionPlaceholder(emptyMessage);
    }

    return SizedBox(
      height: 230,
      child: ListView.builder(
        padding: EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        itemCount: services.length,
        itemBuilder: (context, index) {
          final service = services[index];
          return Padding(
            padding: EdgeInsets.symmetric(horizontal: 6),
            child: _buildServiceCard(service),
          );
        },
      ),
    );
  }

  // ── Service Card Widget ────────────────────────────────────────────────────
  Widget _buildServiceCard(ServiceModel service) {
    return GestureDetector(
      onTap: () => Navigator.pushNamed(
        context,
        AppRoutes.customerServiceDetail,
        arguments: {'service_id': service.id, 'service': service},
      ),
      child: Container(
        width: 190,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Service Image
            Stack(
              children: [
                Container(
                  height: 110,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.vertical(top: Radius.circular(15)),
                  ),
                  child: ClipRRect(
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(15)),
                    child: Image.network(
                      service.resolvedImage,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Icon(
                        CategoryHelper.getCategoryIcon(service.categorySlug),
                        color: CategoryHelper.getCategoryColor(service.categorySlug),
                        size: 40,
                      ),
                    ),
                  ),
                ),
                if (service.isFeatured)
                  Positioned(
                    top: 8,
                    left: 8,
                    child: Container(
                      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFF2563EB),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text('featured'.tr(context),
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ),
              ],
            ),

            // Card Body
            Expanded(
              child: Padding(
                padding: EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          AppTranslations.getLocalizedName(context, service.name),
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        SizedBox(height: 2),
                        Text(
                          service.shortDescription.isNotEmpty
                              ? service.shortDescription
                              : (service.durationDisplay.isNotEmpty ? service.durationDisplay : 'Professional Service'),
                          style: TextStyle(
                            fontSize: 11,
                            color: Color(0xFF64748B),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            service.priceRangeDisplay.isNotEmpty
                                ? service.priceRangeDisplay
                                : '₹${service.basePrice.toStringAsFixed(0)}',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF2563EB),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        SizedBox(width: 4),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.star_rounded, size: 14, color: Color(0xFFF59E0B)),
                            SizedBox(width: 2),
                            Text(
                              service.rating.toStringAsFixed(1),
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF334155),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Empty Section Placeholder ──────────────────────────────────────────────
  Widget _buildEmptySectionPlaceholder(String message) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 20),
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Center(
        child: Text(
          message,
          style: TextStyle(
            color: Color(0xFF94A3B8),
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  // ── Loading Shimmer State ──────────────────────────────────────────────────
  Widget _buildLoadingShimmer() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('Loading Categories...'),
        SizedBox(height: 12),
        SizedBox(
          height: 95,
          child: ListView.builder(
            padding: EdgeInsets.symmetric(horizontal: 16),
            scrollDirection: Axis.horizontal,
            itemCount: 5,
            itemBuilder: (_, __) => Padding(
              padding: EdgeInsets.symmetric(horizontal: 6),
              child: Container(
                width: 76,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
        ),
        SizedBox(height: 28),
        _buildSectionHeader('Loading Services...'),
        SizedBox(height: 12),
        SizedBox(
          height: 220,
          child: ListView.builder(
            padding: EdgeInsets.symmetric(horizontal: 16),
            scrollDirection: Axis.horizontal,
            itemCount: 3,
            itemBuilder: (_, __) => Padding(
              padding: EdgeInsets.symmetric(horizontal: 6),
              child: Container(
                width: 190,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  // ── Error View with Retry ──────────────────────────────────────────────────
  Widget _buildErrorView() {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      padding: EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFFCA5A5)),
      ),
      child: Column(
        children: [
          Icon(Icons.wifi_off_rounded, size: 48, color: Color(0xFFEF4444)),
          SizedBox(height: 12),
          Text('unable_to_connect_to_ally'.tr(context),
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0F172A),
            ),
          ),
          SizedBox(height: 6),
          Text(
            _errorMessage ?? 'Please check your connection and try again.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
          ),
          SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _fetchHomeData,
            icon: Icon(Icons.refresh_rounded, size: 18),
            label: Text('try_again'.tr(context)),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }
}
