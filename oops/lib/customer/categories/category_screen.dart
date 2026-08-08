// File: lib/customer/categories/category_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/category_model.dart';
import '../../models/service_model.dart';
import '../../services/api_service.dart';
import '../../shared/cards/service_card.dart';
import '../../shared/modals/service_filter_modal.dart';
import '../../shared/utils/category_helper.dart';
import '../../shared/widgets/active_filter_chips_bar.dart';
import '../../l10n/app_translations.dart';

class CategoryScreen extends StatefulWidget {
  final String categoryId;
  final String categoryName;

  const CategoryScreen({
    super.key,
    this.categoryId = '',
    this.categoryName = 'Category Details',
  });

  @override
  State<CategoryScreen> createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();

  CategoryModel? _categoryDetail;
  final List<ServiceModel> _services = [];

  bool _isLoadingInitial = true;
  bool _isFetchingMore = false;
  String? _errorMessage;

  int _page = 1;
  final int _limit = 10;
  int _totalPages = 1;
  int _totalServices = 0;
  String _searchQuery = '';
  ServiceFilterData _filterData = const ServiceFilterData();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    _initialLoad();
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      if (!_isFetchingMore && _page < _totalPages && !_isLoadingInitial) {
        _fetchPage(_page + 1);
      }
    }
  }

  Future<void> _initialLoad() async {
    setState(() {
      _isLoadingInitial = true;
      _errorMessage = null;
      _services.clear();
      _page = 1;
    });

    try {
      if (widget.categoryId.isNotEmpty) {
        try {
          final catMeta = await ApiService.instance.getCategoryById(widget.categoryId);
          _categoryDetail = catMeta;
        } catch (_) {}
      }

      await _fetchPage(1, isInitial: true);
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e is ApiException ? e.message : 'Failed to load category services.';
          _isLoadingInitial = false;
        });
      }
    }
  }

  Future<void> _fetchPage(int targetPage, {bool isInitial = false}) async {
    if (!isInitial) {
      setState(() => _isFetchingMore = true);
    }

    try {
      final Map<String, dynamic> res;
      if (widget.categoryId.isNotEmpty) {
        res = await ApiService.instance.getCategoryServices(
          widget.categoryId,
          page: targetPage,
          limit: _limit,
          sortBy: _filterData.sortBy,
          isFeatured: _filterData.isFeatured ? true : null,
          minPrice: _filterData.minPrice,
          maxPrice: _filterData.maxPrice,
          maxDuration: _filterData.maxDuration,
        );
      } else {
        res = await ApiService.instance.fetchServices(
          page: targetPage,
          limit: _limit,
          sortBy: _filterData.sortBy,
          isFeatured: _filterData.isFeatured ? true : null,
          minPrice: _filterData.minPrice,
          maxPrice: _filterData.maxPrice,
          maxDuration: _filterData.maxDuration,
        );
      }

      final itemsRaw = res['items'] as List? ?? [];
      final newServices = itemsRaw.map((e) => ServiceModel.fromJson(e as Map<String, dynamic>)).toList();

      if (mounted) {
        setState(() {
          if (isInitial) {
            _services.clear();
          }
          _services.addAll(newServices);
          _page = res['page'] as int? ?? targetPage;
          _totalPages = res['pages'] as int? ?? 1;
          _totalServices = res['total'] as int? ?? _services.length;
          _isLoadingInitial = false;
          _isFetchingMore = false;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        if (isInitial) {
          setState(() {
            _errorMessage = e.message;
            _isLoadingInitial = false;
          });
        } else {
          setState(() => _isFetchingMore = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(e.message), duration: const Duration(seconds: 3)),
          );
        }
      }
    } catch (_) {
      if (mounted) {
        if (isInitial) {
          setState(() {
            _errorMessage = 'An error occurred loading services.';
            _isLoadingInitial = false;
          });
        } else {
          setState(() => _isFetchingMore = false);
        }
      }
    }
  }

  List<ServiceModel> get _filteredServices {
    if (_searchQuery.trim().isEmpty) return _services;
    final q = _searchQuery.trim().toLowerCase();
    return _services.where((s) => s.name.toLowerCase().contains(q) || s.shortDescription.toLowerCase().contains(q)).toList();
  }

  void _openFilterModal() {
    ServiceFilterModal.show(
      context,
      initialData: _filterData,
      onApply: (newFilter) {
        setState(() {
          _filterData = newFilter;
        });
        _initialLoad();
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
      }
    });
    _initialLoad();
  }

  void _clearAllFilters() {
    setState(() {
      _filterData = const ServiceFilterData();
    });
    _initialLoad();
  }

  @override
  Widget build(BuildContext context) {
    final title = _categoryDetail?.name ?? (widget.categoryName.isNotEmpty ? widget.categoryName : 'Category Services');

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Color(0xFF0F172A), size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          title,
          style: const TextStyle(color: Color(0xFF0F172A), fontSize: 18, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: Icon(
              Icons.tune_rounded,
              color: _filterData.hasActiveFilters ? const Color(0xFF2563EB) : const Color(0xFF334155),
            ),
            onPressed: _openFilterModal,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _initialLoad,
        color: const Color(0xFF2563EB),
        child: Column(
          children: [
            ActiveFilterChipsBar(
              filterData: _filterData,
              onRemoveFilter: _removeFilter,
              onClearAll: _clearAllFilters,
            ),
            Expanded(
              child: _isLoadingInitial
                  ? _buildShimmerLoading()
                  : _errorMessage != null
                      ? _buildErrorView()
                      : CustomScrollView(
                          controller: _scrollController,
                          physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                          slivers: [
                            SliverToBoxAdapter(child: _buildHeaderCard(title)),
                            SliverToBoxAdapter(child: _buildSearchBarSection()),
                            if (_filteredServices.isEmpty)
                              SliverFillRemaining(
                                hasScrollBody: false,
                                child: _buildEmptyState(),
                              )
                            else
                              SliverPadding(
                                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                                sliver: SliverList(
                                  delegate: SliverChildBuilderDelegate(
                                    (context, index) {
                                      if (index < _filteredServices.length) {
                                        return Padding(
                                          padding: const EdgeInsets.only(bottom: 14),
                                          child: _buildServiceRowCard(_filteredServices[index]),
                                        );
                                      }
                                      return _buildBottomLoader();
                                    },
                                    childCount: _filteredServices.length + (_isFetchingMore ? 1 : 0),
                                  ),
                                ),
                              ),
                          ],
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard(String title) {
    final catImage = _categoryDetail?.resolvedImage ?? CategoryHelper.getCategoryImageUrl(title);
    final catIcon = _categoryDetail?.resolvedIcon ?? CategoryHelper.getCategoryIcon(title);
    final catColor = _categoryDetail?.resolvedColor ?? CategoryHelper.getCategoryColor(title);

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [catColor, catColor.withValues(alpha: 0.85)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: catColor.withOpacity(0.3),
            blurRadius: 14,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Text(
                  '$_totalServices Available Services',
                  style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 13, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: ClipOval(
              child: Image.network(
                catImage,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Icon(catIcon, color: Colors.white, size: 28),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBarSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
      child: TextField(
        controller: _searchController,
        onChanged: (val) => setState(() => _searchQuery = val),
        decoration: InputDecoration(
          hintText: 'Filter services in this category...',
          prefixIcon: const Icon(Icons.search_rounded, color: Color(0xFF94A3B8)),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear_rounded, color: Color(0xFF94A3B8)),
                  onPressed: () {
                    _searchController.clear();
                    setState(() => _searchQuery = '');
                  },
                )
              : null,
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(vertical: 12),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
          ),
        ),
      ),
    );
  }

  Widget _buildServiceRowCard(ServiceModel service) {
    final priceDisplay = service.priceRangeDisplay.isNotEmpty ? service.priceRangeDisplay : '₹${service.basePrice.toStringAsFixed(0)}';
    final durationDisplay = service.durationDisplay.isNotEmpty ? service.durationDisplay : '${service.estimatedDurationMinutes} min';

    return ServiceCard(
      title: service.name,
      category: service.categorySlug.replaceAll('-', ' '),
      price: priceDisplay,
      imageUrl: service.resolvedImage,
      duration: durationDisplay,
      shortDescription: service.shortDescription,
      isFeatured: service.isFeatured,
      onTap: () {
        Navigator.pushNamed(
          context,
          AppRoutes.customerServiceDetail,
          arguments: {
            'service_title': service.name,
            'service_id': service.id,
          },
        );
      },
    );
  }

  Widget _buildBottomLoader() {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 16),
      child: Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(strokeWidth: 2.5, color: Color(0xFF2563EB)),
        ),
      ),
    );
  }

  Widget _buildShimmerLoading() {
    return ListView.builder(
      padding: const EdgeInsets.all(20),
      itemCount: 5,
      itemBuilder: (_, __) => Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: Container(
          height: 104,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: const BoxDecoration(
                color: Color(0xFFEFF6FF),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.inventory_2_outlined, size: 48, color: Color(0xFF2563EB)),
            ),
            const SizedBox(height: 16),
            Text('no_matching_services_found'.tr(context),
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 8),
            Text('no_services_match_your_active'.tr(context),
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
            if (_filterData.hasActiveFilters) ...[
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _clearAllFilters,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: Text('clear_all_filters'.tr(context)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 48, color: Color(0xFFEF4444)),
            const SizedBox(height: 12),
            Text('unable_to_load_category_services'.tr(context),
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 6),
            Text(
              _errorMessage ?? 'Please check your internet connection.',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _initialLoad,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: Text('try_again'.tr(context)),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
