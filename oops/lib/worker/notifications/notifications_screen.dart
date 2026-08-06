// File: lib/worker/notifications/notifications_screen.dart

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/notification_model.dart';
import '../../services/notification_service.dart';

class WorkerNotificationsScreen extends StatefulWidget {
  const WorkerNotificationsScreen({super.key});

  @override
  State<WorkerNotificationsScreen> createState() =>
      _WorkerNotificationsScreenState();
}

class _WorkerNotificationsScreenState extends State<WorkerNotificationsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  bool _isLoading = true;
  String? _errorMessage;
  List<NotificationModel> _notifications = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadNotifications();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadNotifications() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final list = await NotificationService.instance.getNotifications();
      if (!mounted) return;
      setState(() {
        _notifications = list;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _markAsRead(NotificationModel notif, int index) async {
    if (notif.isRead) return;
    try {
      await NotificationService.instance.markAsRead(notif.id);
      if (mounted) {
        setState(() {
          _notifications[index] = NotificationModel(
            id: notif.id,
            title: notif.title,
            body: notif.body,
            type: notif.type,
            data: notif.data,
            createdAt: notif.createdAt,
            isRead: true,
          );
        });
      }
    } catch (e) {
      debugPrint('Failed to mark read: $e');
    }
  }

  Future<void> _markAllRead() async {
    try {
      await NotificationService.instance.markAllRead();
      _loadNotifications();
    } catch (e) {
      debugPrint('Failed to mark all read: $e');
    }
  }

  void _handleNotificationTap(NotificationModel notif, int index) {
    _markAsRead(notif, index);

    final data = notif.data;
    if (data != null && data.containsKey('booking_id')) {
      final bookingId = data['booking_id'];
      Navigator.pushNamed(
        context,
        '/worker/jobs/details',
        arguments: {'booking_id': bookingId},
      );
    }
  }

  String _getCategory(NotificationModel notif) {
    final type = notif.type.toLowerCase();
    final title = notif.title.toLowerCase();
    final body = notif.body.toLowerCase();

    if (type.contains('payment') ||
        type.contains('payout') ||
        title.contains('payment') ||
        title.contains('credited') ||
        body.contains('₹')) {
      return 'Payments';
    }
    if (type.contains('booking') ||
        type.contains('job') ||
        type.contains('quotation') ||
        type.contains('inspection') ||
        title.contains('booking') ||
        title.contains('job')) {
      return 'Jobs';
    }
    return 'System';
  }

  String _formatTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);

    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return DateFormat('MMM d').format(dt);
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
        title: const Text(
          'Notifications Center',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          TextButton(
            onPressed: _markAllRead,
            child: const Text('Mark All Read'),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF2563EB),
          unselectedLabelColor: const Color(0xFF64748B),
          indicatorColor: const Color(0xFF2563EB),
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Jobs'),
            Tab(text: 'Payments'),
            Tab(text: 'System'),
          ],
        ),
      ),
      body: SafeArea(
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildNotificationList(),
            _buildNotificationList(filterCategory: 'Jobs'),
            _buildNotificationList(filterCategory: 'Payments'),
            _buildNotificationList(filterCategory: 'System'),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationList({String? filterCategory}) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF2563EB)),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded, size: 48, color: Colors.redAccent),
            const SizedBox(height: 12),
            Text(
              'Failed to load notifications',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: _loadNotifications,
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2563EB)),
              child: const Text('Retry', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      );
    }

    final filtered = filterCategory == null
        ? _notifications
        : _notifications
            .where((n) => _getCategory(n) == filterCategory)
            .toList();

    if (filtered.isEmpty) {
      return _buildEmptyState(
        filterCategory == null ? 'No notifications yet' : 'No $filterCategory alerts',
      );
    }

    return RefreshIndicator(
      onRefresh: _loadNotifications,
      color: const Color(0xFF2563EB),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        itemCount: filtered.length,
        itemBuilder: (ctx, idx) {
          final notif = filtered[idx];
          final isUnread = !notif.isRead;
          final cat = _getCategory(notif);

          return GestureDetector(
            onTap: () => _handleNotificationTap(notif, _notifications.indexOf(notif)),
            child: Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isUnread ? const Color(0xFFEFF6FF) : Colors.white,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(
                  color: isUnread
                      ? const Color(0xFF2563EB).withValues(alpha: 0.3)
                      : const Color(0xFFF1F5F9),
                  width: 1.5,
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isUnread
                          ? const Color(0xFF2563EB)
                          : const Color(0xFFF1F5F9),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      cat == 'Jobs'
                          ? Icons.work_outline_rounded
                          : cat == 'Payments'
                              ? Icons.account_balance_wallet_outlined
                              : Icons.notifications_active_outlined,
                      color: isUnread ? Colors.white : const Color(0xFF64748B),
                      size: 20,
                    ),
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
                                notif.title,
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight:
                                      isUnread ? FontWeight.w800 : FontWeight.w700,
                                  color: const Color(0xFF0F172A),
                                ),
                              ),
                            ),
                            Text(
                              _formatTime(notif.createdAt),
                              style: const TextStyle(
                                fontSize: 10,
                                color: Color(0xFF94A3B8),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          notif.body,
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF64748B),
                            height: 1.4,
                          ),
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

  Widget _buildEmptyState(String msg) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.notifications_off_outlined,
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
