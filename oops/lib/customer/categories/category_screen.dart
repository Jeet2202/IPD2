// File: lib/customer/categories/category_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/category_model.dart';
import '../../models/service_model.dart';
import '../../services/api_service.dart';

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
  String _selectedSortBy = 'display_order';
  String _searchQuery = '';

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
      // 1. Fetch category meta if ID is provided
      if (widget.categoryId.isNotEmpty) {
        try {
          final catMeta = await ApiService.instance.getCategoryById(widget.categoryId);
          _categoryDetail = catMeta;
        } catch (_) {}
      }

      // 2. Fetch page 1 services
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
    if (widget.categoryId.isEmpty) {
      if (mounted) {
        setState(() {
          _isLoadingInitial = false;
          _isFetchingMore = false;
        });
      }
      return;
    }

    if (!isInitial) {
      setState(() => _isFetchingMore = true);
    }

    try {
      final res = await ApiService.instance.getCategoryServices(
        widget.categoryId,
        page: targetPage,
        limit: _limit,
        sortBy: _selectedSortBy,
      );

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
    } catch (e) {
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

  @override
  Widget build(BuildContext context) {
    final title = _categoryDetail?.name ?? (widget.categoryName.isNotEmpty ? widget.categoryName : 'Category Services');

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Color(0xFF0F172A), size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          title,
          style: const TextStyle(color: Color(0xFF0F172A), fontSize: 18, fontWeight: FontWeight.bold),
        ),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort_rounded, color: Color(0xFF334155)),
            onSelected: (val) {
              if (val != _selectedSortBy) {
                setState(() => _selectedSortBy = val);
                _initialLoad();
              }
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'display_order', child: Text('Default Order')),
              PopupMenuItem(value: 'price_asc', child: Text('Price: Low to High')),
              PopupMenuItem(value: 'price_desc', child: Text('Price: High to Low')),
              PopupMenuItem(value: '-created_at', child: Text('Newest First')),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _initialLoad,
        color: const Color(0xFF2563EB),
        child: _isLoadingInitial
            ? _buildShimmerLoading()
            : _errorMessage != null
                ? _buildErrorView()
                : CustomScrollView(
                    controller: _scrollController,
                    physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                    slivers: [
                      // Header Card Section
                      SliverToBoxAdapter(child: _buildHeaderCard(title)),

                      // Search Bar Section
                      SliverToBoxAdapter(child: _buildSearchBarSection()),

                      // Services Grid / List Section
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
    );
  }

  // ── Header Card ────────────────────────────────────────────────────────────
  Widget _buildHeaderCard(String title) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E40AF), Color(0xFF3B82F6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF2563EB).withOpacity(0.3),
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
            child: _categoryDetail?.image.isNotEmpty == true
                ? ClipOval(
                    child: Image.network(
                      _categoryDetail!.image,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => const Icon(Icons.home_repair_service_rounded, color: Colors.white, size: 28),
                    ),
                  )
                : const Icon(Icons.home_repair_service_rounded, color: Colors.white, size: 28),
          ),
        ],
      ),
    );
  }

  // ── Search Bar Section ──────────────────────────────────────────────────────
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

  // ── Service Row Card ───────────────────────────────────────────────────────
  Widget _buildServiceRowCard(ServiceModel service) {
    return GestureDetector(
      onTap: () => Navigator.pushNamed(
        context,
        AppRoutes.serviceSelection,
        arguments: {'service_id': service.id, 'service_name': service.name},
      ),
      child: Container(
        padding: const EdgeInsets.all(12),
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
            // Image
            Container(
              width: 90,
              height: 90,
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(12),
              ),
              child: service.image.isNotEmpty
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.network(
                        service.image,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const Icon(Icons.build_rounded, color: Color(0xFF94A3B8), size: 36),
                      ),
                    )
                  : const Icon(Icons.build_rounded, color: Color(0xFF94A3B8), size: 36),
            ),
            const SizedBox(width: 14),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          service.name,
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (service.isFeatured)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFDBEAFE),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text(
                            'FEATURED',
                            style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF2563EB)),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    service.shortDescription.isNotEmpty ? service.shortDescription : 'Professional home service',
                    style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        service.priceRangeDisplay.isNotEmpty ? service.priceRangeDisplay : '₹${service.basePrice.toStringAsFixed(0)}',
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF2563EB)),
                      ),
                      Row(
                        children: [
                          const Icon(Icons.access_time_rounded, size: 13, color: Color(0xFF64748B)),
                          const SizedBox(width: 3),
                          Text(
                            service.durationDisplay.isNotEmpty ? service.durationDisplay : '${service.estimatedDurationMinutes} min',
                            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
                          ),
                        ],
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
  }

  // ── Bottom Pagination Spinner ──────────────────────────────────────────────
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

  // ── Shimmer Initial Loading State ──────────────────────────────────────────
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

  // ── Empty State View ───────────────────────────────────────────────────────
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
            const Text(
              'No Services Found',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 8),
            const Text(
              'No services are available under this category at the moment. Please check back later.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
          ],
        ),
      ),
    );
  }

  // ── Error View with Retry ──────────────────────────────────────────────────
  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 48, color: Color(0xFFEF4444)),
            const SizedBox(height: 12),
            const Text(
              'Unable to Load Category Services',
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
      ),
    );
  }
}
