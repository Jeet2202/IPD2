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

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final ApiService _apiService = ApiService.instance;
  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  Timer? _debounceTimer;

  List<Map<String, dynamic>> _searchResults = [];
  final List<String> _recentSearches = [
    'AC Deep Cleaning',
    'Fan Repair',
    'Full House Painting',
    'Bathroom Plumber',
  ];

  final List<String> _popularSearches = [
    'Electrician',
    'Switchboard Fix',
    'Sofa Cleaning',
    'RO Water Purifier',
    'Leakage Repair',
    'Pest Control',
  ];

  bool _isSearching = false;
  bool _isLoading = false;
  bool _isLoadingMore = false;
  bool _hasMorePages = true;
  int _currentPage = 1;
  int _totalResults = 0;
  String? _errorMessage;
  String _currentQuery = '';
  ServiceFilterData _filterData = const ServiceFilterData(sortBy: 'relevance');

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _searchController.dispose();
    _scrollController.removeListener(_onScroll);
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

  void _onSearchChanged(String value) {
    _debounceTimer?.cancel();
    final query = value.trim();

    if (query.isEmpty) {
      setState(() {
        _currentQuery = '';
        _isSearching = false;
        _isLoading = false;
        _searchResults.clear();
        _errorMessage = null;
      });
      return;
    }

    setState(() {
      _currentQuery = query;
      _isSearching = true;
    });

    _debounceTimer = Timer(const Duration(milliseconds: 400), () {
      _performSearch(query: query, page: 1);
    });
  }

  void _addRecentSearch(String term) {
    if (term.isEmpty) return;
    _recentSearches.removeWhere((item) => item.toLowerCase() == term.toLowerCase());
    _recentSearches.insert(0, term);
    if (_recentSearches.length > 10) {
      _recentSearches.removeLast();
    }
  }

  Future<void> _performSearch({required String query, required int page}) async {
    if (page == 1) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    } else {
      setState(() {
        _isLoadingMore = true;
      });
    }

    try {
      final res = await _apiService.searchServices(
        query: query,
        page: page,
        pageSize: 10,
        category: _filterData.categoryId,
        featured: _filterData.isFeatured ? true : null,
        minPrice: _filterData.minPrice,
        maxPrice: _filterData.maxPrice,
        maxDuration: _filterData.maxDuration,
        sortBy: _filterData.sortBy,
      );

      final List rawItems = res['items'] as List? ?? [];
      final List<Map<String, dynamic>> items = rawItems.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      final totalPages = (res['pages'] as int?) ?? 1;
      final total = (res['total'] as int?) ?? items.length;

      if (!mounted) return;

      setState(() {
        if (page == 1) {
          _searchResults = items;
          if (query.isNotEmpty && items.isNotEmpty) {
            _addRecentSearch(query);
          }
        } else {
          _searchResults.addAll(items);
        }
        _currentPage = page;
        _totalResults = total;
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
          _errorMessage = 'Unable to connect to server. Please check your network connection.';
        }
      });
    }
  }

  Future<void> _loadMoreServices() async {
    if (_isLoadingMore || !_hasMorePages) return;
    await _performSearch(query: _currentQuery, page: _currentPage + 1);
  }

  void _onSelectSearchTerm(String term) {
    _searchController.text = term;
    _searchController.selection = TextSelection.fromPosition(TextPosition(offset: term.length));
    _onSearchChanged(term);
  }

  void _openFilterModal() {
    ServiceFilterModal.show(
      context,
      initialData: _filterData,
      showCategoryFilter: true,
      onApply: (newFilter) {
        setState(() {
          _filterData = newFilter;
        });
        if (_currentQuery.isNotEmpty) {
          _performSearch(query: _currentQuery, page: 1);
        }
      },
    );
  }

  void _removeFilter(String filterKey) {
    setState(() {
      if (filterKey == 'sort_by') {
        _filterData = _filterData.copyWith(sortBy: 'relevance');
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
    if (_currentQuery.isNotEmpty) {
      _performSearch(query: _currentQuery, page: 1);
    }
  }

  void _clearAllFilters() {
    setState(() {
      _filterData = const ServiceFilterData(sortBy: 'relevance');
    });
    if (_currentQuery.isNotEmpty) {
      _performSearch(query: _currentQuery, page: 1);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: AppColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        titleSpacing: 0,
        title: Padding(
          padding: const EdgeInsets.only(right: 16.0),
          child: Container(
            height: 44,
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              border: Border.all(color: AppColors.divider),
            ),
            child: TextField(
              controller: _searchController,
              autofocus: true,
              onChanged: _onSearchChanged,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppColors.textPrimary),
              decoration: InputDecoration(
                hintText: 'Search services, e.g. Fan, Tap, Cleaning...',
                hintStyle: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                prefixIcon: const Icon(Icons.search_rounded, color: AppColors.primary, size: 20),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.cancel_rounded, color: AppColors.textSecondary, size: 18),
                        onPressed: () {
                          _searchController.clear();
                          _onSearchChanged('');
                        },
                      )
                    : null,
                border: InputBorder.none,
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            if (_isSearching)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: AppDimensions.md, vertical: AppDimensions.sm),
                color: Colors.white,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '$_totalResults Services Found',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                    ),
                    IconButton(
                      onPressed: _openFilterModal,
                      icon: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: _filterData.hasActiveFilters
                              ? AppColors.primary.withValues(alpha: 0.15)
                              : const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
                          border: Border.all(color: _filterData.hasActiveFilters ? AppColors.primary : Colors.transparent),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.tune_rounded, size: 16, color: _filterData.hasActiveFilters ? AppColors.primary : AppColors.textPrimary),
                            const SizedBox(width: 4),
                            Text(
                              'Filter & Sort',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: _filterData.hasActiveFilters ? AppColors.primary : AppColors.textPrimary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            // Active Filter Chips Bar
            ActiveFilterChipsBar(
              filterData: _filterData,
              onRemoveFilter: _removeFilter,
              onClearAll: _clearAllFilters,
            ),
            if (_isSearching) const Divider(height: 1, thickness: 1, color: AppColors.divider),
            Expanded(
              child: _isSearching ? _buildSearchResultsView() : _buildInitialSearchSuggestions(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInitialSearchSuggestions() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.all(AppDimensions.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Recent Searches
          if (_recentSearches.isNotEmpty) ...[
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Recent Searches',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                ),
                GestureDetector(
                  onTap: () => setState(() => _recentSearches.clear()),
                  child: const Text(
                    'Clear History',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.error),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Column(
              children: _recentSearches.map((term) {
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  dense: true,
                  leading: const Icon(Icons.history_rounded, color: AppColors.textHint, size: 20),
                  title: Text(term, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
                  trailing: const Icon(Icons.north_west_rounded, color: AppColors.textHint, size: 16),
                  onTap: () => _onSelectSearchTerm(term),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),
          ],

          // Popular Searches
          const Text(
            'Popular Searches 🔥',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _popularSearches.map((term) {
              return ActionChip(
                label: Text(term),
                labelStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                backgroundColor: const Color(0xFFF1F5F9),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                  side: const BorderSide(color: Colors.transparent),
                ),
                onPressed: () => _onSelectSearchTerm(term),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchResultsView() {
    if (_isLoading) {
      return _buildSkeletonList();
    }

    if (_errorMessage != null) {
      return _buildErrorView();
    }

    if (_searchResults.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.separated(
      controller: _scrollController,
      padding: const EdgeInsets.all(AppDimensions.md),
      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
      itemCount: _searchResults.length + (_hasMorePages ? 1 : 0),
      separatorBuilder: (_, __) => const SizedBox(height: AppDimensions.sm),
      itemBuilder: (context, index) {
        if (index == _searchResults.length) {
          return _buildPaginationLoader();
        }

        final srv = _searchResults[index];
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
            'Loading more matches...',
            style: TextStyle(fontSize: 13, color: AppColors.textSecondary, fontWeight: FontWeight.w500),
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
                  'Search Failed',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 8),
                Text(
                  _errorMessage ?? 'Unable to fetch search results.',
                  style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: () => _performSearch(query: _currentQuery, page: 1),
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

  Widget _buildEmptyState() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.6,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.search_off_rounded, size: 72, color: AppColors.textHint),
                const SizedBox(height: 16),
                const Text(
                  'No matching services found',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 8),
                Text(
                  'We couldn\'t find any matches for "$_currentQuery". Try clearing your active filters or searching for another term.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                ),
                if (_filterData.hasActiveFilters) ...[
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
              ],
            ),
          ),
        ),
      ),
    );
  }
}
