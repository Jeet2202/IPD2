// File: lib/worker/inspection/customer_decision/customer_decision_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';
import '../../../../widgets/language_selector_widget.dart';

class WorkerCustomerDecisionScreen extends StatefulWidget {
  const WorkerCustomerDecisionScreen({super.key});

  @override
  State<WorkerCustomerDecisionScreen> createState() =>
      _WorkerCustomerDecisionScreenState();
}

class _WorkerCustomerDecisionScreenState
    extends State<WorkerCustomerDecisionScreen> {
  bool _notifyOnDecision = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'customer_decision_tracker'.tr(context),
          style: const TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Decision Status Card Header
              Container(
                padding: const EdgeInsets.all(20),
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
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            'quotation_id_mock'.tr(context),
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                              letterSpacing: 0.8,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF59E0B),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'under_review'.tr(context),
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    Text(
                      'customer_reviewing_quote'.tr(context),
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'quotation_total_submitted'.tr(context),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.white.withOpacity(0.85),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Status Timeline Section
              Text(
                'proposal_status_timeline'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 14),

              _buildTimelineStep(
                title: 'timeline_quotation_submitted'.tr(context),
                subtitle: 'timeline_quotation_submitted_sub'.tr(context),
                isDone: true,
              ),
              _buildTimelineStep(
                title: 'timeline_customer_viewed'.tr(context),
                subtitle: 'timeline_customer_viewed_sub'.tr(context),
                isDone: true,
              ),
              _buildTimelineStep(
                title: 'timeline_decision_pending'.tr(context),
                subtitle: 'timeline_decision_pending_sub'.tr(context),
                isCurrent: true,
              ),
              _buildTimelineStep(
                title: 'timeline_accepted'.tr(context),
                subtitle: 'timeline_accepted_sub'.tr(context),
                isPending: true,
              ),
              _buildTimelineStep(
                title: 'timeline_negotiation'.tr(context),
                subtitle: 'timeline_negotiation_sub'.tr(context),
                isPending: true,
                isLast: true,
              ),

              const SizedBox(height: 24),

              // Action Bar & Negotiation Quick Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                      color: const Color(0xFF2563EB).withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.chat_bubble_outline_rounded,
                            color: Color(0xFF2563EB), size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'direct_customer_communication'.tr(context),
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF2563EB),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'pooja_can_request'.tr(context),
                      style: const TextStyle(
                        fontSize: 12,
                        color: Color(0xFF475569),
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      height: 44,
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.pushNamed(
                              context, '/worker/inspection/negotiation-chat');
                        },
                        icon: const Icon(Icons.chat_rounded, size: 18),
                        label: Text('open_negotiation_chat'.tr(context)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Notification Toggle & Actions
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'push_notification_alert'.tr(context),
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'notify_on_customer_decision'.tr(context),
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF64748B),
                        ),
                      ),
                    ],
                  ),
                  Switch(
                    value: _notifyOnDecision,
                    activeColor: const Color(0xFF2563EB),
                    onChanged: (val) =>
                        setState(() => _notifyOnDecision = val),
                  ),
                ],
              ),

              const SizedBox(height: 28),

              // Return to Dashboard Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.pushReplacementNamed(
                        context, '/worker/dashboard');
                  },
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFCBD5E1), width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    'return_to_partner_dashboard'.tr(context),
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF475569),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTimelineStep({
    required String title,
    required String subtitle,
    bool isDone = false,
    bool isCurrent = false,
    bool isPending = false,
    bool isLast = false,
  }) {
    final color = isDone
        ? const Color(0xFF10B981)
        : (isCurrent ? const Color(0xFF2563EB) : const Color(0xFFCBD5E1));

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
              child: Icon(
                isDone ? Icons.check_rounded : Icons.circle,
                size: 12,
                color: Colors.white,
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 36,
                color: isDone ? const Color(0xFF10B981) : const Color(0xFFE2E8F0),
              ),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: isPending
                      ? const Color(0xFF94A3B8)
                      : const Color(0xFF0F172A),
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 11,
                  color: Color(0xFF64748B),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ],
    );
  }
}
