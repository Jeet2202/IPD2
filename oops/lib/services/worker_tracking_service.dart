import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import 'api_service.dart';

class WorkerTrackingService {
  WorkerTrackingService._();
  static final WorkerTrackingService instance = WorkerTrackingService._();
  
  final ApiService _apiService = ApiService.instance;
  StreamSubscription<Position>? _positionStream;
  String? _currentBookingId;
  
  bool get isTracking => _positionStream != null;

  Future<void> startTracking(String bookingId) async {
    if (isTracking) {
      if (_currentBookingId == bookingId) return;
      await stopTracking();
    }
    
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }
    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permissions are permanently denied, please enable them in Android settings.');
    }
    
    _currentBookingId = bookingId;
    
    // Attempt to configure Android foreground service
    late LocationSettings locationSettings;
    
    if (defaultTargetPlatform == TargetPlatform.android) {
        locationSettings = AndroidSettings(
            accuracy: LocationAccuracy.high,
            distanceFilter: 10,
            forceLocationManager: true,
            intervalDuration: const Duration(seconds: 5),
            foregroundNotificationConfig: const ForegroundNotificationConfig(
                notificationText: "Ally is running in background to share your live location with the customer.",
                notificationTitle: "Ally Live Tracking",
                enableWakeLock: true,
            )
        );
    } else {
        locationSettings = const LocationSettings(
            accuracy: LocationAccuracy.high,
            distanceFilter: 10,
        );
    }

    _positionStream = Geolocator.getPositionStream(locationSettings: locationSettings).listen((Position position) {
      _sendLocationToBackend(position);
    }, onError: (e) {
      debugPrint("Location tracking error: $e");
    });
    
    // Fetch and send immediately so the customer's map updates instantly without waiting for movement
    try {
      final initialPosition = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      await _sendLocationToBackend(initialPosition);
    } catch (e) {
      debugPrint("Failed to fetch initial location: $e");
    }
  }
  
  Future<void> _sendLocationToBackend(Position position) async {
    if (_currentBookingId == null) return;
    try {
      await _apiService.post('/tracking/location', {
        'booking_id': _currentBookingId,
        'latitude': position.latitude,
        'longitude': position.longitude,
        'timestamp': DateTime.now().toUtc().toIso8601String(),
      });
    } catch (e) {
      debugPrint("Failed to send tracking update: $e");
    }
  }

  Future<void> stopTracking() async {
    await _positionStream?.cancel();
    _positionStream = null;
    _currentBookingId = null;
  }
}
