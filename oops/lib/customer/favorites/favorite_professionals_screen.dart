// File:
// lib/customer/favorites/favorite_professionals_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../l10n/app_translations.dart';

class FavoriteProfessionalsScreen extends StatefulWidget {
  const FavoriteProfessionalsScreen({super.key});

  @override
  State<FavoriteProfessionalsScreen> createState() => _FavoriteProfessionalsScreenState();
}

class _FavoriteProfessionalsScreenState extends State<FavoriteProfessionalsScreen> {
  final List<Map<String, dynamic>> _favorites = [
    {
      'id': '1',
      'name': 'Sunil Verma',
      'profession': 'Master Electrician',
      'rating': '4.95',
      'jobs': '142 Jobs',
      'experience': '8 Yrs Exp',
      'distance': '1.8 km away',
      'available': 'Available Today',
    },
    {
      'id': '2',
      'name': 'Ramesh Kumar',
      'profession': 'Senior AC Technician',
      'rating': '4.88',
      'jobs': '98 Jobs',
      'experience': '6 Yrs Exp',
      'distance': '2.4 km away',
      'available': 'Available Tomorrow',
    },
    {
      'id': '3',
      'name': 'Suresh Patel',
      'profession': 'Plumbing Specialist',
      'rating': '4.92',
      'jobs': '210 Jobs',
      'experience': '10 Yrs Exp',
      'distance': '3.1 km away',
      'available': 'Available Today',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('favorite_professionals'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              // ── Search Input ─────────────────────────────────────────
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.search_rounded, color: Color(0xFF64748B)),
                    SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Search saved technicians...',
                          hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                          border: InputBorder.none,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ── Favorite Cards List ──────────────────────────────────
              _favorites.isEmpty
                  ? _buildEmptyState()
                  : Column(
                      children: List.generate(_favorites.length, (index) {
                        final fav = _favorites[index];
                        return Container(
                          margin: const EdgeInsets.only(bottom: 16),
                          padding: const EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(22),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                            boxShadow: [
                              BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4)),
                            ],
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    width: 50,
                                    height: 50,
                                    decoration: const BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                                    child: const Icon(Icons.engineering_rounded, color: Color(0xFF2563EB), size: 28),
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Text(fav['name'] as String, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                                            IconButton(
                                              icon: const Icon(Icons.favorite_rounded, color: Color(0xFFEF4444), size: 20),
                                              onPressed: () {
                                                setState(() => _favorites.removeAt(index));
                                              },
                                            ),
                                          ],
                                        ),
                                        Text('${fav['profession']} • ${fav['experience']}', style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                                      ],
                                    ),
                                  ),
                                ],
                              ),

                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  const Icon(Icons.star_rounded, color: Color(0xFFFBBF24), size: 16),
                                  const SizedBox(width: 4),
                                  Text(fav['rating'] as String, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                                  const SizedBox(width: 4),
                                  Text('(${fav['jobs']})', style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                                  const Spacer(),
                                  Text(fav['distance'] as String, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                                ],
                              ),

                              const SizedBox(height: 14),
                              const Divider(color: Color(0xFFF1F5F9), height: 1),
                              const SizedBox(height: 12),

                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
                                    child: Text(fav['available'] as String, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                                  ),
                                  ElevatedButton(
                                    onPressed: () => Navigator.pushNamed(context, AppRoutes.customerServices),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: const Color(0xFF2563EB),
                                      foregroundColor: Colors.white,
                                      elevation: 0,
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                    ),
                                    child: Text('book_again'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        );
                      }),
                    ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 40),
        child: Column(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: const BoxDecoration(color: Color(0xFFFEF2F2), shape: BoxShape.circle),
              child: const Icon(Icons.favorite_border_rounded, color: Color(0xFFEF4444), size: 40),
            ),
            const SizedBox(height: 16),
            Text('no_favorite_professionals_yet'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
            const SizedBox(height: 6),
            Text('start_adding_your_trusted_professionals'.tr(context), textAlign: TextAlign.center, style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
          ],
        ),
      ),
    );
  }
}
