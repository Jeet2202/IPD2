// File: lib/services/language_service.dart

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageService {
  LanguageService._();
  static final LanguageService instance = LanguageService._();

  static const String _prefLanguageKey = 'selected_app_language';

  final ValueNotifier<Locale> currentLocale = ValueNotifier<Locale>(const Locale('en'));

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final savedLang = prefs.getString(_prefLanguageKey) ?? 'en';
    currentLocale.value = Locale(savedLang);
  }

  Future<void> changeLanguage(String languageCode) async {
    if (!['en', 'hi', 'mr'].contains(languageCode)) return;
    currentLocale.value = Locale(languageCode);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefLanguageKey, languageCode);
  }

  String get currentLanguageCode => currentLocale.value.languageCode;
}
