// File:
// lib/customer/bookings/my_bookings/my_bookings_screen.dart

import 'package:flutter/material.dart';

class MyBookingsScreen extends StatefulWidget {
  const MyBookingsScreen({super.key});

  @override
  State<MyBookingsScreen> createState() => _MyBookingsScreenState();
}

class _MyBookingsScreenState extends State<MyBookingsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedFilter = 'All';

  final List<String> _filters = ['All', 'Upcoming', 'In Progress', 'Completed', 'Cancelled'];

  final List<Map<String, dynamic>> _normalBookings = [
    {
      'id': '#BK-90214',
      'service': 'Full AC Deep Servicing',
      'tech': 'Ramesh Kumar',
      'date': '31 Jul 2026',
      'time': '02:00 PM',
      'amount': '₹899',
      'status': 'In Progress',
      'statusColor': const Color(0xFF2563EB),
    },
    {
      'id': '#BK-88102',
      'service': 'Bathroom Deep Cleaning',
      'tech': 'Pooja Sharma',
      'date': '02 Aug 2026',
      'time': '10:00 AM',
      'amount': '₹1,249',
      'status': 'Upcoming',
      'statusColor': const Color(0xFF0EA5E9),
    },
    {
      'id': '#BK-74912',
      'service': 'Kitchen Tap Leakage Repair',
      'tech': 'Suresh Patel',
      'date': '24 Jul 2026',
      'time': '04:30 PM',
      'amount': '₹450',
      'status': 'Completed',
      'statusColor': const Color(0xFF16A34A),
    },
  ];

  final List<Map<String, dynamic>> _inspectionBookings = [
    {
      'id': '#INS-49210',
      'service': 'Electrical DB Short Circuit Diagnosis',
      'tech': 'Sunil Verma',
      'date': '31 Jul 2026',
      'time': '11:00 AM',
      'amount': '₹99',
      'status': 'In Progress',
      'statusColor': const Color(0xFF2563EB),
    },
    {
      'id': '#INS-38104',
      'service': 'Washing Machine Drainage Diagnosis',
      'tech': 'Amit Roy',
      'date': '15 Jul 2026',
      'time': '03:00 PM',
      'amount': '₹99',
      'status': 'Completed',
      'statusColor': const Color(0xFF16A34A),
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'My Bookings',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF2563EB),
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: const Color(0xFF2563EB),
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
          tabs: const [
            Tab(text: 'Direct Services'),
            Tab(text: 'Inspection Flow'),
          ],
        ),
      ),
      body: Column(
        children: [
          // ── Filter Chips ───────────────────────────────────────────────
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: SizedBox(
              height: 38,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: _filters.length,
                itemBuilder: (context, index) {
                  final filter = _filters[index];
                  final isSelected = _selectedFilter == filter;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text(filter),
                      selected: isSelected,
                      selectedColor: const Color(0xFF2563EB),
                      backgroundColor: const Color(0xFFF1F5F9),
                      labelStyle: TextStyle(
                        fontSize: 12,
                        fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
                        color: isSelected ? Colors.white : const Color(0xFF475569),
                      ),
                      onSelected: (_) => setState(() => _selectedFilter = filter),
                    ),
                  );
                },
              ),
            ),
          ),

          // ── Tab View Content ──────────────────────────────────────────
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildBookingList(_normalBookings),
                _buildBookingList(_inspectionBookings),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        backgroundColor: const Color(0xFF2563EB),
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_rounded),
        label: const Text('Book New Service', style: TextStyle(fontWeight: FontWeight.w800)),
      ),
    );
  }

  Widget _buildBookingList(List<Map<String, dynamic>> bookings) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      physics: const BouncingScrollPhysics(),
      itemCount: bookings.length,
      itemBuilder: (context, index) {
        final b = bookings[index];
        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: const Color(0xFFE2E8F0)),
            boxShadow: [
              BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4)),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(b['id'] as String, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF64748B))),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: (b['statusColor'] as Color).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      b['status'] as String,
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: b['statusColor'] as Color),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                b['service'] as String,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  const Icon(Icons.person_outline_rounded, size: 16, color: Color(0xFF64748B)),
                  const SizedBox(width: 6),
                  Text(b['tech'] as String, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                  const Spacer(),
                  const Icon(Icons.schedule_rounded, size: 16, color: Color(0xFF64748B)),
                  const SizedBox(width: 6),
                  Text('${b['date']} • ${b['time']}', style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                ],
              ),
              const SizedBox(height: 14),
              const Divider(color: Color(0xFFF1F5F9), height: 1),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(b['amount'] as String, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                  ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFEFF6FF),
                      foregroundColor: const Color(0xFF2563EB),
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text('View Details', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
