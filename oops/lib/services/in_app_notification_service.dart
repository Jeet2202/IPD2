import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../app/routes/app_router.dart';
import '../models/notification_model.dart';
import '../utils/token_storage.dart';
import 'notification_service.dart';
import 'push_notification_service.dart';

class InAppNotificationService {
  InAppNotificationService._();
  static final InAppNotificationService instance = InAppNotificationService._();

  Timer? _pollingTimer;
  final Set<String> _seenNotificationIds = {};
  bool _isInitialized = false;

  /// Start polling for new notifications when user is logged in
  void startPolling() {
    if (_isInitialized) return;
    _isInitialized = true;
    _loadSeenIds();

    // Initial check after 2 seconds
    Future.delayed(const Duration(seconds: 2), () {
      checkForNewNotifications();
    });

    // Fast polling every 4 seconds
    _pollingTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      checkForNewNotifications();
    });
  }

  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
    _isInitialized = false;
  }

  Future<void> _loadSeenIds() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final saved = prefs.getStringList('seen_notification_ids') ?? [];
      _seenNotificationIds.addAll(saved);
    } catch (_) {}
  }

  Future<void> _saveSeenId(String id) async {
    _seenNotificationIds.add(id);
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('seen_notification_ids', _seenNotificationIds.toList());
    } catch (_) {}
  }

  Future<void> checkForNewNotifications() async {
    if (TokenStorage.accessToken.isEmpty) return;

    try {
      final notifications = await NotificationService.instance.getNotifications(limit: 10);
      if (notifications.isEmpty) return;

      for (var notif in notifications) {
        if (!_seenNotificationIds.contains(notif.id)) {
          await _saveSeenId(notif.id);

          // Trigger local device system notification
          PushNotificationService.instance.showLocalNotificationDirect(
            title: notif.title,
            body: notif.body,
            payloadData: notif.data,
          );

          // If unread, trigger in-app floating banner pop-up
          if (!notif.isRead) {
            _showInAppBanner(notif);
          }
        }
      }
    } catch (e) {
      debugPrint('InAppNotificationService error: $e');
    }
  }

  void _showInAppBanner(NotificationModel notif) {
    final context = AppRouter.navigatorKey.currentContext;
    if (context == null) return;

    final overlay = Overlay.maybeOf(context);
    if (overlay == null) return;

    late OverlayEntry entry;

    entry = OverlayEntry(
      builder: (context) {
        final isQuotation = notif.type.toLowerCase().contains('quotation') ||
            notif.title.toLowerCase().contains('quotation');

        return Positioned(
          top: MediaQuery.of(context).padding.top + 10,
          left: 16,
          right: 16,
          child: Material(
            color: Colors.transparent,
            child: TweenAnimationBuilder<double>(
              duration: const Duration(milliseconds: 350),
              curve: Curves.easeOutBack,
              tween: Tween(begin: -120.0, end: 0.0),
              builder: (context, translateY, child) {
                return Transform.translate(
                  offset: Offset(0, translateY),
                  child: child,
                );
              },
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.3),
                      blurRadius: 18,
                      offset: const Offset(0, 8),
                    ),
                  ],
                  border: Border.all(
                    color: isQuotation ? const Color(0xFF3B82F6) : const Color(0xFF334155),
                    width: 1.5,
                  ),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isQuotation
                                ? const Color(0xFF2563EB).withValues(alpha: 0.25)
                                : Colors.white10,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            isQuotation
                                ? Icons.request_quote_rounded
                                : Icons.notifications_active_rounded,
                            color: isQuotation ? const Color(0xFF60A5FA) : Colors.amber,
                            size: 22,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                notif.title,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                notif.body,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  color: Color(0xFF94A3B8),
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            entry.remove();
                          },
                          child: const Padding(
                            padding: EdgeInsets.all(4.0),
                            child: Icon(Icons.close_rounded, color: Colors.white54, size: 18),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        TextButton(
                          onPressed: () {
                            entry.remove();
                            NotificationService.instance.markAsRead(notif.id);

                            final data = notif.data ?? {};
                            if (data.containsKey('booking_id')) {
                              Navigator.of(context).pushNamed(
                                '/customer/booking/details',
                                arguments: {'booking_id': data['booking_id']},
                              );
                            } else {
                              Navigator.of(context).pushNamed('/customer/notifications');
                            }
                          },
                          style: TextButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          child: Text(
                            isQuotation ? 'View Quotation' : 'View Notification',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );

    overlay.insert(entry);

    // Auto dismiss after 7 seconds
    Future.delayed(const Duration(seconds: 7), () {
      try {
        entry.remove();
      } catch (_) {}
    });
  }
}
