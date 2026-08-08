// File: lib/utils/booking_slot_utils.dart

import 'package:intl/intl.dart';

class DateCardItem {
  final String dayLabel; // e.g. 'Today', 'Tomorrow', 'Fri'
  final String dateDisplay; // e.g. '8 Aug', '08 Aug'
  final DateTime date;
  final bool isAvailable;

  const DateCardItem({
    required this.dayLabel,
    required this.dateDisplay,
    required this.date,
    this.isAvailable = true,
  });
}

class BookingSlotUtils {
  BookingSlotUtils._();

  /// Parses a slot time string into a DateTime on [targetDate].
  /// Supports formats such as:
  /// - "09:00 AM"
  /// - "09:00 AM - 11:00 AM"
  /// - "09:00 - 11:00"
  /// - "09:00"
  static DateTime? parseSlotStartTime(String slotStr, DateTime targetDate) {
    if (slotStr.trim().isEmpty) return null;

    try {
      // Extract the start time part (before '-' if range)
      String startPart = slotStr.split('-')[0].trim();

      int hour = 0;
      int minute = 0;

      // Check for AM/PM format
      final upperStr = startPart.toUpperCase();
      final isPm = upperStr.contains('PM');
      final isAm = upperStr.contains('AM');

      // Remove AM/PM letters
      startPart = startPart.replaceAll(RegExp(r'[A-Za-z]'), '').trim();

      final parts = startPart.split(':');
      if (parts.isEmpty) return null;

      hour = int.parse(parts[0]);
      if (parts.length > 1) {
        minute = int.parse(parts[1]);
      }

      if (isPm && hour < 12) {
        hour += 12;
      } else if (isAm && hour == 12) {
        hour = 0;
      }

      return DateTime(targetDate.year, targetDate.month, targetDate.day, hour, minute);
    } catch (_) {
      return null;
    }
  }

  /// Determines whether a time slot on [selectedDate] is in the future relative to [now].
  /// If [selectedDate] is a future day, returns true.
  /// If [selectedDate] is a past day, returns false.
  /// If [selectedDate] is today, compares the slot start time against [now] (plus optional [bufferMinutes]).
  static bool isSlotAvailable(
    String slotStr,
    DateTime selectedDate, {
    DateTime? now,
    int bufferMinutes = 0,
  }) {
    final currentNow = now ?? DateTime.now();
    final today = DateTime(currentNow.year, currentNow.month, currentNow.day);
    final targetDay = DateTime(selectedDate.year, selectedDate.month, selectedDate.day);

    if (targetDay.isAfter(today)) {
      return true;
    }

    if (targetDay.isBefore(today)) {
      return false;
    }

    // It's Today: check if slot start time is after current time + buffer
    final slotDt = parseSlotStartTime(slotStr, selectedDate);
    if (slotDt == null) {
      return true; // Fallback to available if parsing fails
    }

    final cutoff = currentNow.add(Duration(minutes: bufferMinutes));
    return slotDt.isAfter(cutoff);
  }

  /// Checks if any slot in [slots] is available on [selectedDate].
  static bool hasAvailableSlots(
    List<String> slots,
    DateTime selectedDate, {
    DateTime? now,
    int bufferMinutes = 0,
  }) {
    for (final slot in slots) {
      if (isSlotAvailable(slot, selectedDate, now: now, bufferMinutes: bufferMinutes)) {
        return true;
      }
    }
    return false;
  }

  /// Generates a list of [DateCardItem] starting from Today for [days] count.
  static List<DateCardItem> generateDateCards({
    int days = 7,
    List<String>? sampleSlots,
    DateTime? now,
  }) {
    final currentNow = now ?? DateTime.now();
    final today = DateTime(currentNow.year, currentNow.month, currentNow.day);
    final list = <DateCardItem>[];

    final weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    for (int i = 0; i < days; i++) {
      final date = today.add(Duration(days: i));
      String dayLabel;
      if (i == 0) {
        dayLabel = 'Today';
      } else if (i == 1) {
        dayLabel = 'Tomorrow';
      } else {
        dayLabel = weekdayNames[date.weekday - 1];
      }

      final dateDisplay = DateFormat('d MMM').format(date);

      bool isAvail = true;
      if (i == 0 && sampleSlots != null && sampleSlots.isNotEmpty) {
        isAvail = hasAvailableSlots(sampleSlots, date, now: currentNow);
      }

      list.add(DateCardItem(
        dayLabel: dayLabel,
        dateDisplay: dateDisplay,
        date: date,
        isAvailable: isAvail,
      ));
    }

    return list;
  }

  /// Finds the index of the first date card that has available slots.
  /// If Today (index 0) has available slots, returns 0.
  /// Otherwise returns 1 (Tomorrow).
  static int getFirstAvailableDateIndex(
    List<DateCardItem> cards,
    List<String> timeSlots, {
    DateTime? now,
  }) {
    if (cards.isEmpty) return 0;

    final currentNow = now ?? DateTime.now();
    if (hasAvailableSlots(timeSlots, cards[0].date, now: currentNow)) {
      return 0;
    }

    return cards.length > 1 ? 1 : 0;
  }
}
