// File: lib/worker/jobs/navigation/navigation_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../services/booking_chat_service.dart';
import '../../../widgets/booking_chat_bottom_sheet.dart';

class WorkerNavigationScreen extends StatelessWidget {
  const WorkerNavigationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Full Screen Google Maps Placeholder
          Container(
            width: double.infinity,
            height: double.infinity,
            color: const Color(0xFFE2E8F0),
            child: Stack(
              children: [
                // Grid representation of roads/map
                GridView.builder(
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 6,
                  ),
                  itemBuilder: (ctx, idx) => Container(
                    margin: const EdgeInsets.all(1),
                    color: Colors.blueGrey.withOpacity(0.08),
                  ),
                ),

                // Curved Polyline representation
                Center(
                  child: Container(
                    width: 220,
                    height: 280,
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: const Color(0xFF2563EB),
                        width: 5,
                      ),
                      borderRadius: BorderRadius.circular(100),
                    ),
                  ),
                ),

                // Current Location Dot Marker
                const Positioned(
                  bottom: 280,
                  left: 100,
                  child: CircleAvatar(
                    radius: 12,
                    backgroundColor: Color(0xFF2563EB),
                    child: Icon(Icons.navigation_rounded,
                        color: Colors.white, size: 14),
                  ),
                ),

                // Destination Marker
                const Positioned(
                  top: 240,
                  right: 110,
                  child: Column(
                    children: [
                      Icon(Icons.location_on_rounded,
                          color: Color(0xFFEF4444), size: 36),
                      Text(
                        'Sunil Verma',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Top Header & External Maps Floating Button
          SafeArea(
            child: Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.white,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_back_rounded,
                          color: Color(0xFF0F172A)),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Opening Google Maps navigation...'),
                          backgroundColor: Color(0xFF0F172A),
                        ),
                      );
                    },
                    icon: const Icon(Icons.open_in_new_rounded, size: 16),
                    label: const Text('Open Google Maps'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0F172A),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ETA Floating Card Top Overlay
          Positioned(
            top: 90,
            left: 20,
            right: 20,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 16,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: const BoxDecoration(
                      color: Color(0xFF2563EB),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.turn_right_rounded,
                        color: Colors.white, size: 24),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'In 200m turn right onto Sector 15 Main Rd',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'ETA: 12 Mins • 2.4 Km remaining',
                          style: TextStyle(
                            fontSize: 12,
                            color: Color(0xFF94A3B8),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Bottom Navigation & Customer Action Sheet
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(28),
                  topRight: Radius.circular(28),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 20,
                    offset: Offset(0, -6),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Customer Header Row
                  Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: const BoxDecoration(
                          color: Color(0xFFDBEAFE),
                          shape: BoxShape.circle,
                        ),
                        child: const Center(
                          child: Text(
                            'SV',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Sunil Verma',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'MCB Tripping Repair • Dwarka Sector 15',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF64748B),
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.call_rounded,
                            color: Color(0xFF10B981)),
                        onPressed: () async {
                          const phone = '+919876543210';
                          await Clipboard.setData(const ClipboardData(text: phone));
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Copied phone number ($phone) to clipboard! Opening phone app...'),
                                backgroundColor: Color(0xFF10B981),
                                behavior: SnackBarBehavior.floating,
                              ),
                            );
                          }
                          final Uri launchUri = Uri(scheme: 'tel', path: phone);
                          if (await canLaunchUrl(launchUri)) {
                            await launchUrl(launchUri);
                          }
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.chat_bubble_outline_rounded,
                            color: Color(0xFF2563EB)),
                        onPressed: () {
                          final chatService = BookingChatService(
                            bookingId: 'JOB-8821',
                            currentUserId: 'worker',
                          );
                          BookingChatBottomSheet.show(context, chatService: chatService);
                        },
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Swipe to Mark Arrived Action Button
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pushNamed(
                            context, '/worker/jobs/mark-arrival');
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.location_city_rounded, size: 20),
                          SizedBox(width: 10),
                          Text(
                            'Mark Arrived at Location',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
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
}
