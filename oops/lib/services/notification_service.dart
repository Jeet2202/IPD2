import '../models/notification_model.dart';
import 'api_service.dart';

class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  Future<List<NotificationModel>> getNotifications({int skip = 0, int limit = 50}) async {
    final res = await ApiService.instance.get('/notifications', params: {
      'skip': skip.toString(),
      'limit': limit.toString(),
    });
    final list = res['items'] as List; // backend returns NotificationListResponse with 'items' and 'total'
    return list
        .map((e) => NotificationModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<int> getUnreadCount() async {
    final res = await ApiService.instance.get('/notifications/unread-count');
    return res['count'] as int? ?? 0;
  }

  Future<void> markAsRead(String id) async {
    await ApiService.instance.put('/notifications/read/$id', {});
  }

  Future<void> markAllRead() async {
    await ApiService.instance.put('/notifications/read-all', {});
  }

  Future<void> deleteNotification(String id) async {
    await ApiService.instance.delete('/notifications/$id');
  }

  Future<void> deleteAllRead() async {
    await ApiService.instance.delete('/notifications/read-all');
  }

  Future<Map<String, dynamic>> getPreferences() async {
    return await ApiService.instance.get('/notifications/preferences');
  }

  Future<void> updatePreferences(Map<String, dynamic> data) async {
    await ApiService.instance.put('/notifications/preferences', data);
  }
}
