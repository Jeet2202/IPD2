// File:
// lib/customer/inspection_booking/repair_tracking/repair_tracking_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class RepairTrackingScreen extends StatelessWidget {
  const RepairTrackingScreen({super.key});

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
          'Live Repair Progress',
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
              // ── Active Status Highlight ──────────────────────────────
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.28), blurRadius: 16, offset: const Offset(0, 6)),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), shape: BoxShape.circle),
                      child: const Icon(Icons.build_circle_rounded, color: Colors.white, size: 32),
                    ),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('REPAIR IN PROGRESS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFDBEAFE))),
                          SizedBox(height: 2),
                          Text('Replacing 32A MCB (~65%)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.white)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Worker Header ────────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: const BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                      child: const Icon(Icons.engineering_rounded, size: 28, color: Color(0xFF2563EB)),
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Sunil Verma', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('Est. 25 Mins Remaining', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                        child: const Icon(Icons.call_rounded, color: Color(0xFF2563EB), size: 18),
                      ),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Calling Inspector Sunil Verma (+91 9876543210)...'), backgroundColor: Color(0xFF16A34A)),
                        );
                      },
                    ),
                    IconButton(
                      icon: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                        child: const Icon(Icons.chat_bubble_outline_rounded, color: Color(0xFF2563EB), size: 18),
                      ),
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.customerChat),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Repair OTP Card ──────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Completion Verification OTP', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                        SizedBox(height: 2),
                        Text('8 4 9 2', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF0F172A), letterSpacing: 4)),
                      ],
                    ),
                    Icon(Icons.shield_rounded, color: Color(0xFF16A34A), size: 28),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Checklist & Progress Timeline ───────────────────────
              const Text('Active Repair Tasks', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              const SizedBox(height: 12),

              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: const Column(
                  children: [
                    _TaskRow(title: 'Inspection & Root Cause', isDone: true),
                    SizedBox(height: 12),
                    _TaskRow(title: 'Approved Revised Quotation (₹4,850)', isDone: true),
                    SizedBox(height: 12),
                    _TaskRow(title: 'Replacing burnt 32A DP MCB Breaker', isDone: false, isActive: true),
                    SizedBox(height: 12),
                    _TaskRow(title: 'Load Testing & Thermal Safety Audit', isDone: false),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.inspectionCompleted),
                  icon: const Icon(Icons.check_circle_outline_rounded, size: 20),
                  label: const Text('Complete Repair & View Summary', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF16A34A),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
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

class _TaskRow extends StatelessWidget {
  final String title;
  final bool isDone;
  final bool isActive;

  const _TaskRow({required this.title, required this.isDone, this.isActive = false});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: BoxDecoration(
            color: isDone ? const Color(0xFF16A34A) : (isActive ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: isDone
                ? const Icon(Icons.check_rounded, color: Colors.white, size: 14)
                : (isActive ? Container(width: 6, height: 6, decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle)) : null),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            title,
            style: TextStyle(
              fontSize: 13,
              fontWeight: isDone || isActive ? FontWeight.w800 : FontWeight.w500,
              color: isDone || isActive ? const Color(0xFF0F172A) : const Color(0xFF94A3B8),
            ),
          ),
        ),
      ],
    );
  }
}
