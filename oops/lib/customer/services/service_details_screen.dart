// File:
// lib/customer/services/service_details_screen.dart

import 'package:flutter/material.dart';

class ServiceDetailsScreen extends StatefulWidget {
  final String serviceTitle;
  const ServiceDetailsScreen({
    super.key,
    this.serviceTitle = 'Split AC Service & Inspection',
  });

  @override
  State<ServiceDetailsScreen> createState() => _ServiceDetailsScreenState();
}

class _ServiceDetailsScreenState extends State<ServiceDetailsScreen> {
  bool _isBookmarked = false;

  final List<String> _whatsIncluded = [
    'Deep cleaning of indoor cooling coils & filter',
    'Outdoor unit high-pressure jet washing',
    'Gas pressure check & leak check inspection',
    'Drain pipe flushing and clearing blockages',
  ];

  final List<String> _whatsNotIncluded = [
    'Spare parts replacement (charged separately if needed)',
    'Gas refilling (can be added separately if pressure low)',
    'Major copper pipe repair works',
  ];

  final List<Map<String, dynamic>> _whyChooseUs = [
    {'title': '30-Day Guarantee', 'subtitle': 'Free re-service if issue persists', 'icon': Icons.shield_rounded},
    {'title': 'Verified Pros', 'subtitle': 'Background checked technicians', 'icon': Icons.verified_user_rounded},
    {'title': 'Transparent Price', 'subtitle': 'Standardized rate card', 'icon': Icons.receipt_long_rounded},
  ];

  final List<Map<String, String>> _reviews = [
    {
      'name': 'Vikram Singh',
      'rating': '5.0',
      'date': '2 days ago',
      'comment': 'Awesome cooling performance after service! The professional arrived right on time and cleaned everything neatly.',
    },
    {
      'name': 'Ananya Roy',
      'rating': '4.8',
      'date': '1 week ago',
      'comment': 'Thorough inspection and jet cleaning. Very polite behavior.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // ── Scrollable Body Content ─────────────────────────────────
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Service Hero Banner ────────────────────────────────
                Stack(
                  children: [
                    Container(
                      height: 260,
                      width: double.infinity,
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Positioned.fill(
                            child: Opacity(
                              opacity: 0.15,
                              child: CustomPaint(painter: _GridBackgroundPainter()),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.all(28),
                            decoration: BoxDecoration(
                              color: const Color(0xFF2563EB).withOpacity(0.2),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.ac_unit_rounded,
                              size: 72,
                              color: Color(0xFF0EA5E9),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Top Custom App Bar Overlay
                    Positioned(
                      top: 44,
                      left: 16,
                      right: 16,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildCircleIconButton(
                            icon: Icons.arrow_back_rounded,
                            onTap: () => Navigator.pop(context),
                          ),
                          Row(
                            children: [
                              _buildCircleIconButton(
                                icon: _isBookmarked ? Icons.bookmark_rounded : Icons.bookmark_border_rounded,
                                iconColor: _isBookmarked ? const Color(0xFF2563EB) : const Color(0xFF0F172A),
                                onTap: () => setState(() => _isBookmarked = !_isBookmarked),
                              ),
                              const SizedBox(width: 10),
                              _buildCircleIconButton(
                                icon: Icons.share_outlined,
                                onTap: () {},
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                // ── Main Card Overlay Details ───────────────────────────
                Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Badge
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'AC REPAIR & SERVICE',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                        ),
                      ),
                      const SizedBox(height: 8),

                      // Title
                      Text(
                        widget.serviceTitle,
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(height: 12),

                      // Stats Row
                      Row(
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.star_rounded, size: 18, color: Color(0xFFFBBF24)),
                              const SizedBox(width: 4),
                              const Text('4.8', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                              const Text(' (2.4k reviews)', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                            ],
                          ),
                          const SizedBox(width: 16),
                          Container(width: 4, height: 4, decoration: const BoxDecoration(color: Color(0xFFCBD5E1), shape: BoxShape.circle)),
                          const SizedBox(width: 16),
                          const Text('1,800+ Jobs', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF10B981))),
                        ],
                      ),

                      const SizedBox(height: 16),

                      // Price & Duration Banner Card
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Starting Price', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                                SizedBox(height: 2),
                                Text('₹499', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                              ],
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text('Est. Duration', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                                SizedBox(height: 4),
                                Row(
                                  children: [
                                    Icon(Icons.schedule_rounded, size: 16, color: Color(0xFF0F172A)),
                                    SizedBox(width: 4),
                                    Text('45 - 60 Mins', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 28),

                      // ── About Section ─────────────────────────────────────
                      _buildSectionTitle('About Service'),
                      const SizedBox(height: 8),
                      const Text(
                        'Complete foam & jet power service for split air conditioners. Cleans deep embedded dirt from cooling coils and improves cooling efficiency while reducing power consumption.',
                        style: TextStyle(fontSize: 14, color: Color(0xFF475569), height: 1.6),
                      ),

                      const SizedBox(height: 28),

                      // ── What's Included ───────────────────────────────────
                      _buildSectionTitle('What\'s Included'),
                      const SizedBox(height: 12),
                      Column(
                        children: _whatsIncluded.map((item) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10.0),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(color: Color(0xFFDCFCE7), shape: BoxShape.circle),
                                  child: const Icon(Icons.check_rounded, size: 14, color: Color(0xFF16A34A)),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Text(item, style: const TextStyle(fontSize: 14, color: Color(0xFF334155)))),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 24),

                      // ── What's Not Included ───────────────────────────────
                      _buildSectionTitle('What\'s Not Included'),
                      const SizedBox(height: 12),
                      Column(
                        children: _whatsNotIncluded.map((item) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10.0),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(color: Color(0xFFFEE2E2), shape: BoxShape.circle),
                                  child: const Icon(Icons.close_rounded, size: 14, color: Color(0xFFDC2626)),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Text(item, style: const TextStyle(fontSize: 14, color: Color(0xFF64748B)))),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 28),

                      // ── Why Choose Us ──────────────────────────────────────
                      _buildSectionTitle('Why Choose KaamSetu?'),
                      const SizedBox(height: 14),
                      Column(
                        children: _whyChooseUs.map((feature) {
                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF8FAFC),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(10),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF2563EB).withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Icon(feature['icon'] as IconData, color: const Color(0xFF2563EB), size: 22),
                                ),
                                const SizedBox(width: 14),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(feature['title'] as String, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                                    const SizedBox(height: 2),
                                    Text(feature['subtitle'] as String, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                                  ],
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 28),

                      // ── Customer Reviews ──────────────────────────────────
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildSectionTitle('Customer Reviews'),
                          TextButton(
                            onPressed: () {},
                            child: const Text('See All', style: TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ..._reviews.map((rev) {
                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(rev['name']!, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                                  Row(
                                    children: [
                                      const Icon(Icons.star_rounded, size: 14, color: Color(0xFFFBBF24)),
                                      const SizedBox(width: 3),
                                      Text(rev['rating']!, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                                    ],
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Text(rev['comment']!, style: const TextStyle(fontSize: 13, color: Color(0xFF475569), height: 1.4)),
                            ],
                          ),
                        );
                      }),

                      const SizedBox(height: 100), // Bottom padding for sticky buttons
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── Sticky Bottom Action Bar ─────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.08),
                    blurRadius: 20,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {
                        // Inspection Booking Placeholder
                      },
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        side: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: const Text(
                        'Need Inspection',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        // Direct Booking Flow Placeholder
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: const Text(
                        'Book Service',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A), letterSpacing: -0.4),
    );
  }

  Widget _buildCircleIconButton({
    required IconData icon,
    Color iconColor = const Color(0xFF0F172A),
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 10),
          ],
        ),
        child: Icon(icon, size: 20, color: iconColor),
      ),
    );
  }
}

class _GridBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..strokeWidth = 1;
    for (double i = 0; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double j = 0; j < size.height; j += 30) {
      canvas.drawLine(Offset(0, j), Offset(size.width, j), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
