import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../models/notification_model.dart';
import '../../../services/notification_service.dart';
import '../../../utils/token_storage.dart';
import 'notification_preferences_screen.dart';

class NotificationCenterScreen extends StatefulWidget {
  const NotificationCenterScreen({super.key});

  @override
  State<NotificationCenterScreen> createState() => _NotificationCenterScreenState();
}

class _NotificationCenterScreenState extends State<NotificationCenterScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<NotificationModel> _notifications = [];
  String _selectedFilter = 'All';
  final List<String> _filters = ['All', 'Booking', 'Communication', 'System'];

  @override
  void initState() {
    super.initState();
    _loadNotifications();
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

  Future<void> _deleteNotification(String id) async {
    try {
      await NotificationService.instance.deleteNotification(id);
      if (mounted) {
        setState(() {
          _notifications.removeWhere((n) => n.id == id);
        });
      }
    } catch (e) {
      debugPrint('Failed to delete notification: $e');
    }
  }

  void _handleNotificationTap(NotificationModel notif, int index) {
    _markAsRead(notif, index);

    final data = notif.data;
    if (data != null && data.containsKey('booking_id')) {
      final bookingId = data['booking_id'];
      final role = TokenStorage.userRole;
      final route = role == 'worker' ? '/worker/jobs/details' : '/customer/booking/details';
      Navigator.of(context).pushNamed(
        route,
        arguments: {'booking_id': bookingId},
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Notifications',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: Color(0xFF0F172A),
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Color(0xFF64748B)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const NotificationPreferencesScreen()),
              );
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert, color: Color(0xFF64748B)),
            onSelected: (val) {
              if (val == 'read_all') _markAllRead();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'read_all',
                child: Text('Mark all as read'),
              ),
            ],
          ),
        ],
        iconTheme: const IconThemeData(color: Color(0xFF0F172A)),
      ),
      body: Column(
        children: [
          _buildFilterBar(),
          Expanded(
            child: _buildBody(),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterBar() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: _filters.map((filter) {
            final isSelected = _selectedFilter == filter;
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: ChoiceChip(
                label: Text(filter),
                selected: isSelected,
                selectedColor: const Color(0xFF2563EB).withOpacity(0.1),
                labelStyle: TextStyle(
                  color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF64748B),
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                ),
                backgroundColor: const Color(0xFFF1F5F9),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                  side: BorderSide(
                    color: isSelected ? const Color(0xFF2563EB) : Colors.transparent,
                  ),
                ),
                onSelected: (selected) {
                  setState(() => _selectedFilter = filter);
                },
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)));
    }
    if (_errorMessage != null) {
      return Center(
        child: Text('Error: $_errorMessage', style: const TextStyle(color: Colors.red)),
      );
    }

    List<NotificationModel> filtered = _notifications;
    if (_selectedFilter != 'All') {
      filtered = _notifications.where((n) {
        if (_selectedFilter == 'Booking') return n.type == 'booking_status_update' || n.type == 'new_booking';
        if (_selectedFilter == 'Communication') return n.type == 'new_message' || n.type == 'new_media';
        if (_selectedFilter == 'System') return n.type == 'system' || n.type == 'promotional';
        return false;
      }).toList();
    }

    if (filtered.isEmpty) {
      return _buildEmptyState();
    }

    return RefreshIndicator(
      onRefresh: _loadNotifications,
      color: const Color(0xFF2563EB),
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        itemCount: filtered.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final notif = filtered[index];
          return _buildNotificationCard(notif, index);
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.notifications_off_outlined, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'No notifications yet',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'When you get notifications, they\'ll show up here.',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationCard(NotificationModel notif, int index) {
    IconData icon;
    Color color;

    if (notif.type == 'booking_status_update' || notif.type == 'new_booking') {
      icon = Icons.event_note_rounded;
      color = const Color(0xFF2563EB); // Blue
    } else if (notif.type == 'new_message' || notif.type == 'new_media') {
      icon = Icons.chat_bubble_outline_rounded;
      color = const Color(0xFF10B981); // Green
    } else if (notif.type == 'system') {
      icon = Icons.info_outline_rounded;
      color = const Color(0xFFF59E0B); // Amber
    } else {
      icon = Icons.notifications_none_rounded;
      color = const Color(0xFF64748B); // Slate
    }

    final formattedTime = DateFormat('MMM d, h:mm a').format(notif.createdAt.toLocal());

    return Dismissible(
      key: Key(notif.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => _deleteNotification(notif.id),
      background: Container(
        padding: const EdgeInsets.only(right: 20),
        alignment: Alignment.centerRight,
        decoration: BoxDecoration(
          color: const Color(0xFFEF4444),
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Icon(Icons.delete_outline, color: Colors.white),
      ),
      child: InkWell(
        onTap: () => _handleNotificationTap(notif, index),
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: notif.isRead ? Colors.white : const Color(0xFFF0FDF4),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: notif.isRead ? const Color(0xFFE2E8F0) : const Color(0xFF86EFAC), width: 1),
            boxShadow: [
              if (!notif.isRead)
                BoxShadow(
                  color: const Color(0xFF10B981).withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                )
            ],
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(width: 16),
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
                              fontWeight: notif.isRead ? FontWeight.w600 : FontWeight.w700,
                              fontSize: 16,
                              color: const Color(0xFF0F172A),
                            ),
                          ),
                        ),
                        if (!notif.isRead)
                          Container(
                            width: 8,
                            height: 8,
                            margin: const EdgeInsets.only(left: 8),
                            decoration: const BoxDecoration(
                              color: Color(0xFF2563EB),
                              shape: BoxShape.circle,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      notif.body,
                      style: TextStyle(
                        fontSize: 14,
                        color: const Color(0xFF475569),
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      formattedTime,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Color(0xFF94A3B8),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
