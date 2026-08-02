import '../constants/app_constants.dart';

class Validators {
  Validators._();

  static String? name(String? value) {
    if (value == null || value.trim().isEmpty) return 'Full name is required';
    if (value.trim().length < 2) return 'Name must be at least 2 characters';
    return null;
  }

  static String? email(String? value) {
    if (value == null || value.trim().isEmpty) return 'Email address is required';
    final emailTrimmed = value.trim();
    final emailRegExp = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegExp.hasMatch(emailTrimmed)) return 'Please enter a valid email address';
    return null;
  }

  static String? phone(String? value) {
    if (value == null || value.trim().isEmpty) return 'Phone number is required';
    if (!AppConstants.phoneRegex.hasMatch(value.trim())) {
      return 'Please enter a valid phone number';
    }
    return null;
  }

  static String? password(String? value) {
    if (value == null || value.isEmpty) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters';
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!RegExp(r'[a-z]').hasMatch(value)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!RegExp(r'\d').hasMatch(value)) {
      return 'Password must contain at least one number';
    }
    if (!RegExp(r'[^A-Za-z0-9]').hasMatch(value)) {
      return 'Password must contain at least one special character';
    }
    return null;
  }

  static String? confirmPassword(String? value, String password) {
    if (value == null || value.isEmpty) return 'Please confirm your password';
    if (value != password) return 'Passwords do not match';
    return null;
  }

  static String? otp(String? value) {
    if (value == null || value.trim().isEmpty) return 'OTP code is required';
    if (value.trim().length != 6) return 'OTP must be 6 digits';
    return null;
  }

  static String? pincode(String? value) {
    if (value == null || value.trim().isEmpty) return 'Pincode is required';
    if (!AppConstants.pinRegex.hasMatch(value.trim())) return 'Enter a valid 6-digit pincode';
    return null;
  }
}
