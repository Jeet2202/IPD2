// File:
// lib/customer/normal_booking/worker_assigned/worker_assigned_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class WorkerAssignedScreen extends StatelessWidget {
  const WorkerAssignedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Worker Assigned',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Top Confirmation Banner ──────────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 28),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Worker Assigned Successfully!',
                            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF14532D)),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'Your professional is preparing to depart.',
                            style: TextStyle(fontSize: 12, color: Color(0xFF15803D)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Worker Profile Card ──────────────────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Stack(
                          children: [
                            Container(
                              width: 72,
                              height: 72,
                              decoration: BoxDecoration(
                                color: const Color(0xFFDBEAFE),
                                shape: BoxShape.circle,
                                border: Border.all(color: const Color(0xFF2563EB), width: 2),
                              ),
                              child: const Icon(Icons.person_rounded, size: 44, color: Color(0xFF2563EB)),
                            ),
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: Container(
                                padding: const EdgeInsets.all(3),
                                decoration: const BoxDecoration(color: Color(0xFF16A34A), shape: BoxShape.circle),
                                child: const Icon(Icons.verified_rounded, size: 14, color: Colors.white),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(width: 16),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Ramesh Kumar',
                                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                              ),
                              SizedBox(height: 3),
                              Text(
                                'Senior Electrician • 6+ Yrs Exp',
                                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF2563EB)),
                              ),
                              SizedBox(height: 6),
                              Row(
                                children: [
                                  Icon(Icons.star_rounded, size: 16, color: Color(0xFFFBBF24)),
                                  SizedBox(width: 4),
                                  Text(
                                    '4.9',
                                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                                  ),
                                  Text(
                                    ' (420+ Jobs Completed)',
                                    style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    const SizedBox(height: 16),

                    // Quick Action Buttons Row: Call, Chat, Live Tracking
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Calling technician Ramesh Kumar (+91 9876543210)...'), backgroundColor: Color(0xFF16A34A)),
                              );
                            },
                            icon: const Icon(Icons.call_rounded, size: 18),
                            label: const Text('Call'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF2563EB),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              side: const BorderSide(color: Color(0xFF2563EB)),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => Navigator.pushNamed(context, AppRoutes.customerChat),
                            icon: const Icon(Icons.chat_bubble_outline_rounded, size: 18),
                            label: const Text('Chat'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF2563EB),
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              side: const BorderSide(color: Color(0xFF2563EB)),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => Navigator.pushNamed(context, AppRoutes.liveTracking),
                            icon: const Icon(Icons.navigation_rounded, size: 18),
                            label: const Text('Track'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF2563EB),
                              foregroundColor: Colors.white,
                              elevation: 0,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ── Arrival & Start Work OTP Banner ─────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Column(
                        children: [
                          Icon(Icons.timer_rounded, color: Color(0xFF2563EB), size: 24),
                          SizedBox(height: 4),
                          Text('18 Mins', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Work Start Verification OTP', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                          SizedBox(height: 2),
                          Text(
                            '4 8 2 9',
                            style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: Color(0xFF0F172A), letterSpacing: 6),
                          ),
                          SizedBox(height: 2),
                          Text('Share this code with Ramesh upon arrival', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ── Service Info Card ────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Service Booking Details', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                    SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Booking ID:', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                        Text('#KS-94821', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      ],
                    ),
                    SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Service:', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                        Text('Switchboard & Wiring Repair', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      ],
                    ),
                    SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Total Amount:', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                        Text('₹377 (Cash/UPI on spot)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
