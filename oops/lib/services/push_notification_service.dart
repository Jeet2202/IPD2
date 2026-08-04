import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../app/routes/app_router.dart';
import '../utils/token_storage.dart';
import 'api_service.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  debugPrint('Handling a background message: ${message.messageId}');
}

class PushNotificationService {
  PushNotificationService._();
  static final PushNotificationService instance = PushNotificationService._();

  FirebaseMessaging get _fcm => FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();

  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      await Firebase.initializeApp();
      FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

      // Request permission
      final settings = await _fcm.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        debugPrint('User granted permission');
      } else {
        debugPrint('User declined or has not accepted permission');
        return;
      }

      // Initialize local notifications for foreground messages
      const initializationSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');
      const initializationSettingsDarwin = DarwinInitializationSettings();
      const initializationSettings = InitializationSettings(
        android: initializationSettingsAndroid,
        iOS: initializationSettingsDarwin,
      );

      await _localNotifications.initialize(
        settings: initializationSettings,
        onDidReceiveNotificationResponse: (details) {
          if (details.payload != null) {
            final data = jsonDecode(details.payload!);
            _handleNotificationTap(data);
          }
        },
      );

      // Set up foreground message handler
      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        _showLocalNotification(message);
      });

      // Set up background message tap handler
      FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
        _handleNotificationTap(message.data);
      });

      // Handle initial message (if app was terminated)
      final initialMessage = await _fcm.getInitialMessage();
      if (initialMessage != null) {
        // Delay navigation slightly to allow app to render
        Future.delayed(const Duration(milliseconds: 500), () {
          _handleNotificationTap(initialMessage.data);
        });
      }

      // Register device token with backend
      final token = await _fcm.getToken();
      if (token != null) {
        await _registerDeviceToken(token);
      }

      _fcm.onTokenRefresh.listen(_registerDeviceToken);

      _isInitialized = true;
    } catch (e) {
      debugPrint('Error initializing PushNotificationService: $e');
    }
  }

  Future<void> _registerDeviceToken(String token) async {
    try {
      await ApiService.instance.post(
        '/notifications/register-device',
        {
          'token': token,
          'platform': kIsWeb ? 'web' : Platform.operatingSystem,
        },
      );
      debugPrint('Device token registered with backend.');
    } catch (e) {
      debugPrint('Failed to register device token: $e');
    }
  }

  Future<void> removeDeviceToken() async {
    if (!_isInitialized) return;
    try {
      final token = await _fcm.getToken();
      if (token != null) {
        await ApiService.instance.delete(
          '/notifications/remove-device',
          body: {'token': token},
        );
        debugPrint('Device token removed from backend.');
      }
    } catch (e) {
      debugPrint('Failed to remove device token: $e');
    }
  }

  void _showLocalNotification(RemoteMessage message) {
    final notification = message.notification;
    final android = message.notification?.android;

    if (notification != null && android != null && !kIsWeb) {
      _localNotifications.show(
        id: notification.hashCode,
        title: notification.title,
        body: notification.body,
        notificationDetails: const NotificationDetails(
          android: AndroidNotificationDetails(
            'ally_high_importance_channel', // id
            'High Importance Notifications', // name
            channelDescription: 'This channel is used for important notifications.',
            importance: Importance.max,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
          ),
          iOS: DarwinNotificationDetails(
            presentAlert: true,
            presentBadge: true,
            presentSound: true,
          ),
        ),
        payload: jsonEncode(message.data),
      );
    }
  }

  void _handleNotificationTap(Map<String, dynamic> data) {
    if (data.containsKey('booking_id')) {
      final bookingId = data['booking_id'];
      if (AppRouter.navigatorKey.currentState != null) {
        final role = TokenStorage.userRole;
        final route = role == 'worker' ? '/worker/jobs/details' : '/customer/booking/details';
        AppRouter.navigatorKey.currentState!.pushNamed(
          route,
          arguments: {'booking_id': bookingId},
        );
      }
    }
  }
}
