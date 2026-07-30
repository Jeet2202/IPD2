// File: lib/worker/performance/leaderboard/leaderboard_screen.dart

import 'package:flutter/material.dart';

class WorkerLeaderboardScreen extends StatefulWidget {
  const WorkerLeaderboardScreen({super.key});

  @override
  State<WorkerLeaderboardScreen> createState() =>
      _WorkerLeaderboardScreenState();
}

class _WorkerLeaderboardScreenState extends State<WorkerLeaderboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final List<Map<String, String>> _topWorkers = [
    {
      'rank': '1',
      'name': 'Suresh Verma',
      'category': 'Electrician',
      'jobs': '48 Jobs',
      'rating': '5.0 ★',
      'earnings': '₹ 18,400',
    },
    {
      'rank': '2',
      'name': 'Ramesh Kumar (You)',
      'category': 'Electrician Pro',
      'jobs': '42 Jobs',
      'rating': '4.9 ★',
      'earnings': '₹ 14,800',
    },
    {
      'rank': '3',
      'name': 'Amit Patel',
      'category': 'Plumber',
      'jobs': '39 Jobs',
      'rating': '4.9 ★',
      'earnings': '₹ 13,200',
    },
    {
      'rank': '4',
      'name': 'Deepak Sharma',
      'category': 'AC Technician',
      'jobs': '35 Jobs',
      'rating': '4.8 ★',
      'earnings': '₹ 11,900',
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
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Regional Leaderboard',
          style: TextStyle(
            color: Color(0xFF0F172A),
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
            Tab(text: 'Weekly'),
            Tab(text: 'Monthly'),
            Tab(text: 'All Time'),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Your Current Rank Banner Card
            Container(
              margin: const EdgeInsets.all(20),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF2563EB).withOpacity(0.25),
                    blurRadius: 16,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: const Row(
                children: [
                  CircleAvatar(
                    radius: 20,
                    backgroundColor: Colors.white,
                    child: Text(
                      '#2',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w900,
                        color: Color(0xFF2563EB),
                      ),
                    ),
                  ),
                  SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Your Regional Rank: #2 in Delhi NCR',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'Top 5% of all active tradesmen this week',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white70,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Leaderboard Cards List
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                itemCount: _topWorkers.length,
                itemBuilder: (ctx, idx) {
                  final worker = _topWorkers[idx];
                  final isUser = worker['rank'] == '2';

                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFFEFF6FF) : Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(
                        color: isUser
                            ? const Color(0xFF2563EB)
                            : const Color(0xFFF1F5F9),
                        width: isUser ? 1.5 : 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 32,
                          height: 32,
                          decoration: BoxDecoration(
                            color: worker['rank'] == '1'
                                ? const Color(0xFFFEF3C7)
                                : (worker['rank'] == '2'
                                    ? const Color(0xFFE0F2FE)
                                    : const Color(0xFFF1F5F9)),
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: Text(
                              '#${worker['rank']}',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w800,
                                color: worker['rank'] == '1'
                                    ? const Color(0xFFD97706)
                                    : const Color(0xFF2563EB),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                worker['name']!,
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w800,
                                  color: isUser
                                      ? const Color(0xFF2563EB)
                                      : const Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '${worker['category']} • ${worker['jobs']}',
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: Color(0xFF64748B),
                                ),
                              ),
                            ],
                          ),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              worker['earnings']!,
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF10B981),
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              worker['rating']!,
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFFF59E0B),
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
