import 'dart:async';
import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../services/api_service.dart';
import '../../shared/cards/service_card.dart';
import '../../shared/utils/category_helper.dart';
import '../../shared/modals/service_filter_modal.dart';
import '../../shared/widgets/active_filter_chips_bar.dart';

class ServicesScreen extends StatefulWidget {
  const ServicesScreen({super.key});

  @override
  State<ServicesScreen> createState() => _ServicesScreenState();
}

class _ServicesScreenState extends State<ServicesScreen> {
  final ApiService _apiService = ApiService.instance;
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();
  Timer? _searchDebounce;

  List<Map<String, dynamic>> _services = [];
  bool _isLoading = true;
  bool _isLoadingMore = false;
  bool _hasMorePages = true;
  int _currentPage = 1;
  String? _errorMessage;

  String _searchQuery = '';
  ServiceFilterData _filterData = const ServiceFilterData();

  final Map<String, String> _sortOptions = {
    'display_order': 'Popularity',
    'price_asc': 'Price: Low to High',
    'price_desc': 'Price: High to Low',
    '-created_at': 'Newest First',
    'title_asc': 'A-Z',
  };

  @override
  void initState() {
    super.initState();
    _fetchServices(page: 1);
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200 &&
        !_isLoadingMore &&
        _hasMorePages &&
        !_isLoading) {
      _loadMoreServices();
    }
  }

  Future<void> _fetchServices({required int page, bool isRefresh = false}) async {
    if (page == 1 && !isRefresh) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final res = await _apiService.fetchServices(
        page: page,
        limit: 10,
        categoryId: _filterData.categoryId,
        isFeatured: _filterData.isFeatured ? true : null,
        minPrice: _filterData.minPrice,
        maxPrice: _filterData.maxPrice,
        maxDuration: _filterData.maxDuration,
        search: _searchQuery,
        sortBy: _filterData.sortBy,
      );

      final List rawItems = res['items'] as List? ?? [];
      final List<Map<String, dynamic>> items = rawItems.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      final totalPages = (res['pages'] as int?) ?? 1;

      if (!mounted) return;

      setState(() {
        if (page == 1) {
          _services = items;
        } else {
          _services.addAll(items);
        }
        _currentPage = page;
        _hasMorePages = page < totalPages;
        _isLoading = false;
        _isLoadingMore = false;
        _errorMessage = null;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _isLoadingMore = false;
        if (page == 1) {
          _errorMessage = e.message;
        }
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _isLoadingMore = false;
        if (page == 1) {
          _errorMessage = 'Unable to connect to server. Please try again.';
        }
      });
    }
  }

  Future<void> _loadMoreServices() async {
    if (_isLoadingMore || !_hasMorePages) return;

    setState(() {
      _isLoadingMore = true;
    });

    await _fetchServices(page: _currentPage + 1);
  }

  Future<void> _handleRefresh() async {
    _searchDebounce?.cancel();
    await _fetchServices(page: 1, isRefresh: true);
  }

  void _onSearchChanged(String val) {
    if (_searchDebounce?.isActive ?? false) _searchDebounce!.cancel();
    _searchDebounce = Timer(const Duration(milliseconds: 400), () {
      setState(() {
        _searchQuery = val.trim();
      });
      _fetchServices(page: 1);
    });
  }

  void _onSortSelected(String sortBy) {
    if (_filterData.sortBy == sortBy) return;
    setState(() {
      _filterData = _filterData.copyWith(sortBy: sortBy);
    });
    _fetchServices(page: 1);
  }

  void _openFilterModal() {
    ServiceFilterModal.show(
      context,
      initialData: _filterData,
      onApply: (newFilter) {
        setState(() {
          _filterData = newFilter;
        });
        _fetchServices(page: 1);
      },
    );
  }

  void _removeFilter(String filterKey) {
    setState(() {
      if (filterKey == 'sort_by') {
        _filterData = _filterData.copyWith(sortBy: 'display_order');
      } else if (filterKey == 'price') {
        _filterData = _filterData.copyWith(minPrice: () => null, maxPrice: () => null);
      } else if (filterKey == 'max_duration') {
        _filterData = _filterData.copyWith(maxDuration: () => null);
      } else if (filterKey == 'is_featured') {
        _filterData = _filterData.copyWith(isFeatured: false);
      } else if (filterKey == 'category_id') {
        _filterData = _filterData.copyWith(categoryId: () => null);
      }
    });
    _fetchServices(page: 1);
  }

  void _clearAllFilters() {
    setState(() {
      _filterData = const ServiceFilterData();
    });
    _fetchServices(page: 1);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(
        title: const Text(
          'Browse All Services',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,        elevation: 0.5,
        iconTheme: const IconThemeData(),
      ),
      body: Column(
        children: [
          // Search Bar & Filter Button
          Container(
            padding: const EdgeInsets.symmetric(horizontal: AppDimensions.md, vertical: AppDimensions.sm),
            color: Colors.white,
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        height: 44,
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                        ),
                        child: TextField(
                          controller: _searchController,
                          onChanged: _onSearchChanged,
                          style: const TextStyle(fontSize: 14),
                          decoration: InputDecoration(
                            hintText: 'Search services, e.g. Fan, Tap, Cleaning...',
                            hintStyle: const TextStyle(fontSize: 13),
                            prefixIcon: const Icon(Icons.search_rounded, size: 20),
                            suffixIcon: _searchController.text.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear_rounded, size: 18),
                                    onPressed: () {
                                      _searchController.clear();
                                      _onSearchChanged('');
                                    },
                                  )
                                : null,
                            border: InputBorder.none,
                            contentPadding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Filter Button with Badge
                    Stack(
                      children: [
                        IconButton(
                          onPressed: _openFilterModal,
                          icon: Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: _filterData.hasActiveFilters
                                  ? AppColors.primary.withValues(alpha: 0.15)
                                  : const Color(0xFFF1F5F9),
                              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                              border: Border.all(
                                color: _filterData.hasActiveFilters ? AppColors.primary : Colors.transparent,
                              ),
                            ),
                            child: Icon(
                              Icons.tune_rounded,
                              size: 20,
                              color: _filterData.hasActiveFilters ? AppColors.primary : AppColors.textPrimary,
                            ),
                          ),
                        ),
                        if (_filterData.activeFilterCount > 0)
                          Positioned(
                            right: 4,
                            top: 4,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: const BoxDecoration(
                                color: AppColors.primary,
                                shape: BoxShape.circle,
                              ),
                              child: Text(
                                '${_filterData.activeFilterCount}',
                                style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Sorting Choice Chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: _sortOptions.entries.map((entry) {
                      final isSelected = _filterData.sortBy == entry.key;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(entry.value),
                          selected: isSelected,
                          onSelected: (_) => _onSortSelected(entry.key),
                          selectedColor: AppColors.primary.withValues(alpha: 0.15),
                          backgroundColor: const Color(0xFFF1F5F9),
                          labelStyle: TextStyle(
                            fontSize: 12,
                            fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                            color: isSelected ? AppColors.primary : AppColors.textSecondary,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20),
                            side: BorderSide(
                              color: isSelected ? AppColors.primary : Colors.transparent,
                              width: 1,
                            ),
                          ),
                          showCheckmark: false,
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          // Active Filter Chips Strip
          ActiveFilterChipsBar(
            filterData: _filterData,
            onRemoveFilter: _removeFilter,
            onClearAll: _clearAllFilters,
          ),

          const Divider(height: 1, thickness: 1, color: AppColors.divider),

          // Main Content
          Expanded(
            child: RefreshIndicator(
              onRefresh: _handleRefresh,
              color: AppColors.primary,
              child: _buildMainContent(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMainContent() {
    if (_isLoading) {
      return _buildSkeletonList();
    }

    if (_errorMessage != null) {
      return _buildErrorView();
    }

    if (_services.isEmpty) {
      return _buildEmptyView();
    }

    return ListView.separated(
      controller: _scrollController,
      padding: const EdgeInsets.all(AppDimensions.md),
      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
      itemCount: _services.length + (_hasMorePages ? 1 : 0),
      separatorBuilder: (_, __) => const SizedBox(height: AppDimensions.sm),
      itemBuilder: (context, index) {
        if (index == _services.length) {
          return _buildPaginationLoader();
        }

        final srv = _services[index];
        final title = srv['title'] as String? ?? srv['name'] as String? ?? 'Service';
        final catSlug = srv['category_slug'] as String? ?? 'General';
        final srvSlug = srv['slug'] as String? ?? '';
        final priceDisplay = srv['price_range_display'] as String? ?? '₹${srv['base_price']}';
        final durationDisplay = srv['duration_display'] as String?;
        final rawImg = srv['service_image_url'] as String? ?? srv['service_image'] as String?;
        final imageUrl = (rawImg != null && rawImg.isNotEmpty)
            ? rawImg
            : CategoryHelper.getServiceImageUrl(srvSlug, catSlug, title);
        final shortDesc = srv['short_description'] as String?;
        final isFeatured = (srv['is_featured'] as bool?) ?? false;

        return ServiceCard(
          title: title,
          category: catSlug.replaceAll('-', ' '),
          price: priceDisplay,
          imageUrl: imageUrl,
          duration: durationDisplay,
          shortDescription: shortDesc,
          isFeatured: isFeatured,
          onTap: () {
            Navigator.pushNamed(
              context,
              AppRoutes.customerServiceDetail,
              arguments: {
                'service_title': title,
                'service_id': srv['id'],
              },
            );
          },
        );
      },
    );
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      padding: const EdgeInsets.all(AppDimensions.md),
      itemCount: 6,
      separatorBuilder: (_, __) => const SizedBox(height: AppDimensions.sm),
      itemBuilder: (_, __) => Container(
        height: 88,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        ),
        child: Row(
          children: [
            const SizedBox(width: 12),
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(width: 80, height: 10, color: Colors.grey.shade200),
                  const SizedBox(height: 8),
                  Container(width: 140, height: 14, color: Colors.grey.shade200),
                  const SizedBox(height: 8),
                  Container(width: 100, height: 12, color: Colors.grey.shade200),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPaginationLoader() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      alignment: Alignment.center,
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
          ),
          SizedBox(width: 10),
          Text(
            'Loading more services...',
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.6,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.cloud_off_rounded, size: 64, color: AppColors.error),
                const SizedBox(height: 16),
                const Text(
                  'Connection Error',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  _errorMessage ?? 'Unable to fetch services.',
                  style: const TextStyle(fontSize: 13),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: () => _fetchServices(page: 1),
                  icon: const Icon(Icons.refresh_rounded, size: 18),
                  label: const Text('Try Again'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyView() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.6,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.home_repair_service_outlined, size: 72, color: AppColors.textHint),
              const SizedBox(height: 16),
              const Text(
                'No matching services found.',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'We couldn\'t find any services matching your filter criteria.',
                style: TextStyle(fontSize: 13),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _clearAllFilters,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                ),
                child: const Text('Clear All Filters'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
