import 'package:flutter/material.dart';
import '../services/notification_service.dart';

class NotificationBell extends StatefulWidget {
  final VoidCallback? onBellPressed; // Usually navigates to NotificationCenter

  const NotificationBell({super.key, this.onBellPressed});

  @override
  State<NotificationBell> createState() => _NotificationBellState();
}

class _NotificationBellState extends State<NotificationBell> {
  int _unreadCount = 0;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchUnreadCount();
  }

  Future<void> _fetchUnreadCount() async {
    if (!mounted) return;
    setState(() => _isLoading = true);
    try {
      final count = await NotificationService.instance.getUnreadCount();
      if (mounted) {
        setState(() {
          _unreadCount = count;
        });
      }
    } catch (e) {
      debugPrint('Failed to fetch unread count: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        IconButton(
          icon: const Icon(Icons.notifications_outlined),
          onPressed: () async {
            if (widget.onBellPressed != null) {
              widget.onBellPressed!();
              // Optionally refresh after returning, if we awaited a Future, but 
              // for generic callback it's tricky. Let's just do it directly if needed
              // or rely on route observer.
            } else {
              await Navigator.of(context).pushNamed('/notifications');
              _fetchUnreadCount(); // Refresh after coming back
            }
          },
        ),
        if (!_isLoading && _unreadCount > 0)
          Positioned(
            right: 8,
            top: 8,
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: const BoxDecoration(
                color: Colors.red,
                shape: BoxShape.circle,
              ),
              constraints: const BoxConstraints(
                minWidth: 16,
                minHeight: 16,
              ),
              child: Text(
                _unreadCount > 99 ? '99+' : '$_unreadCount',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
      ],
    );
  }
}
