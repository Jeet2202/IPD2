import 'package:intl/intl.dart';

extension DateTimeExtensions on DateTime {
  String get toDisplayDate  => DateFormat('dd MMM yyyy').format(this);
  String get toDisplayTime  => DateFormat('hh:mm a').format(this);
  String get toDisplayDateTime => DateFormat('dd MMM yyyy, hh:mm a').format(this);
  String get toApiFormat    => toIso8601String();

  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  bool get isTomorrow {
    final tomorrow = DateTime.now().add(const Duration(days: 1));
    return year == tomorrow.year && month == tomorrow.month && day == tomorrow.day;
  }

  String get relativeDisplay {
    if (isToday)     return 'Today';
    if (isTomorrow)  return 'Tomorrow';
    return toDisplayDate;
  }
}

extension NumExtensions on num {
  String get toRupees => '₹${toStringAsFixed(2)}';
  String get toKm     => '${toStringAsFixed(1)} km';
}

extension StringExtensions on String {
  String get capitalised =>
      isNotEmpty ? '${this[0].toUpperCase()}${substring(1)}' : this;

  String get toTitleCase => split(' ').map((w) => w.capitalised).join(' ');

  bool get isValidEmail =>
      RegExp(r'^[\w.+-]+@[\w-]+\.[a-z]{2,}$').hasMatch(this);

  bool get isValidIndianPhone => RegExp(r'^[6-9]\d{9}$').hasMatch(this);
}
