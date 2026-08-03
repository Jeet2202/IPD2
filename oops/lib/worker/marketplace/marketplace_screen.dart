// File: lib/worker/marketplace/marketplace_screen.dart

import 'dart:async';
import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/marketplace_booking_model.dart';
import '../../services/marketplace_service.dart';
import '../../utils/token_storage.dart';
import '../widgets/worker_bottom_navigation_bar.dart';
import 'widgets/marketplace_booking_card.dart';
import 'widgets/marketplace_booking_detail_modal.dart';
import 'widgets/marketplace_filter_bottom_sheet.dart';

class WorkerMarketplaceScreen extends StatefulWidget {
  const WorkerMarketplaceScreen({super.key});

  @override
  State<WorkerMarketplaceScreen> createState() => _WorkerMarketplaceScreenState();
}

class _WorkerMarketplaceScreenState extends State<WorkerMarketplaceScreen> {
  final TextEditingController _searchController = TextEditingController();
  Timer? _debounceTimer;

  bool _isLoading = true;
  String? _errorMessage;
  List<MarketplaceBookingItem> _bookings = [];
  int _totalBookings = 0;

  // Filter & Sort State
  MarketplaceFilterData _filterData = MarketplaceFilterData();
  String _selectedSort = 'recommended'; // recommended, newest, oldest, price_high, price_low

  @override
  void initState() {
    super.initState();
    _loadMarketplaceBookings();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _debounceTimer?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 400), () {
      _loadMarketplaceBookings();
    });
  }

  Future<void> _loadMarketplaceBookings() async {
    if (!mounted) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await MarketplaceService.instance.fetchMarketplaceBookings(
        query: _searchController.text,
        bookingType: _filterData.bookingType,
        scheduledDate: _filterData.scheduledDate,
        minPrice: _filterData.minPrice,
        maxPrice: _filterData.maxPrice,
        sortBy: _selectedSort,
        page: 1,
        pageSize: 50,
      );

      if (!mounted) return;

      setState(() {
        _bookings = result.items;
        _totalBookings = result.total;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _clearAllFilters() {
    _searchController.clear();
    setState(() {
      _filterData = MarketplaceFilterData();
      _selectedSort = 'recommended';
    });
    _loadMarketplaceBookings();
  }

  Future<void> _openFilterBottomSheet() async {
    final result = await MarketplaceFilterBottomSheet.show(context, _filterData);
    if (result != null) {
      setState(() {
        _filterData = result;
      });
      _loadMarketplaceBookings();
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasActiveFilters =
        _filterData.hasActiveFilters || _searchController.text.isNotEmpty;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFFEFF6FF),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(
                Icons.storefront_rounded,
                color: Color(0xFF2563EB),
                size: 22,
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Job Marketplace',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
                Text(
                  '$_totalBookings open booking${_totalBookings == 1 ? '' : 's'} available',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF64748B)),
            onPressed: _loadMarketplaceBookings,
            tooltip: 'Refresh Marketplace',
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Search Bar & Filter/Sort Controls
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
              child: Column(
                children: [
                  Row(
                    children: [
                      // Search Input Field
                      Expanded(
                        child: Container(
                          height: 44,
                          decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: TextField(
                            controller: _searchController,
                            onChanged: _onSearchChanged,
                            textInputAction: TextInputAction.search,
                            decoration: InputDecoration(
                              hintText: 'Search service, category, keyword...',
                              hintStyle: const TextStyle(
                                fontSize: 13,
                                color: Color(0xFF94A3B8),
                              ),
                              prefixIcon: const Icon(
                                Icons.search_rounded,
                                color: Color(0xFF64748B),
                                size: 20,
                              ),
                              suffixIcon: _searchController.text.isNotEmpty
                                  ? IconButton(
                                      icon: const Icon(Icons.clear_rounded,
                                          size: 18, color: Color(0xFF64748B)),
                                      onPressed: () {
                                        _searchController.clear();
                                        _loadMarketplaceBookings();
                                      },
                                    )
                                  : null,
                              border: InputBorder.none,
                              contentPadding:
                                  const EdgeInsets.symmetric(vertical: 10),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),

                      // Filter Bottom Sheet Button
                      GestureDetector(
                        onTap: _openFilterBottomSheet,
                        child: Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: _filterData.hasActiveFilters
                                ? const Color(0xFFEFF6FF)
                                : const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: _filterData.hasActiveFilters
                                  ? const Color(0xFF2563EB)
                                  : const Color(0xFFE2E8F0),
                            ),
                          ),
                          child: Icon(
                            Icons.tune_rounded,
                            color: _filterData.hasActiveFilters
                                ? const Color(0xFF2563EB)
                                : const Color(0xFF64748B),
                            size: 20,
                          ),
                        ),
                      ),

                      const SizedBox(width: 8),

                      // Sort Menu Dropdown
                      PopupMenuButton<String>(
                        initialValue: _selectedSort,
                        onSelected: (val) {
                          if (_selectedSort != val) {
                            setState(() {
                              _selectedSort = val;
                            });
                            _loadMarketplaceBookings();
                          }
                        },
                        itemBuilder: (ctx) => [
                          const PopupMenuItem(
                            value: 'recommended',
                            child: Row(
                              children: [
                                Icon(Icons.star_rounded, size: 16, color: Color(0xFFD97706)),
                                SizedBox(width: 8),
                                Text('Recommended for You'),
                              ],
                            ),
                          ),
                          const PopupMenuItem(
                            value: 'newest',
                            child: Text('Newest First'),
                          ),
                          const PopupMenuItem(
                            value: 'oldest',
                            child: Text('Oldest First'),
                          ),
                          const PopupMenuItem(
                            value: 'price_high',
                            child: Text('Highest Price'),
                          ),
                          const PopupMenuItem(
                            value: 'price_low',
                            child: Text('Lowest Price'),
                          ),
                        ],
                        child: Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: _selectedSort == 'recommended'
                                ? const Color(0xFFFEF3C7)
                                : const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: _selectedSort == 'recommended'
                                  ? const Color(0xFFFDE68A)
                                  : const Color(0xFFE2E8F0),
                            ),
                          ),
                          child: Icon(
                            _selectedSort == 'recommended'
                                ? Icons.star_rounded
                                : Icons.sort_rounded,
                            color: _selectedSort == 'recommended'
                                ? const Color(0xFFD97706)
                                : const Color(0xFF64748B),
                            size: 20,
                          ),
                        ),
                      ),
                    ],
                  ),

                  // Active Filter Badges Row
                  if (hasActiveFilters) ...[
                    const SizedBox(height: 10),
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          if (_searchController.text.isNotEmpty)
                            _buildActiveBadge(
                              'Query: "${_searchController.text}"',
                              () {
                                _searchController.clear();
                                _loadMarketplaceBookings();
                              },
                            ),
                          if (_filterData.bookingType != null)
                            _buildActiveBadge(
                              _filterData.bookingType == 'inspection_request'
                                  ? 'Inspection'
                                  : 'Standard',
                              () {
                                setState(() {
                                  _filterData = _filterData.copyWith(clearType: true);
                                });
                                _loadMarketplaceBookings();
                              },
                            ),
                          if (_filterData.scheduledDate != null)
                            _buildActiveBadge(
                              'Date: ${_filterData.scheduledDate}',
                              () {
                                setState(() {
                                  _filterData = _filterData.copyWith(clearDate: true);
                                });
                                _loadMarketplaceBookings();
                              },
                            ),
                          if (_filterData.minPrice != null ||
                              _filterData.maxPrice != null)
                            _buildActiveBadge(
                              'Price: ₹${_filterData.minPrice?.toStringAsFixed(0) ?? '0'} - ₹${_filterData.maxPrice?.toStringAsFixed(0) ?? 'Max'}',
                              () {
                                setState(() {
                                  _filterData = _filterData.copyWith(clearPrice: true);
                                });
                                _loadMarketplaceBookings();
                              },
                            ),
                          TextButton(
                            onPressed: _clearAllFilters,
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(horizontal: 8),
                            ),
                            child: const Text(
                              'Clear All',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFFEF4444),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            const Divider(height: 1, color: Color(0xFFF1F5F9)),

            // Content Body
            Expanded(
              child: RefreshIndicator(
                color: const Color(0xFF2563EB),
                onRefresh: _loadMarketplaceBookings,
                child: _buildBodyContent(hasActiveFilters),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const WorkerBottomNavigationBar(currentIndex: 1),
    );
  }

  Widget _buildActiveBadge(String label, VoidCallback onRemove) {
    return Container(
      margin: const EdgeInsets.only(right: 6),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFBFDBFE)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Color(0xFF2563EB),
            ),
          ),
          const SizedBox(width: 4),
          GestureDetector(
            onTap: onRemove,
            child: const Icon(Icons.close_rounded, size: 14, color: Color(0xFF2563EB)),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(top: 8.0, bottom: 12.0),
      child: Row(
        children: [
          Icon(icon, size: 18, color: color),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBodyContent(bool hasActiveFilters) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF2563EB)),
      );
    }

    if (_errorMessage != null) {
      final bool isAuthError = _errorMessage!.contains('401') ||
          _errorMessage!.contains('INVALID_TOKEN') ||
          _errorMessage!.contains('signature validation failed');

      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.18),
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isAuthError ? Icons.lock_clock_rounded : Icons.wifi_off_rounded,
                    size: 52,
                    color: isAuthError ? const Color(0xFFEF4444) : const Color(0xFF94A3B8),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    isAuthError ? 'Session Expired' : 'Connection Error',
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isAuthError
                        ? 'Your authentication token is invalid or has expired. Please log in again.'
                        : _errorMessage!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: () {
                      if (isAuthError) {
                        TokenStorage.clear();
                        Navigator.pushNamedAndRemoveUntil(
                          context,
                          AppRoutes.workerLogin,
                          (route) => false,
                        );
                      } else {
                        _loadMarketplaceBookings();
                      }
                    },
                    icon: Icon(isAuthError ? Icons.login_rounded : Icons.refresh_rounded, size: 18),
                    label: Text(isAuthError ? 'Log In Again' : 'Try Again'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    if (_bookings.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.18),
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: const BoxDecoration(
                      color: Color(0xFFF1F5F9),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.search_off_rounded,
                      size: 44,
                      color: Color(0xFF64748B),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    hasActiveFilters
                        ? 'No Matching Marketplace Jobs'
                        : 'No Marketplace Bookings',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    hasActiveFilters
                        ? 'No open bookings matched your search parameters. Try adjusting or clearing your filters.'
                        : 'There are currently no open customer bookings in your area. Pull down to refresh.',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 13,
                      color: Color(0xFF64748B),
                      height: 1.4,
                    ),
                  ),
                  if (hasActiveFilters) ...[
                    const SizedBox(height: 18),
                    OutlinedButton.icon(
                      onPressed: _clearAllFilters,
                      icon: const Icon(Icons.filter_alt_off_rounded, size: 16),
                      label: const Text('Clear All Filters'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF2563EB),
                        side: const BorderSide(color: Color(0xFFBFDBFE)),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      );
    }

    final recommendedJobs = _bookings.where((b) => b.isRecommended).toList();
    final otherJobs = _bookings.where((b) => !b.isRecommended).toList();

    // Render with section headers when recommended jobs exist
    if (_selectedSort == 'recommended' && recommendedJobs.isNotEmpty && otherJobs.isNotEmpty) {
      return ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          _buildSectionHeader('Recommended for You', Icons.star_rounded, const Color(0xFFD97706)),
          ...recommendedJobs.map((b) => MarketplaceBookingCard(
                booking: b,
                onTap: () => MarketplaceBookingDetailModal.show(context, b.id),
              )),
          const SizedBox(height: 12),
          _buildSectionHeader('Other Available Jobs', Icons.work_outline_rounded, const Color(0xFF64748B)),
          ...otherJobs.map((b) => MarketplaceBookingCard(
                booking: b,
                onTap: () => MarketplaceBookingDetailModal.show(context, b.id),
              )),
        ],
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
      physics: const AlwaysScrollableScrollPhysics(),
      itemCount: _bookings.length,
      itemBuilder: (context, index) {
        final booking = _bookings[index];
        return MarketplaceBookingCard(
          booking: booking,
          onTap: () => MarketplaceBookingDetailModal.show(context, booking.id),
        );
      },
    );
  }
}
