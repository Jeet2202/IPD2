import '../models/user_model.dart';
import '../constants/api_endpoints.dart';
import 'api_service.dart';

class UserService {
  UserService._();
  static final UserService instance = UserService._();

  Future<UserModel> getProfile() async {
    final res = await ApiService.instance.get(ApiEndpoints.customerProfile);
    return UserModel.fromJson(res['user'] as Map<String, dynamic>);
  }

  Future<UserModel> updateProfile(Map<String, dynamic> data) async {
    final res = await ApiService.instance.put(ApiEndpoints.customerProfile, data);
    return UserModel.fromJson(res['user'] as Map<String, dynamic>);
  }

  Future<void> updateFcmToken(String token) async {
    await ApiService.instance.post('/auth/fcm-token', {'token': token});
  }

  Future<void> deleteAccount() async {
    await ApiService.instance.delete('/auth/account');
  }
}
