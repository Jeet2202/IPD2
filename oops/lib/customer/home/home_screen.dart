// File: lib/customer/home/home_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/category_model.dart';
import '../../shared/utils/category_helper.dart';
import '../../models/home_model.dart';
import '../../models/service_model.dart';
import '../../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentNavIndex = 0;
  final PageController _bannerController = PageController();
  int _currentBannerIndex = 0;

  bool _isLoading = true;
  String? _errorMessage;
  HomeModel? _homeModel;

  // Promos / Promotional Banners
  final List<Map<String, dynamic>> _banners = [
    {
      'title': 'Summer AC Service Offer',
      'subtitle': 'Get up to 30% OFF on deep cleaning & gas refill',
      'code': 'USE: COOL30',
      'bgGradient': [const Color(0xFF1E40AF), const Color(0xFF3B82F6)],
      'icon': Icons.ac_unit_rounded,
    },
    {
      'title': 'Inspection Before Repair',
      'subtitle': 'Diagnosis at just ₹99. Zero hidden charges!',
      'code': 'BOOK NOW',
      'bgGradient': [const Color(0xFF0F766E), const Color(0xFF14B8A6)],
      'icon': Icons.verified_rounded,
    },
    {
      'title': 'Home Deep Cleaning',
      'subtitle': 'Professional sanitization & deep cleaning experts',
      'code': '20% DISCOUNT',
      'bgGradient': [const Color(0xFF6D28D9), const Color(0xFF8B5CF6)],
      'icon': Icons.cleaning_services_rounded,
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchHomeData();
  }

  @override
  void dispose() {
    _bannerController.dispose();
    super.dispose();
  }

  Future<void> _fetchHomeData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final homeData = await ApiService.instance.getHomeData();
      if (mounted) {
        setState(() {
          _homeModel = homeData;
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

                const SizedBox(height: 16),

                // ── Search Bar ─────────────────────────────────────────
                _buildSearchBar(),

                const SizedBox(height: 20),

                // ── Banner Carousel ────────────────────────────────────
                _buildBannerCarousel(),

                const SizedBox(height: 24),

                // ── Body Content (Loading / Error / Success) ───────────
                if (_isLoading)
                  _buildLoadingShimmer()
                else if (_errorMessage != null)
                  _buildErrorView()
                else
                  _buildHomeSections(),

                const SizedBox(height: 32),
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
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          selectedItemColor: const Color(0xFF2563EB),
          unselectedItemColor: const Color(0xFF94A3B8),
          selectedFontSize: 12,
          unselectedFontSize: 12,
          elevation: 0,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded),
              activeIcon: Icon(Icons.home_rounded),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_rounded),
              activeIcon: Icon(Icons.calendar_today_rounded),
              label: 'Bookings',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.headset_mic_rounded),
              activeIcon: Icon(Icons.headset_mic_rounded),
              label: 'Support',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded),
              activeIcon: Icon(Icons.person_rounded),
              label: 'Profile',
            ),
          ],
        ),
      ),
      // ── AI Assistant Floating Button ──────────────────────────────────
      floatingActionButton: Padding(
        padding: const EdgeInsets.only(bottom: 8),
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
            child: const Icon(Icons.auto_awesome_rounded, color: Colors.white, size: 24),
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    );
  }

  // ── 1. Header Section ──────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
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
                  child: const ClipOval(
                    child: Icon(Icons.person_rounded, color: Color(0xFF2563EB), size: 28),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Text(
                        'Good Day 👋',
                        style: TextStyle(
                          fontSize: 13,
                          color: Color(0xFF64748B),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.location_on_rounded, size: 10, color: Color(0xFF2563EB)),
                            SizedBox(width: 2),
                            Text(
                              'Mumbai',
                              style: TextStyle(fontSize: 10, color: Color(0xFF334155), fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  const Text(
                    'Welcome to KaamSetu',
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
          IconButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Notifications feature coming soon!'),
                  duration: Duration(seconds: 2),
                ),
              );
            },
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: const Icon(Icons.notifications_none_rounded, color: Color(0xFF334155), size: 22),
            ),
          ),
        ],
      ),
    );
  }

  // ── 2. Search Bar ──────────────────────────────────────────────────────────
  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: GestureDetector(
        onTap: () => Navigator.pushNamed(context, AppRoutes.customerSearch),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
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
          child: const Row(
            children: [
              Icon(Icons.search_rounded, color: Color(0xFF94A3B8), size: 22),
              SizedBox(width: 12),
              Text(
                'Search for AC repair, plumbing, electrical...',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 14,
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
                margin: const EdgeInsets.symmetric(horizontal: 20),
                padding: const EdgeInsets.all(20),
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
                            banner['title'] as String,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            banner['subtitle'] as String,
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.9),
                              fontSize: 12,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 10),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.25),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              banner['code'] as String,
                              style: const TextStyle(
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
        const SizedBox(height: 10),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            _banners.length,
            (index) => AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              margin: const EdgeInsets.symmetric(horizontal: 3),
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

  // ── 4. Main Home Sections ──────────────────────────────────────────────────
  Widget _buildHomeSections() {
    final model = _homeModel ?? const HomeModel();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Featured Categories ──────────────────────────────────────────────
        _buildSectionHeader(
          'Featured Categories',
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerCategories),
        ),
        const SizedBox(height: 12),
        _buildCategoriesList(model.featuredCategories),

        const SizedBox(height: 28),

        // ── Featured Services ────────────────────────────────────────────────
        _buildSectionHeader(
          'Featured Services',
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        const SizedBox(height: 12),
        _buildHorizontalServicesList(model.featuredServices, emptyMessage: 'No featured services available'),

        const SizedBox(height: 28),

        // ── Popular Services ─────────────────────────────────────────────────
        _buildSectionHeader(
          'Popular Services',
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        const SizedBox(height: 12),
        _buildHorizontalServicesList(model.popularServices, emptyMessage: 'No popular services found'),

        const SizedBox(height: 28),

        // ── Recommended Services ─────────────────────────────────────────────
        _buildSectionHeader(
          'Recommended For You',
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        const SizedBox(height: 12),
        _buildHorizontalServicesList(model.recommendedServices, emptyMessage: 'No recommendations at this moment'),

        const SizedBox(height: 28),

        // ── Recently Added Services ──────────────────────────────────────────
        _buildSectionHeader(
          'Recently Added Services',
          onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices),
        ),
        const SizedBox(height: 12),
        _buildHorizontalServicesList(model.recentServices, emptyMessage: 'No recent services found'),
      ],
    );
  }

  // ── Section Header Widget ──────────────────────────────────────────────────
  Widget _buildSectionHeader(String title, {VoidCallback? onViewAll}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0F172A),
            ),
          ),
          if (onViewAll != null)
            GestureDetector(
              onTap: onViewAll,
              child: const Text(
                'See All',
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
        padding: const EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final cat = categories[index];
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 6),
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
                    const SizedBox(height: 6),
                    Text(
                      cat.name,
                      style: const TextStyle(
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
        padding: const EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        itemCount: services.length,
        itemBuilder: (context, index) {
          final service = services[index];
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 6),
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
                  decoration: const BoxDecoration(
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
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFF2563EB),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        'FEATURED',
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
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          service.name,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0F172A),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          service.shortDescription.isNotEmpty
                              ? service.shortDescription
                              : (service.durationDisplay.isNotEmpty ? service.durationDisplay : 'Professional Service'),
                          style: const TextStyle(
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
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF2563EB),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.star_rounded, size: 14, color: Color(0xFFF59E0B)),
                            const SizedBox(width: 2),
                            Text(
                              service.rating.toStringAsFixed(1),
                              style: const TextStyle(
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
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Center(
        child: Text(
          message,
          style: const TextStyle(
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
        const SizedBox(height: 12),
        SizedBox(
          height: 95,
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            scrollDirection: Axis.horizontal,
            itemCount: 5,
            itemBuilder: (_, __) => Padding(
              padding: const EdgeInsets.symmetric(horizontal: 6),
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
        const SizedBox(height: 28),
        _buildSectionHeader('Loading Services...'),
        const SizedBox(height: 12),
        SizedBox(
          height: 220,
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            scrollDirection: Axis.horizontal,
            itemCount: 3,
            itemBuilder: (_, __) => Padding(
              padding: const EdgeInsets.symmetric(horizontal: 6),
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
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFFCA5A5)),
      ),
      child: Column(
        children: [
          const Icon(Icons.wifi_off_rounded, size: 48, color: Color(0xFFEF4444)),
          const SizedBox(height: 12),
          const Text(
            'Unable to connect to KaamSetu',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            _errorMessage ?? 'Please check your connection and try again.',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _fetchHomeData,
            icon: const Icon(Icons.refresh_rounded, size: 18),
            label: const Text('Try Again'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }
}
