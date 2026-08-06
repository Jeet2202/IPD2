import 'dart:async';
import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../models/booking_model.dart';
import '../../../models/service_model.dart';
import '../../../services/api_service.dart';
import '../../../services/booking_service.dart';

class MyBookingsScreen extends StatefulWidget {
  const MyBookingsScreen({super.key});

  @override
  State<MyBookingsScreen> createState() => _MyBookingsScreenState();
}

class _MyBookingsScreenState extends State<MyBookingsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final BookingService _bookingService = BookingService.instance;

  String _selectedFilter = 'All';
  final List<String> _filters = ['All', 'Pending', 'Assigned', 'In Progress', 'Work Completed', 'Completed', 'Cancelled'];

  bool _isLoading = true;
  String? _errorMessage;
  List<BookingModel> _allBookings = [];
  Timer? _autoRefreshTimer;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(_handleTabSelection);
    _fetchBookings();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _fetchBookings(isSilent: true);
    });
  }

  void _handleTabSelection() {
    if (_tabController.indexIsChanging) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _tabController.removeListener(_handleTabSelection);
    _tabController.dispose();
    super.dispose();
  }

  String? _mapFilterToStatusParam(String filter) {
    switch (filter) {
      case 'Pending':
        return 'pending';
      case 'Assigned':
        return 'assigned';
      case 'In Progress':
        return 'in_progress';
      case 'Work Completed':
        return 'work_completed';
      case 'Completed':
        return 'completed';
      case 'Cancelled':
        return 'cancelled';
      default:
        return null;
    }
  }

  Future<void> _fetchBookings({bool isSilent = false}) async {
    if (!isSilent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final statusParam = _mapFilterToStatusParam(_selectedFilter);
      final list = await _bookingService.fetchBookings(status: statusParam);
      if (!mounted) return;

      setState(() {
        _allBookings = list;
        _isLoading = false;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.message;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = 'Failed to load bookings. Please check network connection.';
        _isLoading = false;
      });
    }
  }

  List<BookingModel> _getFilteredListForTab(int tabIndex) {
    if (tabIndex == 0) {
      // Direct Services
      return _allBookings.where((b) => b.bookingType != 'inspection_request').toList();
    } else {
      // Inspection Flow
      return _allBookings.where((b) => b.bookingType == 'inspection_request').toList();
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return const Color(0xFFD97706); // Amber
      case 'assigned':
      case 'accepted':
        return const Color(0xFF2563EB); // Blue
      case 'worker_en_route':
        return const Color(0xFF6366F1); // Indigo
      case 'arrived':
        return const Color(0xFF8B5CF6); // Purple
      case 'in_progress':
        return const Color(0xFF4F46E5); // Indigo
      case 'work_completed':
        return const Color(0xFF0D9488); // Teal
      case 'customer_confirmed':
      case 'completed':
        return const Color(0xFF16A34A); // Green
      case 'cancelled':
        return const Color(0xFFDC2626); // Red
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            } else {
              Navigator.pushReplacementNamed(context, AppRoutes.customerHome);
            }
          },
        ),
        title: const Text(
          'My Bookings',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppColors.primary,
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: AppColors.primary,
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
          tabs: const [
            Tab(text: 'Direct Services'),
            Tab(text: 'Inspection Visits'),
          ],
        ),
      ),
      body: Column(
        children: [
          // ── Filter Chips ───────────────────────────────────────────────
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: SizedBox(
              height: 38,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: _filters.length,
                itemBuilder: (context, index) {
                  final filter = _filters[index];
                  final isSelected = _selectedFilter == filter;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text(filter),
                      selected: isSelected,
                      selectedColor: AppColors.primary,
                      backgroundColor: const Color(0xFFF1F5F9),
                      labelStyle: TextStyle(
                        fontSize: 12,
                        fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
                        color: isSelected ? Colors.white : const Color(0xFF475569),
                      ),
                      onSelected: (_) {
                        setState(() => _selectedFilter = filter);
                        _fetchBookings();
                      },
                    ),
                  );
                },
              ),
            ),
          ),

          // ── Tab View Content ──────────────────────────────────────────
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildTabBody(0),
                _buildTabBody(1),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: 1,
          onTap: (index) {
            if (index == 1) return;
            switch (index) {
              case 0:
                if (Navigator.canPop(context)) {
                  Navigator.pop(context);
                } else {
                  Navigator.pushReplacementNamed(context, AppRoutes.customerHome);
                }
                break;
              case 2:
                Navigator.pushReplacementNamed(context, AppRoutes.helpSupport);
                break;
              case 3:
                Navigator.pushReplacementNamed(context, AppRoutes.customerProfile);
                break;
            }
          },
          type: BottomNavigationBarType.fixed,          selectedItemColor: AppColors.primary,
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
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // "Book New Service" FAB is exclusively for Custom Service Requests
          Navigator.pushNamed(
            context,
            AppRoutes.createBookingDetails,
            arguments: {'booking_type': 'custom_service'},
          );
        },
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_rounded),
        label: const Text(
          'Book New Service',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
    );
  }


  Widget _buildPredefinedServicesHeader() {
    final predefinedList = [
      const ServiceModel(
        id: '6a6f95d0281409423c4cce35',
        categoryId: 'cat_ac_repair',
        categorySlug: 'ac-repair',
        name: 'AC Service & Repair',
        basePrice: 499,
        durationDisplay: '45 mins',
        image: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=400&q=80',
      ),
      const ServiceModel(
        id: '6a6f95d0281409423c4cce1b',
        categoryId: 'cat_plumbing',
        categorySlug: 'plumbing',
        name: 'Plumbing Leakage Fix',
        basePrice: 299,
        durationDisplay: '30 mins',
        image: 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?auto=format&fit=crop&w=400&q=80',
      ),
      const ServiceModel(
        id: '6a6f95d0281409423c4cce16',
        categoryId: 'cat_electrical',
        categorySlug: 'electrical',
        name: 'Switchboard Repair',
        basePrice: 199,
        durationDisplay: '20 mins',
        image: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=400&q=80',
      ),
      const ServiceModel(
        id: '6a6f95d0281409423c4cce1a',
        categoryId: 'cat_plumbing',
        categorySlug: 'plumbing',
        name: 'Tap Replacement',
        basePrice: 249,
        durationDisplay: '25 mins',
        image: 'https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=400&q=80',
      ),
    ];

    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Predefined Popular Services',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
              ),
              TextButton(
                onPressed: () => Navigator.pushNamed(context, AppRoutes.customerCategories),
                child: const Text('View All', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 110,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: predefinedList.length,
              itemBuilder: (context, idx) {
                final srv = predefinedList[idx];
                return GestureDetector(
                  onTap: () {
                    Navigator.pushNamed(
                      context,
                      AppRoutes.createBookingDetails,
                      arguments: {
                        'service': srv,
                        'booking_type': 'normal_service',
                      },
                    );
                  },
                  child: Container(
                    width: 145,
                    margin: const EdgeInsets.only(right: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withValues(alpha: 0.03), blurRadius: 8, offset: const Offset(0, 2)),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          srv.name,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '₹${srv.basePrice.toStringAsFixed(0)}',
                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppColors.primary),
                            ),
                            const Icon(Icons.arrow_forward_rounded, size: 16, color: AppColors.primary),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInspectionHeader() {
    return GestureDetector(
      onTap: () {
        Navigator.pushNamed(
          context,
          AppRoutes.problemDetails,
          arguments: {'booking_type': 'inspection_request'},
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 20),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF0F766E), Color(0xFF14B8A6)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(color: const Color(0xFF0F766E).withValues(alpha: 0.3), blurRadius: 10, offset: const Offset(0, 4)),
          ],
        ),
        child: const Row(
          children: [
            Icon(Icons.shield_outlined, color: Colors.white, size: 32),
            SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Unsure what is broken?', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                  SizedBox(height: 2),
                  Text('Request an expert technician diagnostic visit (₹99)', style: TextStyle(color: Colors.white70, fontSize: 11)),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios_rounded, color: Colors.white, size: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildTabBody(int tabIndex) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.primary),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off_rounded, size: 56, color: Color(0xFF94A3B8)),
              const SizedBox(height: 16),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 14),
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _fetchBookings,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('Retry'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final bookings = _getFilteredListForTab(tabIndex);

    if (bookings.isEmpty) {
      return RefreshIndicator(
        onRefresh: _fetchBookings,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
          child: Container(
            alignment: Alignment.center,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                tabIndex == 0 ? _buildPredefinedServicesHeader() : _buildInspectionHeader(),
                const SizedBox(height: 30),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: const BoxDecoration(
                    color: Color(0xFFEFF6FF),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.calendar_today_outlined, size: 48, color: AppColors.primary),
                ),
                const SizedBox(height: 20),
                Text(
                  tabIndex == 0 ? 'No Direct Service Bookings' : 'No Inspection Requests',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  _selectedFilter == 'All'
                      ? 'You have not placed any service bookings yet.'
                      : 'No bookings found with status "$_selectedFilter".',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    if (tabIndex == 1) {
                      Navigator.pushNamed(
                        context,
                        AppRoutes.problemDetails,
                        arguments: {'booking_type': 'inspection_request'},
                      );
                    } else {
                      Navigator.pushNamed(context, AppRoutes.customerCategories);
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: tabIndex == 1 ? const Color(0xFF0F766E) : AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: Text(
                    tabIndex == 1 ? 'Request Inspection Visit' : 'Browse Predefined Services',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _fetchBookings,
      color: AppColors.primary,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
        itemCount: bookings.length + 1,
        itemBuilder: (context, index) {
          if (index == 0) {
            return tabIndex == 0 ? _buildPredefinedServicesHeader() : _buildInspectionHeader();
          }

          final b = bookings[index - 1];
          final statusColor = _getStatusColor(b.status);

          return Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(22),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.03),
                  blurRadius: 10,
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
                    Expanded(
                      child: Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        crossAxisAlignment: WrapCrossAlignment.center,
                        children: [
                          Text(
                            b.bookingNumber,
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppColors.primary),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: b.bookingType == 'inspection_request'
                                  ? const Color(0xFFFEF3C7)
                                  : b.bookingType == 'custom_service'
                                      ? const Color(0xFFFFF7ED)
                                      : const Color(0xFFF1F5F9),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              b.bookingType == 'inspection_request'
                                  ? 'Inspection'
                                  : b.bookingType == 'custom_service'
                                      ? 'Custom'
                                      : 'Direct',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: b.bookingType == 'inspection_request'
                                    ? const Color(0xFFD97706)
                                    : b.bookingType == 'custom_service'
                                        ? const Color(0xFFEA580C)
                                        : AppColors.textSecondary,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: statusColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        b.isWorkCompleted
                            ? 'AWAITING CONFIRMATION'
                            : b.status.toUpperCase().replaceAll('_', ' '),
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: statusColor),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  b.serviceSnapshot.name,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined, size: 16),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        '${b.addressSnapshot.label} • ${b.addressSnapshot.city}',
                        style: const TextStyle(fontSize: 12),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Icon(Icons.schedule_rounded, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '${b.scheduledDate ?? 'ASAP'} ${b.scheduledTime != null ? '• ${b.scheduledTime}' : ''}',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
                if (b.isWorkCompleted) ...[
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FDF4),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFF86EFAC)),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.verified_rounded, size: 16, color: Color(0xFF0D9488)),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Work completed by worker. Tap to review & confirm.',
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF115E59)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                // ── Applicant count badge (only for PENDING marketplace bookings) ──
                if (b.isPending && b.applicantCount > 0) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEFF6FF),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFBFDBFE)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.people_alt_rounded, size: 15, color: Color(0xFF2563EB)),
                        const SizedBox(width: 8),
                        Text(
                          '${b.applicantCount} worker${b.applicantCount == 1 ? '' : 's'} have applied for this job',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF1D4ED8)),
                        ),
                      ],
                    ),
                  ),
                ],
                if (b.isPending && b.applicantCount == 0) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFFBEB),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFFDE68A)),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.hourglass_empty_rounded, size: 15, color: Color(0xFFD97706)),
                        SizedBox(width: 8),
                        Text(
                          'Looking for available workers nearby...',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF92400E)),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 14),
                const Divider(color: Color(0xFFF1F5F9), height: 1),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '₹${b.estimatedPrice?.toStringAsFixed(0) ?? '0'}',
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppColors.primary),
                    ),
                    ElevatedButton(
                      onPressed: () {
                        Navigator.pushNamed(
                          context,
                          AppRoutes.bookingDetails,
                          arguments: {'booking': b, 'booking_id': b.id},
                        ).then((_) => _fetchBookings());
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: b.isWorkCompleted ? const Color(0xFF0D9488) : const Color(0xFFEFF6FF),
                        foregroundColor: b.isWorkCompleted ? Colors.white : AppColors.primary,
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: Text(
                        b.isWorkCompleted ? 'Confirm Work' : 'View Details',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
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
}
