class NotificationModel {
  final String id;
  final String title;
  final String body;
  final String type;
  final Map<String, dynamic>? data;
  final bool isRead;
  final DateTime createdAt;

  const NotificationModel({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    this.data,
    this.isRead = false,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) =>
      NotificationModel(
        id:        json['_id'] as String,
        title:     json['title'] as String,
        body:      json['body'] as String,
        type:      json['type'] as String,
        data:      json['data'] as Map<String, dynamic>?,
        isRead:    json['isRead'] as bool? ?? false,
        createdAt: DateTime.parse(json['createdAt'] as String),
      );

  Map<String, dynamic> toJson() => {
        '_id':       id,
        'title':     title,
        'body':      body,
        'type':      type,
        'data':      data,
        'isRead':    isRead,
        'createdAt': createdAt.toIso8601String(),
      };
}
