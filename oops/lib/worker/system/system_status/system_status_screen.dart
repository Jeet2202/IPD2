// File: lib/worker/system/system_status/system_status_screen.dart

import 'package:flutter/material.dart';

enum WorkerSystemStatusType {
  maintenance,
  serverError,
  notFound,
  forceUpdate,
  sessionExpired,
  verificationRejected,
  accountSuspended,
}

class WorkerSystemStatusScreen extends StatelessWidget {
  final WorkerSystemStatusType statusType;

  const WorkerSystemStatusScreen({
    super.key,
    this.statusType = WorkerSystemStatusType.maintenance,
  });

  @override
  Widget build(BuildContext context) {
    final config = _getStatusConfig(statusType);

    return Scaffold(      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Icon Container
              Container(
                width: 110,
                height: 110,
                decoration: BoxDecoration(
                  color: config.iconBgColor,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  config.icon,
                  size: 56,
                  color: config.iconColor,
                ),
              ),

              const SizedBox(height: 32),

              // Title & Description
              Text(
                config.title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                config.description,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w400,
                  color: Color(0xFF64748B),
                  height: 1.5,
                ),
              ),

              const SizedBox(height: 36),

              // Primary Action Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushReplacementNamed(
                        context, '/worker/dashboard');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    config.primaryBtnText,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 14),

              // Secondary Action / Support Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                        context, '/worker/support/help-center');
                  },
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFCBD5E1), width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Text(
                    'Contact Partner Support',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF475569),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  _StatusConfig _getStatusConfig(WorkerSystemStatusType type) {
    switch (type) {
      case WorkerSystemStatusType.maintenance:
        return _StatusConfig(
          title: 'Scheduled System Maintenance',
          description:
              'Ally Partner Desk is currently undergoing scheduled server upgrades. Services will resume shortly.',
          icon: Icons.engineering_rounded,
          iconBgColor: const Color(0xFFEFF6FF),
          iconColor: const Color(0xFF2563EB),
          primaryBtnText: 'Refresh Status',
        );
      case WorkerSystemStatusType.forceUpdate:
        return _StatusConfig(
          title: 'App Update Required',
          description:
              'A critical new version of Ally Partner App is available with new job dispatch features.',
          icon: Icons.system_update_rounded,
          iconBgColor: const Color(0xFFD1FAE5),
          iconColor: const Color(0xFF10B981),
          primaryBtnText: 'Update Now on Play Store',
        );
      case WorkerSystemStatusType.verificationRejected:
        return _StatusConfig(
          title: 'KYC Document Re-upload Needed',
          description:
              'Your uploaded ID proof was unreadable. Please re-upload clear photos of Aadhaar & PAN card.',
          icon: Icons.error_outline_rounded,
          iconBgColor: const Color(0xFFFEF3C7),
          iconColor: const Color(0xFFD97706),
          primaryBtnText: 'Re-upload KYC Documents',
        );
      case WorkerSystemStatusType.accountSuspended:
        return _StatusConfig(
          title: 'Partner Account Flagged',
          description:
              'Your account has been temporarily flagged due to unverified cancellations. Please reach out to support.',
          icon: Icons.block_rounded,
          iconBgColor: const Color(0xFFFEE2E2),
          iconColor: const Color(0xFFEF4444),
          primaryBtnText: 'Appeal Account Review',
        );
      default:
        return _StatusConfig(
          title: 'System Notice',
          description: 'Temporary system status notice for Ally Partner.',
          icon: Icons.info_outline_rounded,
          iconBgColor: const Color(0xFFEFF6FF),
          iconColor: const Color(0xFF2563EB),
          primaryBtnText: 'Return to Dashboard',
        );
    }
  }
}

class _StatusConfig {
  final String title;
  final String description;
  final IconData icon;
  final Color iconBgColor;
  final Color iconColor;
  final String primaryBtnText;

  _StatusConfig({
    required this.title,
    required this.description,
    required this.icon,
    required this.iconBgColor,
    required this.iconColor,
    required this.primaryBtnText,
  });
}
