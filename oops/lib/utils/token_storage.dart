/// In-memory token store — replace with flutter_secure_storage in production.
class TokenStorage {
  TokenStorage._();

  static String? _access;
  static String? _refresh;

  static String get accessToken  => _access  ?? '';
  static String get refreshToken => _refresh ?? '';
  static bool   get hasToken     => _access != null && _access!.isNotEmpty;

  static void save({required String access, required String refresh}) {
    _access  = access;
    _refresh = refresh;
  }

  static void clear() {
    _access  = null;
    _refresh = null;
  }
}
