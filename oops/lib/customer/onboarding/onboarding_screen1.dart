// File: lib/customer/onboarding/onboarding_screen1.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import 'onboarding_widgets.dart';

class OnboardingPage1 extends StatelessWidget {
  const OnboardingPage1({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // ── Top Bar ─────────────────────────────────────────────
            OnboardingTopBar(
              onSkip: () => Navigator.pushReplacementNamed(
                  context, AppRoutes.customerLogin),
            ),

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
                              icon: Icons.star_rounded,
                              iconColor: const Color(0xFFFBBF24),
                              label: '4.9 Rating',
                            ),
                          ),
                          Positioned(
                            bottom: 24,
                            left: 24,
                            child: OnboardingFloatingBadge(
                              icon: Icons.verified_rounded,
                              iconColor: const Color(0xFF10B981),
                              label: 'Verified Pro',
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
                              Icons.engineering_rounded,
                              size: 62,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 36),

                    const Text(
                      'Book Trusted\nProfessionals',
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
                      'Find skilled electricians, plumbers,\ncarpenters and more — at your doorstep.',
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
              activePage: 0,
              totalPages: 3,
              showBack: false,
              onNext: () => Navigator.pushReplacementNamed(
                  context, '/customer/onboarding/2'),
            ),
          ],
        ),
      ),
    );
  }
}
