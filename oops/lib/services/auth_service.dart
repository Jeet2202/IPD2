import '../models/user_model.dart';
import '../constants/api_endpoints.dart';
import 'api_service.dart';
import '../utils/token_storage.dart';

class AuthService {
  AuthService._();
  static final AuthService instance = AuthService._();

  Future<void> sendOtp(String phone) async {
    await ApiService.instance.post(ApiEndpoints.sendOtp, {'phone': phone});
  }

  Future<UserModel> verifyOtpAndLogin({
    required String phone,
    required String otp,
    required String role,
  }) async {
    final res = await ApiService.instance.post(ApiEndpoints.verifyOtp, {
      'phone': phone,
      'otp':   otp,
      'role':  role,
    });
    TokenStorage.save(
      access:  res['accessToken'] as String,
      refresh: res['refreshToken'] as String,
    );
    return UserModel.fromJson(res['user'] as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await ApiService.instance.post(ApiEndpoints.logout, {});
    TokenStorage.clear();
  }

  Future<void> forgotPassword(String phone) async {
    await ApiService.instance.post(ApiEndpoints.forgotPassword, {'phone': phone});
  }

  Future<void> resetPassword({
    required String otp,
    required String newPassword,
  }) async {
    await ApiService.instance.post(
      ApiEndpoints.resetPassword,
      {'otp': otp, 'newPassword': newPassword},
    );
  }
}
