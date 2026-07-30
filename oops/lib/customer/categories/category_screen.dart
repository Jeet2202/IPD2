// File:
// lib/customer/categories/category_screen.dart

import 'package:flutter/material.dart';

class CategoryScreen extends StatefulWidget {
  final String categoryName;
  const CategoryScreen({
    super.key,
    this.categoryName = 'Electrician',
  });

  @override
  State<CategoryScreen> createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  final TextEditingController _categorySearchController = TextEditingController();
  String _selectedSubCategory = 'All';

  final List<String> _subCategories = [
    'All',
    'Switch & Socket',
    'Fan & Light',
    'MCB & Wiring',
    'Appliance Setup',
  ];

  final List<Map<String, dynamic>> _categoryServices = [
    {
      'name': 'Switchboard Repair & Fitting',
      'subCategory': 'Switch & Socket',
      'price': '₹149',
      'duration': '30 mins',
      'rating': '4.8',
      'reviews': '1,240',
      'description': 'Repairing loose connections, faulty switches or installing new modular switchboards.',
      'icon': Icons.bolt_rounded,
      'color': const Color(0xFF2563EB),
    },
    {
      'name': 'Ceiling Fan Installation & Repair',
      'subCategory': 'Fan & Light',
      'price': '₹199',
      'duration': '45 mins',
      'rating': '4.9',
      'reviews': '2,150',
      'description': 'Complete assembly, downrod installation, regulator fix, and quiet operation setup.',
      'icon': Icons.toys_rounded,
      'color': const Color(0xFF0EA5E9),
    },
    {
      'name': 'MCB Change & Fuse Repair',
      'subCategory': 'MCB & Wiring',
      'price': '₹299',
      'duration': '40 mins',
      'rating': '4.7',
      'reviews': '820',
      'description': 'Single pole / double pole MCB replacement to resolve frequent tripping and short circuits.',
      'icon': Icons.power_rounded,
      'color': const Color(0xFFD97706),
    },
    {
      'name': 'LED Chandelier & Decorative Lighting',
      'subCategory': 'Fan & Light',
      'price': '₹399',
      'duration': '60 mins',
      'rating': '4.8',
      'reviews': '450',
      'description': 'Safe hanging, electrical wiring connection, and ceiling anchor fixing for heavy lights.',
      'icon': Icons.light_rounded,
      'color': const Color(0xFF8B5CF6),
    },
    {
      'name': 'Inverter & Battery Setup',
      'subCategory': 'Appliance Setup',
      'price': '₹499',
      'duration': '60 mins',
      'rating': '4.9',
      'reviews': '960',
      'description': 'Heavy wire connection, main distribution board bypass, and water level check.',
      'icon': Icons.battery_charging_full_rounded,
      'color': const Color(0xFF10B981),
    },
  ];

  @override
  void dispose() {
    _categorySearchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filteredServices = _categoryServices.where((service) {
      final matchesSub = _selectedSubCategory == 'All' || service['subCategory'] == _selectedSubCategory;
      final matchesQuery = service['name'].toString().toLowerCase().contains(_categorySearchController.text.toLowerCase());
      return matchesSub && matchesQuery;
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '${widget.categoryName} Services',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined, color: Color(0xFF0F172A)),
            onPressed: () {},
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ── Category Promo Banner ──────────────────────────────────
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF1E40AF), Color(0xFF3B82F6)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF2563EB).withOpacity(0.28),
                            blurRadius: 16,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Certified Electricians',
                                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.white),
                                ),
                                SizedBox(height: 6),
                                Text(
                                  'Background verified • 30-Day warranty on repairs',
                                  style: TextStyle(fontSize: 12, color: Color(0xFFDBEAFE), height: 1.4),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.verified_user_rounded, color: Colors.white, size: 36),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // ── Category Search Bar ──────────────────────────────────
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
                      ),
                      child: TextField(
                        controller: _categorySearchController,
                        onChanged: (_) => setState(() {}),
                        style: const TextStyle(fontSize: 14, color: Color(0xFF0F172A)),
                        decoration: const InputDecoration(
                          hintText: 'Search within Electrician...',
                          hintStyle: TextStyle(fontSize: 14, color: Color(0xFF94A3B8)),
                          prefixIcon: Icon(Icons.search_rounded, color: Color(0xFF2563EB), size: 20),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(vertical: 14),
                        ),
                      ),
                    ),

                    const SizedBox(height: 16),

                    // ── Sub-Categories Filter Chips ──────────────────────────
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      physics: const BouncingScrollPhysics(),
                      child: Row(
                        children: _subCategories.map((sub) {
                          final isSelected = sub == _selectedSubCategory;
                          return Padding(
                            padding: const EdgeInsets.only(right: 8.0),
                            child: FilterChip(
                              label: Text(sub),
                              selected: isSelected,
                              labelStyle: TextStyle(
                                fontSize: 13,
                                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                                color: isSelected ? Colors.white : const Color(0xFF475569),
                              ),
                              backgroundColor: Colors.white,
                              selectedColor: const Color(0xFF2563EB),
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                                side: BorderSide(
                                  color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
                                ),
                              ),
                              onSelected: (_) => setState(() => _selectedSubCategory = sub),
                            ),
                          );
                        }).toList(),
                      ),
                    ),

                    const SizedBox(height: 20),

                    // ── Services Section Title ────────────────────────────────
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Available Services (${filteredServices.length})',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        ),
                        const Row(
                          children: [
                            Icon(Icons.tune_rounded, size: 16, color: Color(0xFF64748B)),
                            SizedBox(width: 4),
                            Text('Filter', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF64748B))),
                          ],
                        ),
                      ],
                    ),

                    const SizedBox(height: 14),

                    // ── Service Cards List ────────────────────────────────────
                    ...filteredServices.map((service) => _buildServiceCard(service)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Service Card Item Widget ───────────────────────────────────────────────
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
            color: Colors.black.withOpacity(0.03),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: (service['color'] as Color).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(service['icon'] as IconData, size: 30, color: service['color'] as Color),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      service['name'] as String,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.star_rounded, size: 15, color: Color(0xFFFBBF24)),
                        const SizedBox(width: 3),
                        Text(
                          '${service['rating']} (${service['reviews']})',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF334155)),
                        ),
                        const SizedBox(width: 10),
                        const Icon(Icons.schedule_rounded, size: 14, color: Color(0xFF94A3B8)),
                        const SizedBox(width: 3),
                        Text(
                          service['duration'] as String,
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),
          Text(
            service['description'] as String,
            style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),

          const SizedBox(height: 14),
          const Divider(color: Color(0xFFF1F5F9), height: 1),
          const SizedBox(height: 12),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Starts at', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                  Text(
                    service['price'] as String,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                  ),
                ],
              ),
              ElevatedButton(
                onPressed: () {
                  // Navigate to Service Details or Selection
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  elevation: 0,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: const Text('Book Now', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
