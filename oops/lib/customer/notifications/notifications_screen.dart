// File:
// lib/customer/notifications/notifications_screen.dart

import 'package:flutter/material.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  List<Map<String, dynamic>> _notifications = [
    {
      'id': '1',
      'title': 'Inspection Quotation Submitted',
      'desc': 'Sunil Verma uploaded the diagnostic report & quote of ₹4,850 for #INS-49210.',
      'time': '10 Mins Ago',
      'type': 'Booking',
      'isUnread': true,
      'icon': Icons.assignment_outlined,
      'color': const Color(0xFF2563EB),
    },
    {
      'id': '2',
      'title': 'Flat ₹200 Cashback Credited! 🎉',
      'desc': 'You won cashback for completing your AC Deep Servicing booking.',
      'time': '2 Hours Ago',
      'type': 'Offers',
      'isUnread': true,
      'icon': Icons.card_giftcard_rounded,
      'color': const Color(0xFF16A34A),
    },
    {
      'id': '3',
      'title': 'Payment Received ₹4,850',
      'desc': 'Payment confirmed for Electrical DB Repair via KaamSetu Pay.',
      'time': 'Yesterday',
      'type': 'Payments',
      'isUnread': false,
      'icon': Icons.account_balance_wallet_rounded,
      'color': const Color(0xFF0EA5E9),
    },
    {
      'id': '4',
      'title': 'Security Alert & Login',
      'desc': 'New login detected from HSR Layout, Bengaluru.',
      'time': '3 Days Ago',
      'type': 'System',
      'isUnread': false,
      'icon': Icons.security_rounded,
      'color': const Color(0xFF64748B),
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _markAllRead() {
    setState(() {
      for (var n in _notifications) {
        n['isUnread'] = false;
      }
    });
  }

  void _clearAll() {
    setState(() {
      _notifications.clear();
    });
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
          'Notifications',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert_rounded, color: Color(0xFF0F172A)),
            onSelected: (val) {
              if (val == 'read') _markAllRead();
              if (val == 'clear') _clearAll();
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: 'read', child: Text('Mark all as read')),
              PopupMenuItem(value: 'clear', child: Text('Clear all notifications', style: TextStyle(color: Color(0xFFEF4444)))),
            ],
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: const Color(0xFF2563EB),
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: const Color(0xFF2563EB),
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800),
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Bookings'),
            Tab(text: 'Offers'),
            Tab(text: 'Payments'),
            Tab(text: 'System'),
          ],
        ),
      ),
      body: _notifications.isEmpty
          ? _buildEmptyNotifications()
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              physics: const BouncingScrollPhysics(),
              itemCount: _notifications.length,
              itemBuilder: (context, index) {
                final notif = _notifications[index];
                final isUnread = notif['isUnread'] as bool;

                return Dismissible(
                  key: Key(notif['id'] as String),
                  onDismissed: (_) {
                    setState(() {
                      _notifications.removeAt(index);
                    });
                  },
                  background: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.only(right: 20),
                    alignment: Alignment.centerRight,
                    decoration: BoxDecoration(
                      color: const Color(0xFFEF4444),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(Icons.delete_outline_rounded, color: Colors.white),
                  ),
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isUnread ? const Color(0xFFEFF6FF) : Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: isUnread ? const Color(0xFFBFDBFE) : const Color(0xFFE2E8F0)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: (notif['color'] as Color).withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(notif['icon'] as IconData, color: notif['color'] as Color, size: 22),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Expanded(
                                    child: Text(
                                      notif['title'] as String,
                                      style: TextStyle(
                                        fontSize: 14,
                                        fontWeight: isUnread ? FontWeight.w800 : FontWeight.w700,
                                        color: const Color(0xFF0F172A),
                                      ),
                                    ),
                                  ),
                                  if (isUnread)
                                    Container(
                                      width: 8,
                                      height: 8,
                                      decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                notif['desc'] as String,
                                style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.3),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                notif['time'] as String,
                                style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8), fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }

  Widget _buildEmptyNotifications() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: const BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
            child: const Icon(Icons.notifications_off_outlined, color: Color(0xFF2563EB), size: 40),
          ),
          const SizedBox(height: 16),
          const Text('No Notifications Yet', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
          const SizedBox(height: 6),
          const Text('We will update you when your service status changes.', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
        ],
      ),
    );
  }
}
