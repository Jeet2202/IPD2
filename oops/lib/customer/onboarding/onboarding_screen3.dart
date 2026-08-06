// File: lib/customer/onboarding/onboarding_screen3.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import 'onboarding_widgets.dart';

class OnboardingPage3 extends StatelessWidget {
  const OnboardingPage3({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      body: SafeArea(
        child: Column(
          children: [
            // ── Top Bar (no skip on last page) ───────────────────────
            const OnboardingTopBar(onSkip: null),

            // ── Illustration ─────────────────────────────────────────
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  children: [
                    const SizedBox(height: 8),
                    Container(
                      height: 270,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFEFF6FF), Color(0xFFDBEAFE)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(28),
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Positioned(
                            top: 22,
                            right: 24,
                            child: OnboardingFloatingBadge(
                              icon: Icons.search_rounded,
                              iconColor: const Color(0xFF2563EB),
                              label: 'Find Issues Fast',
                            ),
                          ),
                          Positioned(
                            bottom: 24,
                            left: 24,
                            child: OnboardingFloatingBadge(
                              icon: Icons.fact_check_rounded,
                              iconColor: const Color(0xFF10B981),
                              label: 'Diagnose First',
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF2563EB).withOpacity(0.18),
                                  blurRadius: 28,
                                  offset: const Offset(0, 10),
                                ),
                              ],
                            ),
                            child: const Icon(
                              Icons.manage_search_rounded,
                              size: 62,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 36),

                    const Text(
                      'Inspection Before\nRepair',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                        letterSpacing: -0.6,
                        height: 1.25,
                      ),
                    ),

                    const SizedBox(height: 14),

                    const Text(
                      'Not sure what\'s wrong? Book an inspection.\nLet professionals diagnose before repair.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w400,
                        color: Color(0xFF64748B),
                        height: 1.6,
                      ),
                    ),

                    const SizedBox(height: 28),
                  ],
                ),
              ),
            ),

            // ── Bottom Navigation ────────────────────────────────────
            OnboardingBottomNav(
              activePage: 2,
              totalPages: 3,
              showBack: true,
              nextLabel: 'Get Started',
              onBack: () => Navigator.pushReplacementNamed(
                  context, '/customer/onboarding/2'),
              onNext: () => Navigator.pushReplacementNamed(
                  context, AppRoutes.customerLogin),
            ),
          ],
        ),
      ),
    );
  }
}
