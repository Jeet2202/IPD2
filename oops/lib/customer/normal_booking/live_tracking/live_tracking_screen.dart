// File:
// lib/customer/normal_booking/live_tracking/live_tracking_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class LiveTrackingScreen extends StatelessWidget {
  const LiveTrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // ── Map Canvas Placeholder ──────────────────────────────────
          Positioned.fill(
            child: Container(
              color: const Color(0xFFE2E8F0),
              child: Stack(
                children: [
                  Positioned.fill(child: CustomPaint(painter: _TrackingMapPainter())),
                  // Top Floating Back Button
                  Positioned(
                    top: 48,
                    left: 20,
                    child: GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 10),
                          ],
                        ),
                        child: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A), size: 20),
                      ),
                    ),
                  ),
                  // Top Floating Status Chip
                  Positioned(
                    top: 48,
                    right: 20,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 10),
                        ],
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.directions_bike_rounded, size: 16, color: Color(0xFF2563EB)),
                          SizedBox(width: 6),
                          Text('1.8 km away', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ── Bottom Sheet Tracking Information Card ─────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 24, offset: const Offset(0, -6)),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Handle Bar
                  Center(
                    child: Container(
                      width: 36,
                      height: 4,
                      decoration: BoxDecoration(
                        color: const Color(0xFFCBD5E1),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Arrival Banner Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Ramesh is on the way 🛵', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('Est. Arrival in 12 Minutes', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(10)),
                        child: const Text('ON TIME', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                      ),
                    ],
                  ),

                  const SizedBox(height: 18),
                  const Divider(color: Color(0xFFF1F5F9), height: 1),
                  const SizedBox(height: 16),

                  // Worker Strip
                  Row(
                    children: [
                      Container(
                        width: 50,
                        height: 50,
                        decoration: BoxDecoration(
                          color: const Color(0xFFDBEAFE),
                          shape: BoxShape.circle,
                          border: Border.all(color: const Color(0xFF2563EB), width: 1.5),
                        ),
                        child: const Icon(Icons.person_rounded, size: 30, color: Color(0xFF2563EB)),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Ramesh Kumar', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('Hero Splendor • KA-05-EX-4921', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                          child: const Icon(Icons.call_rounded, color: Color(0xFF2563EB), size: 20),
                        ),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Calling technician Ramesh Kumar (+91 9876543210)...'), backgroundColor: Color(0xFF16A34A)),
                          );
                        },
                      ),
                      IconButton(
                        icon: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                          child: const Icon(Icons.chat_bubble_outline_rounded, color: Color(0xFF2563EB), size: 20),
                        ),
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.customerChat),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Action Buttons: Share Location & Cancel
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Live tracking link copied to clipboard!')),
                            );
                          },
                          icon: const Icon(Icons.share_location_rounded, size: 18),
                          label: const Text('Share Live Status'),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            side: const BorderSide(color: Color(0xFFE2E8F0)),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            showDialog(
                              context: context,
                              builder: (ctx) => AlertDialog(
                                title: const Text('Service Start OTP'),
                                content: const Text('Share code 4829 with technician Ramesh Kumar when he arrives.'),
                                actions: [
                                  TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('OK')),
                                ],
                              ),
                            );
                          },
                          icon: const Icon(Icons.qr_code_rounded, size: 18),
                          label: const Text('Show OTP 4829'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            elevation: 0,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TrackingMapPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = const Color(0xFFCBD5E1)
      ..strokeWidth = 1;
    for (double i = 0; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), gridPaint);
    }
    for (double j = 0; j < size.height; j += 30) {
      canvas.drawLine(Offset(0, j), Offset(size.width, j), gridPaint);
    }

    // Route path line
    final routePaint = Paint()
      ..color = const Color(0xFF2563EB)
      ..strokeWidth = 5
      ..style = PaintingStyle.stroke;
    final path = Path()
      ..moveTo(size.width * 0.25, size.height * 0.3)
      ..lineTo(size.width * 0.5, size.height * 0.45)
      ..lineTo(size.width * 0.65, size.height * 0.6);
    canvas.drawPath(path, routePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
