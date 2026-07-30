import '../models/notification_model.dart';
import '../constants/api_endpoints.dart';
import 'api_service.dart';

class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  Future<List<NotificationModel>> getNotifications() async {
    final res = await ApiService.instance.get(ApiEndpoints.customerNotifications);
    final list = res['notifications'] as List;
    return list
        .map((e) => NotificationModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> markAsRead(String id) async {
    await ApiService.instance.put('/notifications/$id/read', {});
  }

  Future<void> markAllRead() async {
    await ApiService.instance.put('/notifications/read-all', {});
  }

  Future<void> deleteNotification(String id) async {
    await ApiService.instance.delete('/notifications/$id');
  }
}
