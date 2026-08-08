// File:
// lib/customer/bookings/reschedule_booking/reschedule_booking_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';
import '../../../utils/booking_slot_utils.dart';

class RescheduleBookingScreen extends StatefulWidget {
  const RescheduleBookingScreen({super.key});

  @override
  State<RescheduleBookingScreen> createState() => _RescheduleBookingScreenState();
}

class _RescheduleBookingScreenState extends State<RescheduleBookingScreen> {
  int _selectedDateIndex = 0;
  int _selectedTimeIndex = 0;
  String _selectedReason = 'Change in Personal Schedule';

  late List<DateCardItem> _dateCards;

  final List<String> _timeSlots = ['09:00 AM - 12:00 PM', '02:00 PM - 05:00 PM', '06:00 PM - 09:00 PM'];
  final List<String> _reasons = [
    'Change in Personal Schedule',
    'Emergency Work / Travel',
    'Prefer Different Time Slot',
    'Technician Delay Request',
  ];

  @override
  void initState() {
    super.initState();
    _dateCards = BookingSlotUtils.generateDateCards(days: 7, sampleSlots: _timeSlots);
    _selectedDateIndex = BookingSlotUtils.getFirstAvailableDateIndex(_dateCards, _timeSlots);

    final selectedDate = _dateCards[_selectedDateIndex].date;
    for (int i = 0; i < _timeSlots.length; i++) {
      if (BookingSlotUtils.isSlotAvailable(_timeSlots[i], selectedDate)) {
        _selectedTimeIndex = i;
        break;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final selectedDate = _dateCards[_selectedDateIndex].date;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('reschedule_booking'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Current Booking Header Card ────────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.calendar_month_rounded, color: Color(0xFF2563EB), size: 28),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('current_slot_31_jul_1100'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('booking_id_bk90214_electrical_db'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Select New Date ────────────────────────────────────
                Text('select_new_date'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                SizedBox(height: 12),

                SizedBox(
                  height: 50,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: _dateCards.length,
                    itemBuilder: (context, index) {
                      final isSelected = _selectedDateIndex == index;
                      final card = _dateCards[index];
                      final isAvail = BookingSlotUtils.hasAvailableSlots(_timeSlots, card.date);

                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedDateIndex = index;
                            final newDate = _dateCards[index].date;
                            for (int i = 0; i < _timeSlots.length; i++) {
                              if (BookingSlotUtils.isSlotAvailable(_timeSlots[i], newDate)) {
                                _selectedTimeIndex = i;
                                break;
                              }
                            }
                          });
                        },
                        child: Container(
                          margin: EdgeInsets.only(right: 10),
                          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? const Color(0xFF2563EB)
                                : (isAvail ? Colors.white : const Color(0xFFF1F5F9)),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                          ),
                          child: Center(
                            child: Text(
                              '${card.dayLabel} (${card.dateDisplay})',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                                color: isSelected
                                    ? Colors.white
                                    : (isAvail ? const Color(0xFF0F172A) : const Color(0xFF94A3B8)),
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),

                SizedBox(height: 24),

                // ── Select New Time ────────────────────────────────────
                Text('select_new_time_slot'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                SizedBox(height: 12),

                Column(
                  children: List.generate(_timeSlots.length, (index) {
                    final isSelected = _selectedTimeIndex == index;
                    final isAvail = BookingSlotUtils.isSlotAvailable(_timeSlots[index], selectedDate);

                    return GestureDetector(
                      onTap: isAvail ? () => setState(() => _selectedTimeIndex = index) : null,
                      child: Container(
                        margin: EdgeInsets.only(bottom: 10),
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        decoration: BoxDecoration(
                          color: isSelected && isAvail
                              ? const Color(0xFFEFF6FF)
                              : (isAvail ? Colors.white : const Color(0xFFF8FAFC)),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: isSelected && isAvail
                                ? const Color(0xFF2563EB)
                                : (isAvail ? const Color(0xFFE2E8F0) : const Color(0xFFCBD5E1)),
                            width: isSelected && isAvail ? 2 : 1,
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              isAvail ? _timeSlots[index] : '${_timeSlots[index]} (Passed)',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w700,
                                color: isSelected && isAvail
                                    ? const Color(0xFF2563EB)
                                    : (isAvail ? const Color(0xFF0F172A) : const Color(0xFF94A3B8)),
                                decoration: isAvail ? TextDecoration.none : TextDecoration.lineThrough,
                              ),
                            ),
                            Icon(
                              isSelected && isAvail
                                  ? Icons.radio_button_checked_rounded
                                  : Icons.radio_button_off_rounded,
                              color: isSelected && isAvail
                                  ? const Color(0xFF2563EB)
                                  : const Color(0xFFCBD5E1),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ),

                SizedBox(height: 20),

                // ── Reason Dropdown ────────────────────────────────────
                Text('reason_for_rescheduling'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                SizedBox(height: 8),

                Container(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _selectedReason,
                      isExpanded: true,
                      items: _reasons.map((r) => DropdownMenuItem(value: r, child: Text(r, style: TextStyle(fontSize: 13, color: Color(0xFF0F172A))))).toList(),
                      onChanged: (val) => setState(() => _selectedReason = val!),
                    ),
                  ),
                ),

                SizedBox(height: 20),

                // ── Free Policy Card ───────────────────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFDCFCE7),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 20),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text('free_rescheduling_available_up_to'.tr(context),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF14532D)),
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Confirm Button ──────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha: 0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('booking_rescheduled_successfully'.tr(context)), backgroundColor: Color(0xFF16A34A)),
                    );
                    Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('confirm_new_slot'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

