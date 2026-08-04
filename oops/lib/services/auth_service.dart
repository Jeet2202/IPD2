import 'package:flutter/foundation.dart';
import '../constants/api_endpoints.dart';
import '../models/user_model.dart';
import '../utils/token_storage.dart';
import 'api_service.dart';
import 'push_notification_service.dart';

class AuthService {
  AuthService._();
  static final AuthService instance = AuthService._();

  /// Register a new Customer or Worker account
  Future<Map<String, dynamic>> register({
    required String email,
    required String phone,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'customer',
  }) async {
    final res = await ApiService.instance.post(ApiEndpoints.register, {
      'email': email,
      'phone': phone,
      'password': password,
      'first_name': firstName,
      'last_name': lastName,
      'role': role,
    });
    return res;
  }

  /// Verify email OTP and complete authentication
  Future<UserModel> verifyEmail({
    required String email,
    required String code,
  }) async {
    final res = await ApiService.instance.post(ApiEndpoints.verifyEmail, {
      'email': email,
      'code': code,
    });

    final data = res['data'] as Map<String, dynamic>;
    final tokens = data['tokens'] as Map<String, dynamic>;
    final user = data['user'] as Map<String, dynamic>;
    TokenStorage.save(
      access: tokens['access_token'] as String,
      refresh: tokens['refresh_token'] as String,
      userId: (user['id'] ?? user['_id'])?.toString(),
      userRole: user['role'] as String?,
    );

    // Initialize push notifications safely
    try {
      await PushNotificationService.instance.initialize();
    } catch (e) {
      debugPrint('FCM init ignored during verifyEmailOtp: $e');
    }

    return UserModel.fromJson(user);
  }

  /// Resend verification OTP code
  Future<void> resendEmailOtp({
    required String email,
    String purpose = 'registration',
  }) async {
    await ApiService.instance.post(ApiEndpoints.resendEmailOtp, {
      'email': email,
      'purpose': purpose,
    });
  }

  /// Authenticate existing user with Email/Phone & Password
  Future<UserModel> login({
    required String emailOrPhone,
    required String password,
    String? role,
  }) async {
    final bool isEmail = emailOrPhone.contains('@');
    final res = await ApiService.instance.post(ApiEndpoints.login, {
      if (isEmail) 'email': emailOrPhone else 'phone': emailOrPhone,
      'password': password,
      if (role != null) 'role': role,
    });

    final data = res['data'] as Map<String, dynamic>;
    final tokens = data['tokens'] as Map<String, dynamic>;
    final user = data['user'] as Map<String, dynamic>;
    TokenStorage.save(
      access: tokens['access_token'] as String,
      refresh: tokens['refresh_token'] as String,
      userId: (user['id'] ?? user['_id'])?.toString(),
      userRole: user['role'] as String?,
    );

    // Initialize push notifications safely
    try {
      await PushNotificationService.instance.initialize();
    } catch (e) {
      debugPrint('FCM init ignored during login: $e');
    }

    return UserModel.fromJson(user);
  }

  /// Get current user profile
  Future<UserModel> getMe() async {
    final res = await ApiService.instance.get(ApiEndpoints.me);
    final data = res['data'] as Map<String, dynamic>;
    return UserModel.fromJson(data['user'] as Map<String, dynamic>);
  }

  /// Refresh Access Token
  Future<void> refresh() async {
    final res = await ApiService.instance.post(ApiEndpoints.refreshToken, {
      'refresh_token': TokenStorage.refreshToken,
    });

    final data = res['data'] as Map<String, dynamic>;
    TokenStorage.save(
      access: data['access_token'] as String,
      refresh: data['refresh_token'] as String,
    );
  }

  /// Request Password Reset OTP
  Future<void> forgotPassword(String email) async {
    await ApiService.instance.post(ApiEndpoints.forgotPassword, {'email': email});
  }

  /// Verify Password Reset OTP and get temporary reset_token
  Future<String> verifyPasswordResetOtp({
    required String email,
    required String otpCode,
  }) async {
    final res = await ApiService.instance.post(
      ApiEndpoints.verifyPasswordResetOtp,
      {'email': email, 'otp_code': otpCode},
    );
    final data = res['data'] as Map<String, dynamic>;
    return data['reset_token'] as String;
  }

  /// Reset Password using reset_token
  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    await ApiService.instance.post(
      ApiEndpoints.resetPassword,
      {'token': token, 'new_password': newPassword},
    );
  }

  /// Change password for authenticated user
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await ApiService.instance.post(ApiEndpoints.changePassword, {
      'current_password': currentPassword,
      'new_password': newPassword,
    });
    await PushNotificationService.instance.removeDeviceToken();
    TokenStorage.clear();
  }

  /// Logout current device session
  Future<void> logout() async {
    try {
      if (TokenStorage.refreshToken.isNotEmpty) {
        await PushNotificationService.instance.removeDeviceToken();
        await ApiService.instance.post(ApiEndpoints.logout, {
          'refresh_token': TokenStorage.refreshToken,
        });
      }
    } catch (_) {}
    TokenStorage.clear();
  }

  /// Logout from all devices
  Future<void> logoutAll() async {
    try {
      await PushNotificationService.instance.removeDeviceToken();
      await ApiService.instance.post(ApiEndpoints.logoutAll, {});
    } catch (_) {}
    TokenStorage.clear();
  }

  /// Delete current user account permanently
  Future<void> deleteAccount(String password) async {
    await PushNotificationService.instance.removeDeviceToken();
    await ApiService.instance.delete(
      ApiEndpoints.deleteAccount,
      body: {'password': password},
    );
    TokenStorage.clear();
  }

  /// Fetch customer profile data
  Future<Map<String, dynamic>> fetchCustomerProfile() async {
    final res = await ApiService.instance.get(ApiEndpoints.customerProfile);
    return res;
  }

  /// Update customer profile details
  Future<Map<String, dynamic>> updateCustomerProfile(Map<String, dynamic> data) async {
    final res = await ApiService.instance.put(ApiEndpoints.customerProfile, data);
    return res;
  }

  /// Fetch worker profile data
  Future<Map<String, dynamic>> fetchWorkerProfile() async {
    final res = await ApiService.instance.get(ApiEndpoints.workerProfile);
    return res;
  }

  /// Update worker profile details
  Future<Map<String, dynamic>> updateWorkerProfile(Map<String, dynamic> data) async {
    final res = await ApiService.instance.put(ApiEndpoints.workerProfile, data);
    return res;
  }

  /// Upload customer profile photo
  Future<Map<String, dynamic>> uploadCustomerProfilePhoto(String filePath) async {
    return await ApiService.instance.uploadMultipart(
      ApiEndpoints.customerProfilePhoto,
      filePath,
    );
  }

  /// Delete customer profile photo
  Future<Map<String, dynamic>> deleteCustomerProfilePhoto() async {
    return await ApiService.instance.delete(ApiEndpoints.customerProfilePhoto);
  }

  /// Upload worker profile photo
  Future<Map<String, dynamic>> uploadWorkerProfilePhoto(String filePath) async {
    return await ApiService.instance.uploadMultipart(
      ApiEndpoints.workerProfilePhoto,
      filePath,
    );
  }

  /// Delete worker profile photo
  Future<Map<String, dynamic>> deleteWorkerProfilePhoto() async {
    return await ApiService.instance.delete(ApiEndpoints.workerProfilePhoto);
  }
}
