// File: lib/worker/verification/verification_status/verification_status_screen.dart

import 'package:flutter/material.dart';

class WorkerVerificationStatusScreen extends StatelessWidget {
  const WorkerVerificationStatusScreen({super.key});

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
          'Verification Progress',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Hero Status Header Card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFEFF6FF), Color(0xFFDBEAFE)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                      color: const Color(0xFF2563EB).withOpacity(0.2)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.verified_user_rounded,
                          size: 36,
                          color: Color(0xFF2563EB),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Text(
                                'Overall Status',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(width: 8),
                              _buildStatusBadge('IN REVIEW', const Color(0xFFF59E0B)),
                            ],
                          ),
                          const SizedBox(height: 6),
                          const Text(
                            'Estimated review time: ~4 to 8 hours',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF0EA5E9),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              const Text(
                'Verification Milestones',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),

              const SizedBox(height: 16),

              // Verification Progress Timeline
              _buildTimelineStep(
                title: 'Personal Information',
                subtitle: 'Name, Photo, Address & Contact Details',
                status: 'Verified',
                statusColor: const Color(0xFF10B981),
                icon: Icons.person_rounded,
                isCompleted: true,
                isLast: false,
              ),

              _buildTimelineStep(
                title: 'KYC Document Verification',
                subtitle: 'Aadhaar Card, PAN & Live Selfie',
                status: 'Pending Review',
                statusColor: const Color(0xFFF59E0B),
                icon: Icons.badge_rounded,
                isCompleted: false,
                isInProgress: true,
                isLast: false,
              ),

              _buildTimelineStep(
                title: 'Professional Details & Skills',
                subtitle: 'Trade experience & service area setup',
                status: 'Verified',
                statusColor: const Color(0xFF10B981),
                icon: Icons.construction_rounded,
                isCompleted: true,
                isLast: false,
              ),

              _buildTimelineStep(
                title: 'Bank Account & Settlement',
                subtitle: 'Direct deposit account validation',
                status: 'Verified',
                statusColor: const Color(0xFF10B981),
                icon: Icons.account_balance_rounded,
                isCompleted: true,
                isLast: false,
              ),

              _buildTimelineStep(
                title: 'Background Check & Police Clearance',
                subtitle: 'Safety verification check by partner agency',
                status: 'In Progress',
                statusColor: const Color(0xFF0EA5E9),
                icon: Icons.security_rounded,
                isCompleted: false,
                isInProgress: true,
                isLast: true,
              ),

              const SizedBox(height: 24),

              // Legend Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildLegendItem('Verified', const Color(0xFF10B981)),
                    _buildLegendItem('Pending', const Color(0xFFF59E0B)),
                    _buildLegendItem('Rejected', const Color(0xFFEF4444)),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // Contact Support Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: OutlinedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, '/worker/support/help-center'),
                  icon: const Icon(Icons.headset_mic_outlined,
                      color: Color(0xFF2563EB)),
                  label: const Text(
                    'Need Help? Contact Partner Support',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF2563EB),
                    ),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
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

  Widget _buildTimelineStep({
    required String title,
    required String subtitle,
    required String status,
    required Color statusColor,
    required IconData icon,
    required bool isCompleted,
    bool isInProgress = false,
    required bool isLast,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline Dot & Line
        Column(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: isCompleted
                    ? const Color(0xFFD1FAE5)
                    : (isInProgress
                        ? const Color(0xFFFEF3C7)
                        : const Color(0xFFF1F5F9)),
                shape: BoxShape.circle,
                border: Border.all(
                  color: isCompleted
                      ? const Color(0xFF10B981)
                      : (isInProgress
                          ? const Color(0xFFF59E0B)
                          : const Color(0xFFCBD5E1)),
                  width: 2,
                ),
              ),
              child: Icon(
                isCompleted ? Icons.check_rounded : icon,
                size: 20,
                color: isCompleted
                    ? const Color(0xFF10B981)
                    : (isInProgress
                        ? const Color(0xFFD97706)
                        : const Color(0xFF64748B)),
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 46,
                color: isCompleted
                    ? const Color(0xFF10B981)
                    : const Color(0xFFE2E8F0),
              ),
          ],
        ),
        const SizedBox(width: 14),
        // Step Details Card
        Expanded(
          child: Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.03),
                  blurRadius: 10,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ),
                    _buildStatusBadge(status, statusColor),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusBadge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          color: color,
        ),
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: Color(0xFF475569),
          ),
        ),
      ],
    );
  }
}
