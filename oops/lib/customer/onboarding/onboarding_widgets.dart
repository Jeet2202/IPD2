// File: lib/customer/onboarding/onboarding_widgets.dart
// Shared widgets used across all onboarding screens.

import 'package:flutter/material.dart';

// ── Floating Badge ────────────────────────────────────────────────────────────
class OnboardingFloatingBadge extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String label;

  const OnboardingFloatingBadge({
    super.key,
    required this.icon,
    required this.iconColor,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.07),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: iconColor),
          const SizedBox(width: 5),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Bottom Navigation Bar ─────────────────────────────────────────────────────
class OnboardingBottomNav extends StatelessWidget {
  final int activePage;
  final int totalPages;
  final VoidCallback onNext;
  final VoidCallback? onBack;
  final bool showBack;
  final String nextLabel;

  const OnboardingBottomNav({
    super.key,
    required this.activePage,
    required this.totalPages,
    required this.onNext,
    this.onBack,
    this.showBack = true,
    this.nextLabel = 'Next',
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 28),
      decoration: const BoxDecoration(
        color: Colors.white,
        border: Border(
          top: BorderSide(color: Color(0xFFF1F5F9), width: 1),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // ── Animated Page Dots ────────────────────────
          Row(
            children: List.generate(totalPages, (i) {
              final isActive = i == activePage;
              return AnimatedContainer(
                duration: const Duration(milliseconds: 250),
                margin: const EdgeInsets.only(right: 6),
                width: isActive ? 24 : 8,
                height: 8,
                decoration: BoxDecoration(
                  color: isActive
                      ? const Color(0xFF2563EB)
                      : const Color(0xFFE2E8F0),
                  borderRadius: BorderRadius.circular(4),
                ),
              );
            }),
          ),

          // ── Nav Buttons ───────────────────────────────
          Row(
            children: [
              if (showBack && onBack != null) ...[
                OnboardingNavButton(
                  label: 'Back',
                  icon: Icons.arrow_back_rounded,
                  isOutlined: true,
                  onTap: onBack!,
                ),
                const SizedBox(width: 12),
              ],
              OnboardingNavButton(
                label: nextLabel,
                icon: Icons.arrow_forward_rounded,
                isOutlined: false,
                onTap: onNext,
                iconOnRight: true,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Nav Button ────────────────────────────────────────────────────────────────
class OnboardingNavButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isOutlined;
  final bool iconOnRight;
  final VoidCallback onTap;

  const OnboardingNavButton({
    super.key,
    required this.label,
    required this.icon,
    required this.isOutlined,
    required this.onTap,
    this.iconOnRight = false,
  });

  @override
  Widget build(BuildContext context) {
    final textColor =
        isOutlined ? const Color(0xFF475569) : Colors.white;

    final children = iconOnRight
        ? <Widget>[
            Text(label,
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: textColor)),
            const SizedBox(width: 6),
            Icon(icon, size: 18, color: textColor),
          ]
        : <Widget>[
            Icon(icon, size: 18, color: textColor),
            const SizedBox(width: 6),
            Text(label,
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: textColor)),
          ];

    final content = Row(mainAxisSize: MainAxisSize.min, children: children);

    if (isOutlined) {
      return OutlinedButton(
        onPressed: onTap,
        style: OutlinedButton.styleFrom(
          side: const BorderSide(color: Color(0xFFCBD5E1), width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        child: content,
      );
    }

    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF2563EB),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
      child: content,
    );
  }
}

// ── Logo Top Bar ──────────────────────────────────────────────────────────────
class OnboardingTopBar extends StatelessWidget {
  final VoidCallback? onSkip; // null = hide skip button

  const OnboardingTopBar({super.key, this.onSkip});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 14.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Logo chip
          Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.asset(
                    'assets/images/logos/ally_logo.png',
                    width: 32,
                    height: 32,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              const Text(
                'Ally',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                ),
              ),
            ],
          ),
          // Skip button or spacer
          if (onSkip != null)
            TextButton(
              onPressed: onSkip,
              style: TextButton.styleFrom(
                foregroundColor: const Color(0xFF64748B),
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side:
                      const BorderSide(color: Color(0xFFE2E8F0), width: 1),
                ),
              ),
              child: const Text('Skip',
                  style:
                      TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
            )
          else
            const SizedBox(width: 60),
        ],
      ),
    );
  }
}
