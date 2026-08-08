// File: lib/worker/jobs/accept_reject/accept_reject_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkerAcceptRejectScreen extends StatefulWidget {
  const WorkerAcceptRejectScreen({super.key});

  @override
  State<WorkerAcceptRejectScreen> createState() =>
      _WorkerAcceptRejectScreenState();
}

class _WorkerAcceptRejectScreenState extends State<WorkerAcceptRejectScreen> {
  bool _toolsReady = true;
  bool _availabilityConfirmed = true;
  bool _travelConfirmed = true;

  String _selectedReason = 'Distance too far';
  List<String> get _declineReasons => [
    'distance_too_far'.tr(context),
    'currently_busy_another_job'.tr(context),
    'price_offered_low'.tr(context),
    'lack_required_equipment'.tr(context),
    'personal_emergency'.tr(context),
  ];

  @override
  Widget build(BuildContext context) {
    final canAccept =
        _toolsReady && _availabilityConfirmed && _travelConfirmed;

    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'confirm_decision'.tr(context),
          style: const TextStyle(
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
              // Job Summary Card
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
                    BoxShadow(
                      color: const Color(0xFF2563EB).withOpacity(0.25),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'mcb_tripping_repair'.tr(context),
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${'customer_prefix'.tr(context)}Sunil Verma • ${'dwarka_sec_15'.tr(context)}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.white.withOpacity(0.85),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _buildSummaryMetric('est_earnings_caps'.tr(context), '₹ 850'),
                        _buildSummaryMetric('distance_caps'.tr(context), '2.4 Km'),
                        _buildSummaryMetric('duration_caps'.tr(context), '45 Mins'),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Acceptance Checklist Section
              Text(
                'pre_acceptance_checklist'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 12),

              _buildCheckTile(
                title: 'professional_tools_ready'.tr(context),
                subtitle: 'tools_ready_desc'.tr(context),
                value: _toolsReady,
                onChanged: (val) => setState(() => _toolsReady = val),
              ),
              const SizedBox(height: 10),
              _buildCheckTile(
                title: 'immediate_availability'.tr(context),
                subtitle: 'availability_desc'.tr(context),
                value: _availabilityConfirmed,
                onChanged: (val) =>
                    setState(() => _availabilityConfirmed = val),
              ),
              const SizedBox(height: 10),
              _buildCheckTile(
                title: 'travel_route_confirmed'.tr(context),
                subtitle: 'travel_route_desc'.tr(context),
                value: _travelConfirmed,
                onChanged: (val) => setState(() => _travelConfirmed = val),
              ),

              const SizedBox(height: 32),

              // Accept Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: canAccept
                      ? () {
                          _showSuccessDialog(context);
                        }
                      : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF10B981),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: const Color(0xFFE2E8F0),
                    disabledForegroundColor: const Color(0xFF94A3B8),
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.check_circle_rounded, size: 22),
                      const SizedBox(width: 8),
                      Text(
                        'confirm_accept_job'.tr(context),
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Divider
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 1,
                      color: const Color(0xFFE2E8F0),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    child: Text(
                      'or_decline'.tr(context),
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF94A3B8),
                        letterSpacing: 0.8,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Container(
                      height: 1,
                      color: const Color(0xFFE2E8F0),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Decline Section
              Text(
                'decline_reason_optional'.tr(context),
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0F172A),
                ),
              ),
              const SizedBox(height: 10),

              DropdownButtonFormField<String>(
                value: _selectedReason,
                decoration: InputDecoration(
                  prefixIcon: const Icon(Icons.help_outline_rounded,
                      color: Color(0xFF64748B)),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide:
                        const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                  ),
                ),
                icon: const Icon(Icons.keyboard_arrow_down_rounded,
                    color: Color(0xFF64748B)),
                items: _declineReasons.map((r) {
                  return DropdownMenuItem(
                    value: r,
                    child: Text(
                      r,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _selectedReason = val;
                    });
                  }
                },
              ),

              const SizedBox(height: 16),

              // Reject Button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFEF4444), width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    'decline_this_job_request'.tr(context),
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFFEF4444),
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

  Widget _buildSummaryMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: Colors.white.withOpacity(0.8),
            letterSpacing: 0.6,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildCheckTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: value ? const Color(0xFFEFF6FF) : const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: value ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
          width: value ? 1.5 : 1,
        ),
      ),
      child: Row(
        children: [
          Checkbox(
            value: value,
            activeColor: const Color(0xFF2563EB),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(5),
            ),
            onChanged: (v) => onChanged(v ?? false),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 2),
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
        ],
      ),
    );
  }

  void _showSuccessDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
              width: 80,
              height: 80,
              decoration: const BoxDecoration(
                color: Color(0xFFD1FAE5),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_circle_rounded,
                size: 52,
                color: Color(0xFF10B981),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              'job_accepted'.tr(context),
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'job_accepted_desc'.tr(context),
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
                color: Color(0xFF64748B),
                height: 1.5,
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pushReplacementNamed(context, '/worker/jobs/active');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Text(
                  'go_to_active_jobs'.tr(context),
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
