// File: lib/services/worker_dashboard_service.dart

import '../models/worker_dashboard_model.dart';
import 'api_service.dart';

class WorkerDashboardService {
  WorkerDashboardService._();
  static final WorkerDashboardService instance = WorkerDashboardService._();

  Future<WorkerDashboardData> fetchDashboardData() async {
    final res = await ApiService.instance.get('/worker/dashboard');
    return WorkerDashboardData.fromJson(res);
  }

  Future<bool> updateAvailability(String newStatus) async {
    final res = await ApiService.instance.put(
      '/worker/profile',
      {'availability': newStatus},
    );
    return res['availability'] == newStatus;
  }
}
