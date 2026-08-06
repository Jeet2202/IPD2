// File: lib/customer/onboarding/onboarding_screen2.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import 'onboarding_widgets.dart';

class OnboardingPage2 extends StatelessWidget {
  const OnboardingPage2({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      body: SafeArea(
        child: Column(
          children: [
            // ── Top Bar ──────────────────────────────────────────────
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
                          colors: [Color(0xFFF0F9FF), Color(0xFFE0F2FE)],
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
                            left: 24,
                            child: OnboardingFloatingBadge(
                              icon: Icons.check_circle_rounded,
                              iconColor: const Color(0xFF10B981),
                              label: 'Zero Hidden Cost',
                            ),
                          ),
                          Positioned(
                            bottom: 24,
                            right: 24,
                            child: OnboardingFloatingBadge(
                              icon: Icons.shield_rounded,
                              iconColor: const Color(0xFF2563EB),
                              label: 'Price Guarantee',
                            ),
                          ),
                          Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(24),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color: const Color(0xFF0EA5E9)
                                          .withOpacity(0.18),
                                      blurRadius: 28,
                                      offset: const Offset(0, 10),
                                    ),
                                  ],
                                ),
                                child: const Icon(
                                  Icons.receipt_long_rounded,
                                  size: 62,
                                  color: Color(0xFF0EA5E9),
                                ),
                              ),
                              const SizedBox(height: 16),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 18, vertical: 9),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(
                                      color: const Color(0xFFBAE6FD),
                                      width: 1.5),
                                ),
                                child: const Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text('Estimated: ',
                                        style: TextStyle(
                                            fontSize: 13,
                                            color: Color(0xFF64748B))),
                                    Text('₹299',
                                        style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.w800,
                                          color: Color(0xFF2563EB),
                                        )),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 36),

                    const Text(
                      'Transparent Pricing',
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
                      'Know estimated market prices before\nconfirming any booking. No surprises.',
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
              activePage: 1,
              totalPages: 3,
              showBack: true,
              onBack: () => Navigator.pushReplacementNamed(
                  context, '/customer/onboarding/1'),
              onNext: () => Navigator.pushReplacementNamed(
                  context, '/customer/onboarding/3'),
            ),
          ],
        ),
      ),
    );
  }
}
