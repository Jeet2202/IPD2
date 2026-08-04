// File: lib/worker/support/ticket_history/ticket_history_screen.dart

import 'package:flutter/material.dart';
import '../../../app/theme/app_colors.dart';

class WorkerTicketHistoryScreen extends StatefulWidget {
  const WorkerTicketHistoryScreen({super.key});

  @override
  State<WorkerTicketHistoryScreen> createState() =>
      _WorkerTicketHistoryScreenState();
}

class _WorkerTicketHistoryScreenState extends State<WorkerTicketHistoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final List<Map<String, String>> _openTickets = [
    {
      'id': 'TCK-9902',
      'subject': 'Escrow payment release pending for #JOB-8821',
      'category': 'Payment Dispute',
      'priority': 'High',
      'date': 'Today, 10:15 AM',
      'status': 'OPEN',
      'statusColor': '0xFF2563EB',
    },
  ];

  final List<Map<String, String>> _resolvedTickets = [
    {
      'id': 'TCK-8812',
      'subject': 'Customer requested location change mid-transit',
      'category': 'Job Issues',
      'priority': 'Normal',
      'date': '24 Jul 2026',
      'status': 'RESOLVED',
      'statusColor': '0xFF10B981',
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
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: AppColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Support Tickets',
          style: TextStyle(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF2563EB),
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: const Color(0xFF2563EB),
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          tabs: const [
            Tab(text: 'Open (1)'),
            Tab(text: 'Resolved (1)'),
            Tab(text: 'Closed (0)'),
          ],
        ),
      ),
      body: SafeArea(
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildTicketList(_openTickets),
            _buildTicketList(_resolvedTickets),
            _buildEmptyState('No closed support tickets'),
          ],
        ),
      ),
    );
  }

  Widget _buildTicketList(List<Map<String, String>> tickets) {
    if (tickets.isEmpty) return _buildEmptyState('No tickets in this section');

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      itemCount: tickets.length,
      itemBuilder: (ctx, idx) {
        final tck = tickets[idx];
        final statusColor = Color(int.parse(tck['statusColor']!));

        return GestureDetector(
          onTap: () {
            Navigator.pushNamed(
                context, '/worker/support/ticket-details');
          },
          child: Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.03),
                  blurRadius: 10,
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      tck['id']!,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF2563EB),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: statusColor.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        tck['status']!,
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: statusColor,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  tck['subject']!,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${tck['category']} • Priority: ${tck['priority']} • ${tck['date']}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildEmptyState(String msg) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.confirmation_number_outlined,
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
