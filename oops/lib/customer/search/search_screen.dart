// File:
// lib/customer/search/search_screen.dart

import 'package:flutter/material.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;
  String _query = '';

  final List<String> _recentSearches = [
    'AC Deep Cleaning',
    'Fan Repair',
    'Full House Painting',
    'Bathroom Plumber',
  ];

  final List<String> _popularSearches = [
    'Electrician near me',
    'Switchboard Fix',
    'Sofa Cleaning',
    'RO Water Purifier',
    'Leakage Repair',
    'Pest Control',
  ];

  final List<Map<String, dynamic>> _allServices = [
    {
      'name': 'Split AC Repair & Servicing',
      'category': 'AC Repair',
      'rating': '4.8',
      'reviews': '1,420',
      'price': '₹499',
      'duration': '60 mins',
      'icon': Icons.ac_unit_rounded,
      'color': const Color(0xFF0EA5E9),
    },
    {
      'name': 'Switchboard & Socket Installation',
      'category': 'Electrician',
      'rating': '4.9',
      'reviews': '2,890',
      'price': '₹199',
      'duration': '30 mins',
      'icon': Icons.bolt_rounded,
      'color': const Color(0xFF2563EB),
    },
    {
      'name': 'Pipe & Tap Leakage Fix',
      'category': 'Plumber',
      'rating': '4.7',
      'reviews': '950',
      'price': '₹299',
      'duration': '45 mins',
      'icon': Icons.plumbing_rounded,
      'color': const Color(0xFF0284C7),
    },
    {
      'name': 'Wooden Door Fitting & Repair',
      'category': 'Carpenter',
      'rating': '4.8',
      'reviews': '610',
      'price': '₹399',
      'duration': '90 mins',
      'icon': Icons.handyman_rounded,
      'color': const Color(0xFFD97706),
    },
    {
      'name': 'Interior Room Painting',
      'category': 'Painter',
      'rating': '4.9',
      'reviews': '430',
      'price': '₹999',
      'duration': '1 day',
      'icon': Icons.format_paint_rounded,
      'color': const Color(0xFFEC4899),
    },
  ];

  String _selectedSort = 'Popularity';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String value) {
    setState(() {
      _query = value;
      _isSearching = value.trim().isNotEmpty;
    });
  }

  @override
  Widget build(BuildContext context) {
    final filteredServices = _allServices
        .where((s) =>
            s['name'].toString().toLowerCase().contains(_query.toLowerCase()) ||
            s['category'].toString().toLowerCase().contains(_query.toLowerCase()))
        .toList();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        titleSpacing: 0,
        title: Padding(
          padding: const EdgeInsets.only(right: 16.0),
          child: Container(
            height: 48,
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
            ),
            child: TextField(
              controller: _searchController,
              autofocus: true,
              onChanged: _onSearchChanged,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
              decoration: InputDecoration(
                hintText: 'Search services, electrician, plumber...',
                hintStyle: const TextStyle(fontSize: 14, color: Color(0xFF94A3B8)),
                prefixIcon: const Icon(Icons.search_rounded, color: Color(0xFF2563EB), size: 22),
                suffixIcon: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (_query.isNotEmpty)
                      IconButton(
                        icon: const Icon(Icons.cancel_rounded, color: Color(0xFF94A3B8), size: 20),
                        onPressed: () {
                          _searchController.clear();
                          _onSearchChanged('');
                        },
                      ),
                    IconButton(
                      icon: const Icon(Icons.mic_none_rounded, color: Color(0xFF2563EB), size: 22),
                      onPressed: () {
                        // Voice search placeholder
                      },
                    ),
                  ],
                ),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ── Filter & Sort Bar (shown when searching) ────────────────
            if (_isSearching)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: const BoxDecoration(
                  border: Border(bottom: BorderSide(color: Color(0xFFF1F5F9), width: 1)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '${filteredServices.length} Services Found',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF475569)),
                    ),
                    Row(
                      children: [
                        _buildChipButton(
                          icon: Icons.tune_rounded,
                          label: 'Filter',
                          onTap: _showFilterBottomSheet,
                        ),
                        const SizedBox(width: 8),
                        _buildChipButton(
                          icon: Icons.sort_rounded,
                          label: _selectedSort,
                          onTap: _showSortBottomSheet,
                        ),
                      ],
                    ),
                  ],
                ),
              ),

            // ── Main Content Area ─────────────────────────────────────
            Expanded(
              child: _isSearching
                  ? (filteredServices.isEmpty ? _buildEmptyState() : _buildSearchResults(filteredServices))
                  : _buildInitialSearchSuggestions(),
            ),
          ],
        ),
      ),
    );
  }

  // ── Initial State (Recent & Popular) ──────────────────────────────────────
  Widget _buildInitialSearchSuggestions() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.all(20.0),
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
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                GestureDetector(
                  onTap: () => setState(() => _recentSearches.clear()),
                  child: const Text(
                    'Clear All',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFFEF4444)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Column(
              children: _recentSearches.map((term) {
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.history_rounded, color: Color(0xFF94A3B8), size: 20),
                  title: Text(term, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: Color(0xFF334155))),
                  trailing: const Icon(Icons.north_west_rounded, color: Color(0xFFCBD5E1), size: 16),
                  onTap: () {
                    _searchController.text = term;
                    _onSearchChanged(term);
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 24),
          ],

          // Popular Searches
          const Text(
            'Popular Searches 🔥',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 10,
            children: _popularSearches.map((term) {
              return ActionChip(
                label: Text(term),
                labelStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
                backgroundColor: const Color(0xFFF1F5F9),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: const BorderSide(color: Color(0xFFE2E8F0)),
                ),
                onPressed: () {
                  _searchController.text = term;
                  _onSearchChanged(term);
                },
              );
            }).toList(),
          ),

          const SizedBox(height: 28),

          // Suggested Services
          const Text(
            'Suggested for You',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 14),
          Column(
            children: _allServices.take(3).map((service) => _buildServiceCard(service)).toList(),
          ),
        ],
      ),
    );
  }

  // ── Search Results List ───────────────────────────────────────────────────
  Widget _buildSearchResults(List<Map<String, dynamic>> results) {
    return ListView.builder(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.all(20),
      itemCount: results.length,
      itemBuilder: (context, index) {
        return _buildServiceCard(results[index]);
      },
    );
  }

  // ── Empty Search State ─────────────────────────────────────────────────────
  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: const BoxDecoration(
                color: Color(0xFFF1F5F9),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.search_off_rounded, size: 48, color: Color(0xFF94A3B8)),
            ),
            const SizedBox(height: 20),
            const Text(
              'No services found',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 8),
            Text(
              'We couldn\'t find any matches for "$_query". Try searching with different keywords.',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: Color(0xFF64748B), height: 1.5),
            ),
          ],
        ),
      ),
    );
  }

  // ── Service Item Card Widget ───────────────────────────────────────────────
  Widget _buildServiceCard(Map<String, dynamic> service) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
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
      child: Row(
        children: [
          Container(
            width: 68,
            height: 68,
            decoration: BoxDecoration(
              color: (service['color'] as Color).withOpacity(0.12),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(service['icon'] as IconData, size: 34, color: service['color'] as Color),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  service['category'] as String,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
                ),
                const SizedBox(height: 2),
                Text(
                  service['name'] as String,
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    const Icon(Icons.star_rounded, size: 15, color: Color(0xFFFBBF24)),
                    const SizedBox(width: 4),
                    Text(
                      '${service['rating']} (${service['reviews']})',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                    ),
                    const SizedBox(width: 10),
                    const Icon(Icons.schedule_rounded, size: 14, color: Color(0xFF94A3B8)),
                    const SizedBox(width: 4),
                    Text(
                      service['duration'] as String,
                      style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                service['price'] as String,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
              ),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () {
                  // Book Service Placeholder
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  elevation: 0,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: const Text('Book', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildChipButton({required IconData icon, required String label, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0xFFF1F5F9),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Row(
          children: [
            Icon(icon, size: 14, color: const Color(0xFF334155)),
            const SizedBox(width: 6),
            Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
          ],
        ),
      ),
    );
  }

  void _showFilterBottomSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Filter Services', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
              const SizedBox(height: 16),
              const Text('Price Range', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: ['Under ₹200', '₹200 - ₹500', '₹500+'].map((p) => ChoiceChip(label: Text(p), selected: false)).toList(),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2563EB)),
                  child: const Text('Apply Filters', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showSortBottomSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Sort By', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
              const SizedBox(height: 12),
              ...['Popularity', 'Rating: High to Low', 'Price: Low to High', 'Price: High to Low'].map((sort) {
                return ListTile(
                  title: Text(sort, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                  trailing: _selectedSort == sort ? const Icon(Icons.check_rounded, color: Color(0xFF2563EB)) : null,
                  onTap: () {
                    setState(() => _selectedSort = sort);
                    Navigator.pop(context);
                  },
                );
              }),
            ],
          ),
        );
      },
    );
  }
}
