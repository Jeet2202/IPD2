// File: lib/worker/inspection/repair_dashboard/repair_dashboard_screen.dart

import 'package:flutter/material.dart';

class WorkerRepairDashboardScreen extends StatefulWidget {
  const WorkerRepairDashboardScreen({super.key});

  @override
  State<WorkerRepairDashboardScreen> createState() =>
      _WorkerRepairDashboardScreenState();
}

class _WorkerRepairDashboardScreenState
    extends State<WorkerRepairDashboardScreen> {
  int _currentNavIndex = 1;

  final List<Map<String, String>> _repairs = [
    {
      'id': 'REPAIR-102',
      'customer': 'Pooja Sharma',
      'service': 'AC Water Leak & Drain Line Repair',
      'status': 'Approved • Ready to Start',
      'statusColor': '0xFF10B981',
      'amount': '₹ 1,198',
      'address': 'Dwarka Sector 15',
    },
    {
      'id': 'REPAIR-105',
      'customer': 'Vikram Singh',
      'service': 'Main DB Board Wiring Overhaul',
      'status': 'Quotation Under Review',
      'statusColor': '0xFFF59E0B',
      'amount': '₹ 2,400',
      'address': 'Green Park Main',
    },
    {
      'id': 'REPAIR-098',
      'customer': 'Sunil Verma',
      'service': 'MCB Switch Replacement',
      'status': 'Completed Today',
      'statusColor': '0xFF2563EB',
      'amount': '₹ 850',
      'address': 'Dwarka Sector 15',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        automaticallyImplyLeading: false,
        title: const Text(
          'Inspection & Repair Dashboard',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
        centerTitle: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined,
                color: Color(0xFF0F172A)),
            onPressed: () => Navigator.pushNamed(context, '/worker/notifications'),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary Metric Cards Grid
              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile(
                      label: "Today's Repairs",
                      value: '2 Ready',
                      icon: Icons.build_rounded,
                      color: const Color(0xFF2563EB),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricTile(
                      label: 'Quotes Pending',
                      value: '1 Review',
                      icon: Icons.hourglass_top_rounded,
                      color: const Color(0xFFF59E0B),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile(
                      label: 'Completed Repairs',
                      value: '18 This Month',
                      icon: Icons.check_circle_rounded,
                      color: const Color(0xFF10B981),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricTile(
                      label: 'Est. Revenue',
                      value: '₹ 14,450',
                      icon: Icons.account_balance_wallet_rounded,
                      color: const Color(0xFF0EA5E9),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Repair Job List Header
              const Text(
                'Active Repairs & Inspection Quotes',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 14),

              ..._repairs.map((r) {
                final color = Color(int.parse(r['statusColor']!));

                return Container(
                  margin: const EdgeInsets.only(bottom: 14),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 16,
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
                              color: color.withOpacity(0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              r['status']!,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                color: color,
                              ),
                            ),
                          ),
                          Text(
                            r['amount']!,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF10B981),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        r['service']!,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${r['customer']} • ${r['address']}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF64748B),
                        ),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () {
                                Navigator.pushNamed(
                                    context, '/worker/inspection/submission');
                              },
                              style: OutlinedButton.styleFrom(
                                side: const BorderSide(color: Color(0xFFCBD5E1)),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: const Text('View Report',
                                  style: TextStyle(
                                      fontSize: 12,
                                      color: Color(0xFF475569))),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: ElevatedButton(
                              onPressed: () {
                                Navigator.pushNamed(
                                    context, '/worker/jobs/start-work');
                              },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF2563EB),
                                foregroundColor: Colors.white,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: const Text('Start Work',
                                  style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w700)),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              }).toList(),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentNavIndex,
        selectedItemColor: const Color(0xFF2563EB),
        unselectedItemColor: const Color(0xFF94A3B8),
        type: BottomNavigationBarType.fixed,        elevation: 12,
        onTap: (idx) {
          if (idx == 0) {
            Navigator.pushReplacementNamed(context, '/worker/dashboard');
          } else if (idx == 1) {
            Navigator.pushReplacementNamed(context, '/worker/jobs/incoming');
          } else if (idx == 2) {
            Navigator.pushReplacementNamed(context, '/worker/earnings/dashboard');
          } else if (idx == 3) {
            Navigator.pushReplacementNamed(context, '/worker/profile');
          }
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.handyman_rounded),
            label: 'Repairs',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_balance_wallet_rounded),
            label: 'Earnings',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_rounded),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  Widget _buildMetricTile({
    required String label,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF64748B),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
