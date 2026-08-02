// File: lib/app/theme/app_motion.dart

import 'package:flutter/material.dart';

class AppMotion {
  AppMotion._();

  // Standard Durations
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration medium = Duration(milliseconds: 250);
  static const Duration slow = Duration(milliseconds: 400);

  // Standard Curves
  static const Curve easeOut = Curves.easeOutCubic;
  static const Curve easeIn = Curves.easeInCubic;
  static const Curve easeInOut = Curves.easeInOutCubic;
  static const Curve bounce = Curves.easeOutBack;
}
