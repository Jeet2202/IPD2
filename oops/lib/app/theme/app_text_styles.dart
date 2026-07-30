import 'package:flutter/material.dart';

class AppTextStyles {
  AppTextStyles._();

  static const String _fontFamily = 'Inter';

  static const TextTheme textTheme = TextTheme(
    displayLarge:  TextStyle(fontFamily: _fontFamily, fontSize: 57, fontWeight: FontWeight.w700),
    displayMedium: TextStyle(fontFamily: _fontFamily, fontSize: 45, fontWeight: FontWeight.w700),
    displaySmall:  TextStyle(fontFamily: _fontFamily, fontSize: 36, fontWeight: FontWeight.w600),

    headlineLarge:  TextStyle(fontFamily: _fontFamily, fontSize: 32, fontWeight: FontWeight.w600),
    headlineMedium: TextStyle(fontFamily: _fontFamily, fontSize: 28, fontWeight: FontWeight.w600),
    headlineSmall:  TextStyle(fontFamily: _fontFamily, fontSize: 24, fontWeight: FontWeight.w600),

    titleLarge:  TextStyle(fontFamily: _fontFamily, fontSize: 22, fontWeight: FontWeight.w600),
    titleMedium: TextStyle(fontFamily: _fontFamily, fontSize: 16, fontWeight: FontWeight.w500),
    titleSmall:  TextStyle(fontFamily: _fontFamily, fontSize: 14, fontWeight: FontWeight.w500),

    bodyLarge:  TextStyle(fontFamily: _fontFamily, fontSize: 16, fontWeight: FontWeight.w400),
    bodyMedium: TextStyle(fontFamily: _fontFamily, fontSize: 14, fontWeight: FontWeight.w400),
    bodySmall:  TextStyle(fontFamily: _fontFamily, fontSize: 12, fontWeight: FontWeight.w400),

    labelLarge:  TextStyle(fontFamily: _fontFamily, fontSize: 14, fontWeight: FontWeight.w500),
    labelMedium: TextStyle(fontFamily: _fontFamily, fontSize: 12, fontWeight: FontWeight.w500),
    labelSmall:  TextStyle(fontFamily: _fontFamily, fontSize: 11, fontWeight: FontWeight.w500),
  );
}
