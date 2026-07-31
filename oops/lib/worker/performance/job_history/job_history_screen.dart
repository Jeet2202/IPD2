// File: lib/worker/performance/job_history/job_history_screen.dart

import 'package:flutter/material.dart';

class WorkerJobHistoryScreen extends StatefulWidget {
  const WorkerJobHistoryScreen({super.key});

  @override
  State<WorkerJobHistoryScreen> createState() =>
      _WorkerJobHistoryScreenState();
}

class _WorkerJobHistoryScreenState extends State<WorkerJobHistoryScreen> {
  final List<Map<String, String>> _jobs = [
    {
      'id': 'JOB-8821',
      'service': 'AC Water Leakage & Drain Line Repair',
      'customer': 'Anita Sharma',
      'date': '31 Jul 2026',
      'amount': '₹ 850',
      'status': 'Completed',
    },
    {
      'id': 'JOB-8814',
      'service': 'MCB Switch Replacement & Wiring',
      'customer': 'Sunil Verma',
      'date': '30 Jul 2026',
      'amount': '₹ 1,200',
      'status': 'Completed',
    },
    {
      'id': 'JOB-8790',
      'service': 'Ceiling Fan Installation',
      'customer': 'Rajesh Gupta',
      'date': '29 Jul 2026',
      'amount': '₹ 450',
      'status': 'Completed',
    },
  ];

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
          'Completed Job History',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Search Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
              child: TextField(
                decoration: InputDecoration(
                  hintText: 'Search jobs by ID or customer name...',
                  hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  prefixIcon:
                      const Icon(Icons.search_rounded, color: Color(0xFF64748B)),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding: const EdgeInsets.symmetric(vertical: 12),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                  ),
                ),
              ),
            ),

            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                itemCount: _jobs.length,
                itemBuilder: (ctx, idx) {
                  final job = _jobs[idx];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                          color: const Color(0xFFF1F5F9), width: 1.5),
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
                              job['id']!,
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
                                color: const Color(0xFFD1FAE5),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'COMPLETED',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF10B981),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          job['service']!,
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${job['customer']} • ${job['date']}',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF64748B),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              job['amount']!,
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF10B981),
                              ),
                            ),
                            OutlinedButton.icon(
                              onPressed: () {
                                Navigator.pushNamed(
                                    context, '/worker/earnings/transaction-details');
                              },
                              icon: const Icon(Icons.receipt_long_rounded,
                                  size: 14),
                              label: const Text('Invoice'),
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
            ),
          ],
        ),
      ),
    );
  }
}
