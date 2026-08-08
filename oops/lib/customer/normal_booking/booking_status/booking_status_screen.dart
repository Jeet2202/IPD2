// File:
// lib/customer/normal_booking/booking_status/booking_status_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class BookingStatusScreen extends StatelessWidget {
  const BookingStatusScreen({super.key});

  final List<Map<String, dynamic>> _timelineSteps = [
    {
      'title': 'Booking Confirmed',
      'time': '10:15 AM',
      'desc': 'Service request received & accepted.',
      'status': 'completed',
    },
    {
      'title': 'Professional Assigned',
      'time': '10:16 AM',
      'desc': 'Ramesh Kumar accepted the task.',
      'status': 'completed',
    },
    {
      'title': 'Worker On The Way',
      'time': '10:20 AM',
      'desc': 'Technician is en route (1.8 km away).',
      'status': 'completed',
    },
    {
      'title': 'Work In Progress',
      'time': '10:35 AM',
      'desc': 'OTP verified & electrical repair started.',
      'status': 'active',
    },
    {
      'title': 'Work Completed & Review',
      'time': 'Pending',
      'desc': 'Inspection & final bill generation.',
      'status': 'pending',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('live_booking_status'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Active Status Highlight Card ─────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.28), blurRadius: 16, offset: const Offset(0, 8)),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), shape: BoxShape.circle),
                      child: Icon(Icons.engineering_rounded, color: Colors.white, size: 32),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('current_status'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFDBEAFE))),
                          SizedBox(height: 2),
                          Text('work_in_progress'.tr(context), style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.white)),
                          SizedBox(height: 2),
                          Text('ramesh_is_currently_replacing_switchboard'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFFE0F2FE))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Timeline Header ──────────────────────────────────────
              Text('service_progress_timeline'.tr(context),
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
              SizedBox(height: 16),

              // ── Vertical Timeline ────────────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: List.generate(_timelineSteps.length, (index) {
                    final step = _timelineSteps[index];
                    final isLast = index == _timelineSteps.length - 1;
                    final isCompleted = step['status'] == 'completed';
                    final isActive = step['status'] == 'active';

                    return IntrinsicHeight(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Timeline Dot & Line Column
                          Column(
                            children: [
                              Container(
                                width: 28,
                                height: 28,
                                decoration: BoxDecoration(
                                  color: isCompleted
                                      ? const Color(0xFF16A34A)
                                      : (isActive ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                                  shape: BoxShape.circle,
                                ),
                                child: Center(
                                  child: isCompleted
                                      ? Icon(Icons.check_rounded, color: Colors.white, size: 16)
                                      : (isActive
                                          ? Container(width: 10, height: 10, decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle))
                                          : null),
                                ),
                              ),
                              if (!isLast)
                                Expanded(
                                  child: Container(
                                    width: 2,
                                    margin: EdgeInsets.symmetric(vertical: 4),
                                    color: isCompleted ? const Color(0xFF16A34A) : const Color(0xFFE2E8F0),
                                  ),
                                ),
                            ],
                          ),

                          SizedBox(width: 16),

                          // Content Column
                          Expanded(
                            child: Padding(
                              padding: EdgeInsets.only(bottom: 20.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        step['title'] as String,
                                        style: TextStyle(
                                          fontSize: 15,
                                          fontWeight: isActive || isCompleted ? FontWeight.w800 : FontWeight.w600,
                                          color: isActive || isCompleted ? const Color(0xFF0F172A) : const Color(0xFF94A3B8),
                                        ),
                                      ),
                                      Text(
                                        step['time'] as String,
                                        style: TextStyle(
                                          fontSize: 11,
                                          fontWeight: FontWeight.w700,
                                          color: isActive ? const Color(0xFF2563EB) : const Color(0xFF94A3B8),
                                        ),
                                      ),
                                    ],
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    step['desc'] as String,
                                    style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ),
              ),

              SizedBox(height: 24),

              // ── Support & Emergency Button Row ────────────────────────
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: Icon(Icons.help_outline_rounded, size: 18),
                      label: Text('get_support'.tr(context)),
                      style: OutlinedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 14),
                        side: BorderSide(color: Color(0xFF2563EB)),
                        foregroundColor: const Color(0xFF2563EB),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {},
                      icon: Icon(Icons.sos_rounded, size: 18),
                      label: Text('emergency_sos'.tr(context)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFEF4444),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
