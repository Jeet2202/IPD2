class ChatMessage {
  final String id;
  final String bookingId;
  final String senderId;
  final String content;
  final DateTime timestamp;
  final bool isRead;
  
  // Media fields
  final String? mediaUrl;
  final String? mediaType; // 'image', 'document'
  final String? mediaName;
  final int? mediaSize;

  ChatMessage({
    required this.id,
    required this.bookingId,
    required this.senderId,
    required this.content,
    required this.timestamp,
    this.isRead = false,
    this.mediaUrl,
    this.mediaType,
    this.mediaName,
    this.mediaSize,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      bookingId: json['booking_id'] ?? '',
      senderId: json['sender_id'] ?? '',
      content: json['message'] ?? '',
      timestamp: json['timestamp'] != null 
          ? DateTime.parse(json['timestamp']) 
          : DateTime.now(),
      isRead: json['is_read'] ?? false,
      mediaUrl: json['media_url'],
      mediaType: json['media_type'],
      mediaName: json['media_name'],
      mediaSize: json['media_size'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'booking_id': bookingId,
      'sender_id': senderId,
      'message': content,
      'timestamp': timestamp.toIso8601String(),
      'is_read': isRead,
      if (mediaUrl != null) 'media_url': mediaUrl,
      if (mediaType != null) 'media_type': mediaType,
      if (mediaName != null) 'media_name': mediaName,
      if (mediaSize != null) 'media_size': mediaSize,
    };
  }
}
