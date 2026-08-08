// File: lib/worker/earnings/payout_history/payout_history_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class WorkerPayoutHistoryScreen extends StatefulWidget {
  const WorkerPayoutHistoryScreen({super.key});

  @override
  State<WorkerPayoutHistoryScreen> createState() =>
      _WorkerPayoutHistoryScreenState();
}

class _WorkerPayoutHistoryScreenState extends State<WorkerPayoutHistoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  List<Map<String, String>> get _completedPayouts => [
    {
      'id': 'PAY-992182',
      'bank': 'mock_bank_name_sbi_ending'.tr(context),
      'amount': '₹ 12,400',
      'date': '28 Jul 2026, 10:30 AM',
      'utr': 'UTR4901928301',
      'status': 'completed'.tr(context),
    },
    {
      'id': 'PAY-991204',
      'bank': 'mock_bank_name_sbi_ending'.tr(context),
      'amount': '₹ 9,850',
      'date': '21 Jul 2026, 10:30 AM',
      'utr': 'UTR3810294812',
      'status': 'completed'.tr(context),
    },
    {
      'id': 'PAY-989102',
      'bank': 'mock_bank_name_sbi_ending'.tr(context),
      'amount': '₹ 14,200',
      'date': '14 Jul 2026, 10:30 AM',
      'utr': 'UTR2910394810',
      'status': 'completed'.tr(context),
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'earnings'.tr(context),
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
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF2563EB),
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: const Color(0xFF2563EB),
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          tabs: [
            Tab(text: 'completed'.tr(context)),
            Tab(text: 'pending'.tr(context)),
            Tab(text: 'cancelled_bookings'.tr(context)),
          ],
        ),
      ),
      body: SafeArea(
        child: TabBarView(
          controller: _tabController,
          children: [
            // Completed Payouts List
            ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              itemCount: _completedPayouts.length,
              itemBuilder: (ctx, idx) {
                final pay = _completedPayouts[idx];
                return Container(
                  margin: const EdgeInsets.only(bottom: 14),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border:
                        Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
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
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFD1FAE5),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              'successful_settlement'.tr(context),
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF10B981),
                              ),
                            ),
                          ),
                          Text(
                            pay['amount']!,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 12),

                      Text(
                        pay['bank']!,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'date_prefix'.tr(context).replaceAll('{}', pay['date'] ?? ''),
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF64748B),
                        ),
                      ),
                      Text(
                        'ref_utr_prefix'.tr(context).replaceAll('{}', pay['utr'] ?? ''),
                        style: const TextStyle(
                          fontSize: 11,
                          color: Color(0xFF94A3B8),
                        ),
                      ),

                      const SizedBox(height: 14),

                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'ref_prefix'.tr(context).replaceAll('{}', pay['id'] ?? ''),
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                          OutlinedButton.icon(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('downloading_payout_statement'.tr(context)),
                                  backgroundColor: const Color(0xFF2563EB),
                                ),
                              );
                            },
                            icon: const Icon(Icons.download_rounded, size: 14),
                            label: Text('download_receipt'.tr(context)),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF2563EB),
                              side: const BorderSide(color: Color(0xFF2563EB)),
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 6),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),

            // Pending Tab Empty View
            _buildEmptyState('no_pending_payouts'.tr(context)),

            // Failed Tab Empty View
            _buildEmptyState('no_failed_payouts'.tr(context)),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(String msg) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.check_circle_outline_rounded,
              size: 54, color: Colors.grey.shade300),
          const SizedBox(height: 12),
          Text(
            msg,
            style: const TextStyle(
              fontSize: 14,
              color: Color(0xFF64748B),
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
