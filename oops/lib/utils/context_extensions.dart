import 'package:flutter/material.dart';

extension ContextExtensions on BuildContext {
  // Theme
  ThemeData get theme       => Theme.of(this);
  TextTheme  get textTheme  => Theme.of(this).textTheme;
  ColorScheme get colors    => Theme.of(this).colorScheme;

  // Size
  Size   get screenSize   => MediaQuery.sizeOf(this);
  double get screenWidth  => screenSize.width;
  double get screenHeight => screenSize.height;

  // Navigation
  void push(String route, {Object? args}) =>
      Navigator.of(this).pushNamed(route, arguments: args);

  void pop([Object? result]) => Navigator.of(this).pop(result);

  void pushReplacement(String route, {Object? args}) =>
      Navigator.of(this).pushReplacementNamed(route, arguments: args);

  void pushAndClearStack(String route, {Object? args}) =>
      Navigator.of(this).pushNamedAndRemoveUntil(route, (_) => false, arguments: args);

  // SnackBar
  void showSnack(String msg, {bool isError = false}) {
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: isError ? Colors.red : Colors.green,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
