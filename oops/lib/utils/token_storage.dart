import 'package:shared_preferences/shared_preferences.dart';

/// Secure persistent token store using SharedPreferences
class TokenStorage {
  TokenStorage._();

  static SharedPreferences? _prefs;
  static String? _access;
  static String? _refresh;

  static const String _keyAccess = 'kaamsetu_access_token';
  static const String _keyRefresh = 'kaamsetu_refresh_token';

  /// Initialize persistent storage and load saved tokens at app startup
  static Future<void> init() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      _access = _prefs?.getString(_keyAccess);
      _refresh = _prefs?.getString(_keyRefresh);
    } catch (_) {
      // Fallback if shared_preferences fails
    }
  }

  static String get accessToken => _access ?? '';
  static String get refreshToken => _refresh ?? '';
  static bool get hasToken => _access != null && _access!.isNotEmpty;

  static void save({required String access, required String refresh}) {
    _access = access;
    _refresh = refresh;
    _prefs?.setString(_keyAccess, access);
    _prefs?.setString(_keyRefresh, refresh);
  }

  static void clear() {
    _access = null;
    _refresh = null;
    _prefs?.remove(_keyAccess);
    _prefs?.remove(_keyRefresh);
  }
}
