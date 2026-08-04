import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:flutter/foundation.dart';
import '../config/app_config.dart';
import '../utils/token_storage.dart';

class SocketService {
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;
  SocketService._internal();

  IO.Socket? _socket;
  bool _isConnected = false;

  bool get isConnected => _isConnected;
  IO.Socket? get socket => _socket;

  Future<void> connect() async {
    if (_isConnected && _socket != null) return;

    final token = TokenStorage.accessToken;
    if (token.isEmpty) {
      debugPrint('SocketService: No access token found. Cannot connect.');
      return;
    }

    final backendUrl = AppConfig.baseUrl.replaceAll('/api/v1', '');
    
    _socket = IO.io(backendUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
      'auth': {
        'token': token
      },
      'extraHeaders': {
        'Authorization': 'Bearer $token'
      },
      // Automatic reconnection
      'reconnection': true,
      'reconnectionAttempts': 5,
      'reconnectionDelay': 1000,
    });

    _socket!.onConnect((_) {
      _isConnected = true;
      debugPrint('SocketService: Connected to Socket.IO backend.');
    });

    _socket!.onDisconnect((_) {
      _isConnected = false;
      debugPrint('SocketService: Disconnected.');
    });

    _socket!.on('reconnect', (_) {
      _isConnected = true;
      debugPrint('SocketService: Reconnected.');
    });

    _socket!.on('reconnect_error', (data) {
      debugPrint('SocketService: Reconnect error -> $data');
    });

    _socket!.onConnectError((data) {
      debugPrint('SocketService: Connection error -> $data');
    });

    _socket!.onError((data) {
      debugPrint('SocketService: Error -> $data');
    });

    _socket!.connect();
  }

  void disconnect() {
    if (_socket != null) {
      _socket!.disconnect();
      _socket!.destroy();
      _socket = null;
    }
    _isConnected = false;
  }

  // --- Phase 7.4: Live Booking Tracking Helpers ---

  void joinBookingTracking(String bookingId) {
    if (_socket != null && _isConnected) {
      _socket!.emit('join_booking_tracking', {'booking_id': bookingId});
      debugPrint('SocketService: Joined tracking room for booking $bookingId');
    }
  }

  void leaveBookingTracking(String bookingId) {
    if (_socket != null && _isConnected) {
      _socket!.emit('leave_booking_tracking', {'booking_id': bookingId});
      debugPrint('SocketService: Left tracking room for booking $bookingId');
    }
  }

  void emitBookingStatusUpdate(String bookingId, String status) {
    if (_socket != null && _isConnected) {
      _socket!.emit('update_booking_status', {
        'booking_id': bookingId,
        'status': status,
        'timestamp': DateTime.now().toIso8601String(),
      });
      debugPrint('SocketService: Emitted status update for booking $bookingId');
    }
  }

  void onBookingStatusUpdated(Function(dynamic) callback) {
    if (_socket != null) {
      _socket!.on('booking_status_updated', callback);
    }
  }

  void offBookingStatusUpdated([Function(dynamic)? callback]) {
    if (_socket != null) {
      if (callback != null) {
        _socket!.off('booking_status_updated', callback);
      } else {
        _socket!.off('booking_status_updated');
      }
    }
  }

  // --- Phase 7.5: Live Location Tracking Helpers ---

  void emitWorkerLocation(String bookingId, double lat, double lng, double distance, int etaMinutes) {
    if (_socket != null && _isConnected) {
      _socket!.emit('update_worker_location', {
        'booking_id': bookingId,
        'lat': lat,
        'lng': lng,
        'distance': distance,
        'eta': etaMinutes,
        'timestamp': DateTime.now().toIso8601String(),
      });
    }
  }

  void onWorkerLocationUpdated(Function(dynamic) callback) {
    if (_socket != null) {
      _socket!.on('worker_location_updated', callback);
    }
  }

  void offWorkerLocationUpdated([Function(dynamic)? callback]) {
    if (_socket != null) {
      if (callback != null) {
        _socket!.off('worker_location_updated', callback);
      } else {
        _socket!.off('worker_location_updated');
      }
    }
  }
}
