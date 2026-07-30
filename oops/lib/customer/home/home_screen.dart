// File:
// lib/customer/home/home_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentNavIndex = 0;
  final PageController _bannerController = PageController();
  int _currentBannerIndex = 0;

  // ── Dummy Data ─────────────────────────────────────────────────────────────
  final List<Map<String, dynamic>> _categories = [
    {'name': 'Electrician', 'icon': Icons.bolt_rounded, 'color': const Color(0xFF3B82F6)},
    {'name': 'Plumber', 'icon': Icons.plumbing_rounded, 'color': const Color(0xFF0EA5E9)},
    {'name': 'Carpenter', 'icon': Icons.handyman_rounded, 'color': const Color(0xFFF59E0B)},
    {'name': 'Painter', 'icon': Icons.format_paint_rounded, 'color': const Color(0xFFEC4899)},
    {'name': 'Cleaning', 'icon': Icons.cleaning_services_rounded, 'color': const Color(0xFF10B981)},
    {'name': 'AC Repair', 'icon': Icons.ac_unit_rounded, 'color': const Color(0xFF06B6D4)},
    {'name': 'Appliance', 'icon': Icons.kitchen_rounded, 'color': const Color(0xFF8B5CF6)},
    {'name': 'Gardening', 'icon': Icons.park_rounded, 'color': const Color(0xFF84CC16)},
    {'name': 'Pest Control', 'icon': Icons.bug_report_rounded, 'color': const Color(0xFFEF4444)},
    {'name': 'More', 'icon': Icons.grid_view_rounded, 'color': const Color(0xFF64748B)},
  ];

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

  final List<Map<String, dynamic>> _popularServices = [
    {
      'name': 'Split AC Repair & Service',
      'category': 'AC Service',
      'price': '₹499',
      'rating': '4.8',
      'reviews': '1.2k',
      'icon': Icons.ac_unit_rounded,
      'color': const Color(0xFF0EA5E9),
    },
    {
      'name': 'Tap & Pipe Leak Fix',
      'category': 'Plumbing',
      'price': '₹299',
      'rating': '4.9',
      'reviews': '850',
      'icon': Icons.plumbing_rounded,
      'color': const Color(0xFF2563EB),
    },
    {
      'name': 'Switch & Socket Replacement',
      'category': 'Electrical',
      'price': '₹199',
      'rating': '4.7',
      'reviews': '2.1k',
      'icon': Icons.bolt_rounded,
      'color': const Color(0xFFF59E0B),
    },
  ];

  final List<Map<String, dynamic>> _nearbyPros = [
    {
      'name': 'Suresh Kumar',
      'role': 'Master Electrician',
      'rating': '4.9',
      'jobs': '340+ Jobs',
      'distance': '1.2 km away',
      'price': '₹199/hr',
    },
    {
      'name': 'Amit Verma',
      'role': 'Senior Plumber',
      'rating': '4.8',
      'jobs': '210+ Jobs',
      'distance': '2.5 km away',
      'price': '₹249/hr',
    },
  ];

  @override
  void dispose() {
    _bannerController.dispose();
    super.dispose();
  }

  void _onBottomNavTapped(int index) {
    if (index == _currentNavIndex) return;
    setState(() => _currentNavIndex = index);
    switch (index) {
      case 0:
        break;
      case 1:
        Navigator.pushNamed(context, AppRoutes.myBookings);
        break;
      case 2:
        Navigator.pushNamed(context, AppRoutes.helpSupport);
        break;
      case 3:
        Navigator.pushNamed(context, AppRoutes.customerProfile);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
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

              // ── Categories Grid ────────────────────────────────────
              _buildSectionHeader('Categories', onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerCategories)),
              const SizedBox(height: 12),
              _buildCategoriesGrid(),

              const SizedBox(height: 28),

              // ── Popular Services (Horizontal Cards) ────────────────
              _buildSectionHeader('Popular Services', onViewAll: () => Navigator.pushNamed(context, AppRoutes.customerServices)),
              const SizedBox(height: 12),
              _buildPopularServicesList(),

              const SizedBox(height: 28),

              // ── Nearby Professionals ───────────────────────────────
              _buildSectionHeader('Nearby Professionals', onViewAll: () => Navigator.pushNamed(context, AppRoutes.favoriteProfessionals)),
              const SizedBox(height: 12),
              _buildNearbyProfessionalsList(),

              const SizedBox(height: 28),

              // ── Recent Booking Card ────────────────────────────────
              _buildSectionHeader('Recent Booking', onViewAll: () => Navigator.pushNamed(context, AppRoutes.myBookings)),
              const SizedBox(height: 12),
              _buildRecentBookingCard(),

              const SizedBox(height: 32),
            ],
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
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
          unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w500, fontSize: 12),
          elevation: 0,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_rounded),
              label: 'Bookings',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.headset_mic_rounded),
              label: 'Support',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }

  // ── Header Widget ──────────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              GestureDetector(
                onTap: () => Navigator.pushNamed(context, AppRoutes.customerProfile),
                child: Row(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFFEFF6FF),
                        border: Border.all(color: const Color(0xFF2563EB), width: 1.5),
                      ),
                      child: const CircleAvatar(
                        backgroundColor: Color(0xFF2563EB),
                        child: Text(
                          'R',
                          style: TextStyle(fontWeight: FontWeight.w800, color: Colors.white, fontSize: 18),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Good Morning 👋',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Color(0xFF64748B)),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'Rahul Sharma',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              GestureDetector(
                onTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
                child: Stack(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(Icons.notifications_none_rounded, color: Color(0xFF0F172A), size: 22),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: Color(0xFFEF4444),
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Location Selector Chip
          GestureDetector(
            onTap: () => Navigator.pushNamed(context, AppRoutes.savedAddresses),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
              ),
              child: const Row(
                children: [
                  Icon(Icons.location_on_rounded, color: Color(0xFF2563EB), size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'HSR Layout, Sector 6, Bengaluru',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Icon(Icons.keyboard_arrow_down_rounded, color: Color(0xFF64748B), size: 20),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Search Bar Widget ──────────────────────────────────────────────────────
  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: GestureDetector(
        onTap: () => Navigator.pushNamed(context, AppRoutes.customerSearch),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: AbsorbPointer(
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Search for "AC repair", "Electrician"...',
                hintStyle: const TextStyle(fontSize: 14, color: Color(0xFF94A3B8)),
                prefixIcon: const Icon(Icons.search_rounded, color: Color(0xFF2563EB), size: 22),
                suffixIcon: Container(
                  margin: const EdgeInsets.all(6),
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2563EB),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.tune_rounded, color: Colors.white, size: 18),
                ),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ── Banner Carousel Widget ──────────────────────────────────────────────────
  Widget _buildBannerCarousel() {
    return Column(
      children: [
        SizedBox(
          height: 155,
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
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: (banner['bgGradient'][0] as Color).withOpacity(0.3),
                      blurRadius: 16,
                      offset: const Offset(0, 8),
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
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.25),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Text(
                              banner['code'] as String,
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            banner['title'] as String,
                            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            banner['subtitle'] as String,
                            style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.85)),
                            maxLines: 2,
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

        // Indicator Dots
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(_banners.length, (i) {
            final isActive = i == _currentBannerIndex;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              margin: const EdgeInsets.only(right: 5),
              width: isActive ? 20 : 6,
              height: 6,
              decoration: BoxDecoration(
                color: isActive ? const Color(0xFF2563EB) : const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(3),
              ),
            );
          }),
        ),
      ],
    );
  }

  // ── Categories Grid Widget ─────────────────────────────────────────────────
  Widget _buildCategoriesGrid() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: _categories.length,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 5,
          mainAxisSpacing: 16,
          crossAxisSpacing: 12,
          childAspectRatio: 0.72,
        ),
        itemBuilder: (context, index) {
          final cat = _categories[index];
          return GestureDetector(
            onTap: () => Navigator.pushNamed(context, AppRoutes.serviceSelection),
            child: Column(
              children: [
                Container(
                  width: 54,
                  height: 54,
                  decoration: BoxDecoration(
                    color: (cat['color'] as Color).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: (cat['color'] as Color).withOpacity(0.2), width: 1),
                  ),
                  child: Icon(
                    cat['icon'] as IconData,
                    color: cat['color'] as Color,
                    size: 26,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  cat['name'] as String,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  // ── Popular Services Horizontal List ───────────────────────────────────────
  Widget _buildPopularServicesList() {
    return SizedBox(
      height: 205,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20),
        itemCount: _popularServices.length,
        itemBuilder: (context, index) {
          final service = _popularServices[index];
          return Container(
            width: 220,
            margin: const EdgeInsets.only(right: 14),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.04),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: (service['color'] as Color).withOpacity(0.12),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Icon(service['icon'] as IconData, color: service['color'] as Color, size: 24),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFEF3C7),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.star_rounded, color: Color(0xFFD97706), size: 14),
                          const SizedBox(width: 3),
                          Text(
                            service['rating'] as String,
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF92400E)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const Spacer(),
                Text(
                  service['category'] as String,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 2),
                Text(
                  service['name'] as String,
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      service['price'] as String,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                    ),
                    GestureDetector(
                      onTap: () => Navigator.pushNamed(context, AppRoutes.customerServices),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF2563EB),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          'Add',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Colors.white),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  // ── Nearby Professionals List ──────────────────────────────────────────────
  Widget _buildNearbyProfessionalsList() {
    return SizedBox(
      height: 140,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20),
        itemCount: _nearbyPros.length,
        itemBuilder: (context, index) {
          final pro = _nearbyPros[index];
          return GestureDetector(
            onTap: () => Navigator.pushNamed(context, AppRoutes.favoriteProfessionals),
            child: Container(
              width: 260,
              margin: const EdgeInsets.only(right: 14),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
              ),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      color: const Color(0xFFEFF6FF),
                    ),
                    child: const Icon(Icons.person_rounded, color: Color(0xFF2563EB), size: 36),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          pro['name'] as String,
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                        ),
                        Text(
                          pro['role'] as String,
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            const Icon(Icons.star_rounded, color: Color(0xFFFBBF24), size: 14),
                            const SizedBox(width: 4),
                            Text(
                              pro['rating'] as String,
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              pro['distance'] as String,
                              style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Recent Booking Card Widget ─────────────────────────────────────────────
  Widget _buildRecentBookingCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFFE2E8F0), width: 1),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFECFDF5),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Icon(Icons.check_circle_rounded, color: Color(0xFF10B981), size: 28),
            ),
            const SizedBox(width: 14),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Full House Inspection',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Completed yesterday • ₹199',
                    style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
            OutlinedButton(
              onPressed: () => Navigator.pushNamed(context, AppRoutes.serviceSelection),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                side: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text('Rebook', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
            ),
          ],
        ),
      ),
    );
  }

  // ── Helper Section Header Widget ───────────────────────────────────────────
  Widget _buildSectionHeader(String title, {required VoidCallback onViewAll}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A),
              letterSpacing: -0.4,
            ),
          ),
          GestureDetector(
            onTap: onViewAll,
            child: const Text(
              'See All',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: Color(0xFF2563EB),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
