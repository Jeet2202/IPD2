// File:
// lib/customer/normal_booking/schedule/schedule_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';
import '../../../utils/booking_slot_utils.dart';

class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  int _selectedDateIndex = 0;
  String _selectedTimeSlot = '10:30 AM';
  bool _preferPreviousPro = false;

  late List<DateCardItem> _dateCards;

  final List<String> _morningSlots = ['09:00 AM', '10:30 AM', '11:30 AM'];
  final List<String> _afternoonSlots = ['01:00 PM', '02:30 PM', '04:00 PM'];
  final List<String> _eveningSlots = ['05:30 PM', '07:00 PM', '08:30 PM'];

  List<String> get _allSlots => [..._morningSlots, ..._afternoonSlots, ..._eveningSlots];

  @override
  void initState() {
    super.initState();
    _dateCards = BookingSlotUtils.generateDateCards(days: 7, sampleSlots: _allSlots);
    _selectedDateIndex = BookingSlotUtils.getFirstAvailableDateIndex(_dateCards, _allSlots);

    final selectedDate = _dateCards[_selectedDateIndex].date;
    final available = _allSlots.where((s) => BookingSlotUtils.isSlotAvailable(s, selectedDate)).toList();
    if (available.isNotEmpty) {
      _selectedTimeSlot = available.first;
    }
  }

  @override
  Widget build(BuildContext context) {
    final selectedDate = _dateCards[_selectedDateIndex].date;

    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          children: [
            Text('step_3_of_4'.tr(context),
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
            ),
            Text('select_date_time'.tr(context),
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Date Selection Header ─────────────────────────────
                Text('select_date'.tr(context),
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                SizedBox(height: 14),

                // Horizontal Date Cards List
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  physics: const BouncingScrollPhysics(),
                  child: Row(
                    children: List.generate(_dateCards.length, (index) {
                      final item = _dateCards[index];
                      final isSelected = index == _selectedDateIndex;
                      final isAvail = BookingSlotUtils.hasAvailableSlots(_allSlots, item.date);

                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedDateIndex = index;
                            final newDate = _dateCards[index].date;
                            final avail = _allSlots.where((s) => BookingSlotUtils.isSlotAvailable(s, newDate)).toList();
                            if (avail.isNotEmpty && !avail.contains(_selectedTimeSlot)) {
                              _selectedTimeSlot = avail.first;
                            }
                          });
                        },
                        child: Container(
                          width: 90,
                          margin: EdgeInsets.only(right: 12),
                          padding: EdgeInsets.symmetric(vertical: 16),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? const Color(0xFF2563EB)
                                : (isAvail ? const Color(0xFFF8FAFC) : const Color(0xFFF1F5F9)),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
                              width: 1.5,
                            ),
                            boxShadow: [
                              if (isSelected)
                                BoxShadow(
                                  color: const Color(0xFF2563EB).withValues(alpha:0.3),
                                  blurRadius: 12,
                                  offset: const Offset(0, 4),
                                ),
                            ],
                          ),
                          child: Column(
                            children: [
                              Text(
                                item.dayLabel,
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: isSelected
                                      ? const Color(0xFFDBEAFE)
                                      : (isAvail ? const Color(0xFF64748B) : const Color(0xFF94A3B8)),
                                ),
                              ),
                              SizedBox(height: 6),
                              Text(
                                item.dateDisplay,
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w800,
                                  color: isSelected
                                      ? Colors.white
                                      : (isAvail ? const Color(0xFF0F172A) : const Color(0xFF94A3B8)),
                                ),
                              ),
                              SizedBox(height: 6),
                              Container(
                                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? Colors.white.withValues(alpha:0.2)
                                      : (isAvail ? const Color(0xFFEFF6FF) : const Color(0xFFE2E8F0)),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  isAvail ? 'Available' : 'Passed',
                                  style: TextStyle(
                                    fontSize: 9,
                                    fontWeight: FontWeight.w700,
                                    color: isSelected
                                        ? Colors.white
                                        : (isAvail ? const Color(0xFF2563EB) : const Color(0xFF64748B)),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    }),
                  ),
                ),

                SizedBox(height: 28),

                // ── Instant Booking Card Banner ───────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF0EA5E9), Color(0xFF2563EB)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(color: Colors.white.withValues(alpha:0.2), shape: BoxShape.circle),
                        child: Icon(Icons.bolt_rounded, color: Colors.white, size: 24),
                      ),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('need_immediate_assistance'.tr(context),
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Colors.white),
                            ),
                            SizedBox(height: 2),
                            Text('instant_pro_dispatch_available_within'.tr(context),
                              style: TextStyle(fontSize: 12, color: Color(0xFFE0F2FE)),
                            ),
                          ],
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.bookingAddress),
                        style: ElevatedButton.styleFrom(
                          foregroundColor: const Color(0xFF2563EB),
                          elevation: 0,
                          padding: EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: Text('book_now'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 28),

                // ── Time Slots Section ────────────────────────────────
                Text('select_time_slot'.tr(context),
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                SizedBox(height: 16),

                // Morning
                _buildSlotGroup('Morning Slots', Icons.wb_sunny_outlined, _morningSlots, selectedDate),
                SizedBox(height: 16),

                // Afternoon
                _buildSlotGroup('Afternoon Slots', Icons.wb_sunny_rounded, _afternoonSlots, selectedDate),
                SizedBox(height: 16),

                // Evening
                _buildSlotGroup('Evening Slots', Icons.nights_stay_outlined, _eveningSlots, selectedDate),

                SizedBox(height: 28),

                // ── Preferred Professional Toggle ─────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.person_pin_rounded, color: Color(0xFF2563EB), size: 26),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('prefer_previously_booked_pro'.tr(context),
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                            ),
                            SizedBox(height: 2),
                            Text('assign_ramesh_kumar_49_if'.tr(context),
                              style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                            ),
                          ],
                        ),
                      ),
                      Switch(
                        value: _preferPreviousPro,
                        activeThumbColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _preferPreviousPro = val),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Bottom Button ────────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withValues(alpha:0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    final dateStr = '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}';
                    Navigator.pushNamed(
                      context,
                      AppRoutes.priceEstimation,
                      arguments: {
                        'scheduled_date': dateStr,
                        'scheduled_time': _selectedTimeSlot,
                      },
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('view_price_estimation'.tr(context),
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                      ),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSlotGroup(String groupTitle, IconData icon, List<String> slots, DateTime selectedDate) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: const Color(0xFF64748B)),
            SizedBox(width: 6),
            Text(
              groupTitle,
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF64748B)),
            ),
          ],
        ),
        SizedBox(height: 10),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: slots.map((slot) {
            final isSelected = slot == _selectedTimeSlot;
            final isAvail = BookingSlotUtils.isSlotAvailable(slot, selectedDate);

            return ChoiceChip(
              label: Text(
                isAvail ? slot : '$slot (Passed)',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                  color: isSelected
                      ? Colors.white
                      : (isAvail ? const Color(0xFF334155) : const Color(0xFF94A3B8)),
                  decoration: isAvail ? TextDecoration.none : TextDecoration.lineThrough,
                ),
              ),
              selected: isSelected && isAvail,
              disabledColor: const Color(0xFFF1F5F9),
              backgroundColor: const Color(0xFFF8FAFC),
              selectedColor: const Color(0xFF2563EB),
              padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
                side: BorderSide(
                  color: isSelected
                      ? const Color(0xFF2563EB)
                      : (isAvail ? const Color(0xFFE2E8F0) : const Color(0xFFCBD5E1)),
                  width: 1.5,
                ),
              ),
              onSelected: isAvail ? (_) => setState(() => _selectedTimeSlot = slot) : null,
            );
          }).toList(),
        ),
      ],
    );
  }
}

