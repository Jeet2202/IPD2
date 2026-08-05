import 'dart:io';
import 'package:flutter/foundation.dart';
import '../models/chat_message_model.dart';
import 'api_service.dart';
import 'socket_service.dart';

class BookingChatService extends ChangeNotifier {
  final String bookingId;
  final String currentUserId;
  final SocketService _socketService = SocketService();
  
  List<ChatMessage> _messages = [];
  bool _isOtherPartyTyping = false;

  // Store callback references so we can deregister the exact function on dispose.
  // Using socket.off('event') without a callback removes ALL listeners globally.
  late final Function(dynamic) _onReceiveMessage;
  late final Function(dynamic) _onTypingUpdate;
  late final Function(dynamic) _onMessageRead;
  
  BookingChatService({required this.bookingId, required this.currentUserId}) {
    _initSocketListeners();
  }

  List<ChatMessage> get messages => _messages;
  bool get isOtherPartyTyping => _isOtherPartyTyping;

  Future<void> fetchHistory() async {
    try {
      final res = await ApiService.instance.get('/customer/bookings/$bookingId/messages');
      final rawList = (res['messages'] as List<dynamic>?) ?? [];
      _messages = rawList.map((j) => ChatMessage.fromJson(j as Map<String, dynamic>)).toList();
      notifyListeners();
    } catch (_) {
      // Ignore if no history or error
    }
  }

  Future<void> _initSocketListeners() async {
    await fetchHistory();
    await _socketService.connect();
    final socket = _socketService.socket;
    if (socket == null) return;

    // Join room
    socket.emit('join_booking', {'booking_id': bookingId});

    _onReceiveMessage = (data) {
      if (data['booking_id'] == bookingId) {
        final msg = ChatMessage.fromJson(data);
        _messages.add(msg);
        notifyListeners();
        
        // Emit read receipt
        socket.emit('read_receipt', {
          'booking_id': bookingId,
          'message_id': msg.id,
          'reader_id': currentUserId
        });
      }
    };

    _onTypingUpdate = (data) {
      if (data['booking_id'] == bookingId && data['sender_id'] != currentUserId) {
        _isOtherPartyTyping = data['is_typing'] ?? false;
        notifyListeners();
      }
    };

    _onMessageRead = (data) {
      if (data['booking_id'] == bookingId) {
        final msgId = data['message_id'];
        final idx = _messages.indexWhere((m) => m.id == msgId);
        if (idx != -1) {
          _messages[idx] = ChatMessage(
            id: _messages[idx].id,
            bookingId: _messages[idx].bookingId,
            senderId: _messages[idx].senderId,
            content: _messages[idx].content,
            timestamp: _messages[idx].timestamp,
            isRead: true,
          );
          notifyListeners();
        }
      }
    };

    // Listen to events using stored callback references
    socket.on('receive_message', _onReceiveMessage);
    socket.on('typing_update', _onTypingUpdate);
    socket.on('message_read', _onMessageRead);
  }

  void sendMessage(String text) {
    if (text.trim().isEmpty) return;
    
    final socket = _socketService.socket;
    if (socket == null) return;

    final msgId = DateTime.now().millisecondsSinceEpoch.toString();
    final data = {
      'id': msgId,
      'booking_id': bookingId,
      'sender_id': currentUserId,
      'message': text,
      'timestamp': DateTime.now().toIso8601String(),
    };

    // Optimistic UI
    final msg = ChatMessage.fromJson(data);
    _messages.add(msg);
    notifyListeners();

    socket.emit('send_message', data);
  }

  Future<void> sendMediaMessage(File file, String mediaType) async {
    final socket = _socketService.socket;
    if (socket == null) return;

    try {
      // 1. Upload via REST API
      final response = await ApiService.instance.uploadMultipart(
        '/uploads/booking-media',
        file.path,
        fields: {'booking_id': bookingId},
      );

      final url = response['url'] as String;
      final type = response['type'] as String; // 'image' or 'document'
      final name = response['name'] as String;
      final size = response['size'] as int;

      // 2. Emit via WebSocket
      final msgId = DateTime.now().millisecondsSinceEpoch.toString();
      final data = {
        'id': msgId,
        'booking_id': bookingId,
        'sender_id': currentUserId,
        'message': mediaType == 'document' ? '📄 $name' : '📷 Image',
        'timestamp': DateTime.now().toIso8601String(),
        'media_url': url,
        'media_type': type,
        'media_name': name,
        'media_size': size,
      };

      final msg = ChatMessage.fromJson(data);
      _messages.add(msg);
      notifyListeners();

      socket.emit('send_message', data);
    } catch (e) {
      debugPrint('Failed to send media: $e');
      rethrow;
    }
  }

  void setTyping(bool isTyping) {
    final socket = _socketService.socket;
    if (socket == null) return;

    socket.emit('typing_indicator', {
      'booking_id': bookingId,
      'sender_id': currentUserId,
      'is_typing': isTyping
    });
  }

  @override
  void dispose() {
    final socket = _socketService.socket;
    if (socket != null) {
      socket.emit('leave_booking', {'booking_id': bookingId});
      // Deregister only our specific callback references — not all global listeners
      socket.off('receive_message', _onReceiveMessage);
      socket.off('typing_update', _onTypingUpdate);
      socket.off('message_read', _onMessageRead);
    }
    _messages.clear();
    super.dispose();
  }
}
