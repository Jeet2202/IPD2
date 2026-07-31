// File:
// lib/customer/inspection_booking/inspection_intro/inspection_intro_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class InspectionIntroScreen extends StatelessWidget {
  const InspectionIntroScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Expert Inspection',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Hero Banner Card ──────────────────────────────────
                Container(
                  padding: const EdgeInsets.all(22),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1E40AF), Color(0xFF2563EB), Color(0xFF0EA5E9)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF2563EB).withOpacity(0.3),
                        blurRadius: 18,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'UNIQUE FEATURE',
                                style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white),
                              ),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'Not Sure What\'s Wrong?',
                              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.white, letterSpacing: -0.4),
                            ),
                            const SizedBox(height: 6),
                            const Text(
                              'Get a certified expert to visit, inspect, diagnose the issue & provide a transparent repair quote.',
                              style: TextStyle(fontSize: 12, color: Color(0xFFE0F2FE), height: 1.4),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.saved_search_rounded, color: Colors.white, size: 42),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ── Fee & Refund Notice Card ──────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFBFDBFE)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
                        child: const Icon(Icons.payments_rounded, color: Colors.white, size: 20),
                      ),
                      const SizedBox(width: 14),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Nominal Diagnosis Fee: ₹99',
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                            ),
                            SizedBox(height: 2),
                            Text(
                              '100% waived off when you approve the repair quotation!',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF2563EB)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ── How It Works Steps ────────────────────────────────
                const Text(
                  'How Inspection Works',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 16),

                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: const Column(
                    children: [
                      _StepItem(step: '1', title: 'Book Inspection', desc: 'Select problem category & preferred date/time slot.'),
                      SizedBox(height: 16),
                      _StepItem(step: '2', title: 'Expert Visits Site', desc: 'Certified technician arrives with diagnostic tools.'),
                      SizedBox(height: 16),
                      _StepItem(step: '3', title: 'Thorough Diagnosis', desc: 'Identifies root cause, required parts & labor.'),
                      SizedBox(height: 16),
                      _StepItem(step: '4', title: 'Digital Quotation Sent', desc: 'Receive detailed cost breakup on your app.'),
                      SizedBox(height: 16),
                      _StepItem(step: '5', title: 'Approve & Start Repair', desc: 'Repair starts only after your digital approval.'),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ── KaamSetu Guarantees ───────────────────────────────
                const Text(
                  'Why Choose KaamSetu Inspection?',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 14),

                const _BenefitRow(icon: Icons.verified_user_rounded, title: 'No Hidden Charges', desc: 'You decide whether to proceed after seeing the full quotation.'),
                const SizedBox(height: 10),
                const _BenefitRow(icon: Icons.speed_rounded, title: 'Express Arrival', desc: 'Expert arrives at your doorstep in under 45 minutes.'),
                const SizedBox(height: 10),
                const _BenefitRow(icon: Icons.shield_rounded, title: '30-Day Service Guarantee', desc: 'All diagnosed & approved repairs come with warranty.'),

                const SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Book Inspection Button ───────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.inspectionSchedule),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Book Inspection (₹99)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StepItem extends StatelessWidget {
  final String step;
  final String title;
  final String desc;

  const _StepItem({required this.step, required this.title, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
          child: Center(
            child: Text(step, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Colors.white)),
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              const SizedBox(height: 2),
              Text(desc, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.3)),
            ],
          ),
        ),
      ],
    );
  }
}

class _BenefitRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String desc;

  const _BenefitRow({required this.icon, required this.title, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF2563EB), size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                const SizedBox(height: 2),
                Text(desc, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
