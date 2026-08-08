// File:
// lib/customer/inspection_booking/inspection_schedule/inspection_schedule_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';
import '../../../utils/booking_slot_utils.dart';

class InspectionScheduleScreen extends StatefulWidget {
  const InspectionScheduleScreen({super.key});

  @override
  State<InspectionScheduleScreen> createState() => _InspectionScheduleScreenState();
}

class _InspectionScheduleScreenState extends State<InspectionScheduleScreen> {
  int _selectedDateIndex = 0;
  String _selectedTimeSlot = '11:00 AM - 12:00 PM';
  bool _isExpressVisit = false;
  bool _preferSeniorTech = true;

  late List<DateCardItem> _dateCards;

  final List<String> _morningSlots = ['08:00 AM - 09:00 AM', '09:30 AM - 10:30 AM', '11:00 AM - 12:00 PM'];
  final List<String> _afternoonSlots = ['01:00 PM - 02:00 PM', '02:30 PM - 03:30 PM', '04:00 PM - 05:00 PM'];
  final List<String> _eveningSlots = ['05:30 PM - 06:30 PM', '07:00 PM - 08:00 PM'];

  List<String> get _allSlots => [..._morningSlots, ..._afternoonSlots, ..._eveningSlots];

  @override
  void initState() {
    super.initState();
    _dateCards = BookingSlotUtils.generateDateCards(days: 7, sampleSlots: _allSlots);
    _selectedDateIndex = BookingSlotUtils.getFirstAvailableDateIndex(_dateCards, _allSlots);

    final selectedDate = _dateCards[_selectedDateIndex].date;
    final avail = _allSlots.where((s) => BookingSlotUtils.isSlotAvailable(s, selectedDate)).toList();
    if (avail.isNotEmpty) {
      _selectedTimeSlot = avail.first;
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
        title: Text('schedule_visit'.tr(context),
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
                // ── Express Visit Banner Toggle ────────────────────────
                GestureDetector(
                  onTap: () => setState(() => _isExpressVisit = !_isExpressVisit),
                  child: Container(
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: _isExpressVisit ? const Color(0xFFEFF6FF) : Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _isExpressVisit ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
                        width: _isExpressVisit ? 2 : 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: _isExpressVisit ? const Color(0xFF2563EB) : const Color(0xFFF1F5F9),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.flash_on_rounded, color: _isExpressVisit ? Colors.white : const Color(0xFF2563EB), size: 22),
                        ),
                        SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('express_inspection_within_45_mins'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                              SizedBox(height: 2),
                              Text('nearest_expert_assigned_immediately'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                        Checkbox(
                          value: _isExpressVisit,
                          activeColor: const Color(0xFF2563EB),
                          onChanged: (val) => setState(() => _isExpressVisit = val!),
                        ),
                      ],
                    ),
                  ),
                ),

                SizedBox(height: 24),

                if (!_isExpressVisit) ...[
                  // ── Date Selector ────────────────────────────────────
                  Text('select_date'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                  SizedBox(height: 12),

                  SizedBox(
                    height: 80,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      physics: const BouncingScrollPhysics(),
                      itemCount: _dateCards.length,
                      itemBuilder: (context, index) {
                        final isSelected = _selectedDateIndex == index;
                        final item = _dateCards[index];
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
                            width: 72,
                            margin: EdgeInsets.only(right: 12),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? const Color(0xFF2563EB)
                                  : (isAvail ? Colors.white : const Color(0xFFF1F5F9)),
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  item.dayLabel,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isSelected
                                        ? const Color(0xFFDBEAFE)
                                        : (isAvail ? const Color(0xFF64748B) : const Color(0xFF94A3B8)),
                                  ),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  item.dateDisplay,
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w800,
                                    color: isSelected
                                        ? Colors.white
                                        : (isAvail ? const Color(0xFF0F172A) : const Color(0xFF94A3B8)),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),

                  SizedBox(height: 24),

                  // ── Time Slots ───────────────────────────────────────
                  Text('select_time_slot'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                  SizedBox(height: 12),

                  _buildSlotGroup('Morning', _morningSlots, selectedDate),
                  SizedBox(height: 12),
                  _buildSlotGroup('Afternoon', _afternoonSlots, selectedDate),
                  SizedBox(height: 12),
                  _buildSlotGroup('Evening', _eveningSlots, selectedDate),

                  SizedBox(height: 24),
                ],

                // ── Technician Preferences ────────────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.star_rounded, color: Color(0xFFFBBF24), size: 24),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('assign_toprated_inspector'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('48_rated_certified_experts_only'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                      Switch(
                        value: _preferSeniorTech,
                        activeThumbColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _preferSeniorTech = val),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 20),

                // ── Address Preview ──────────────────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12)),
                        child: Icon(Icons.location_on_rounded, color: Color(0xFF2563EB), size: 20),
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('inspection_address'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                            SizedBox(height: 2),
                            Text('house_402_green_avenue_hsr'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          ],
                        ),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.savedAddresses),
                        child: Text('change'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
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
                    final dateStr = '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}';
                    Navigator.pushNamed(
                      context,
                      AppRoutes.searchingProfessional,
                      arguments: {
                        'scheduled_date': dateStr,
                        'scheduled_time': _selectedTimeSlot,
                        'is_express': _isExpressVisit,
                      },
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('confirm_find_inspector_99'.tr(context),
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSlotGroup(String groupTitle, List<String> slots, DateTime selectedDate) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(groupTitle, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF94A3B8))),
        SizedBox(height: 6),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: slots.map((slot) {
            final isSelected = _selectedTimeSlot == slot;
            final isAvail = BookingSlotUtils.isSlotAvailable(slot, selectedDate);

            return ChoiceChip(
              label: Text(
                isAvail ? slot : '$slot (Passed)',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                  color: isSelected
                      ? Colors.white
                      : (isAvail ? const Color(0xFF0F172A) : const Color(0xFF94A3B8)),
                  decoration: isAvail ? TextDecoration.none : TextDecoration.lineThrough,
                ),
              ),
              selected: isSelected && isAvail,
              disabledColor: const Color(0xFFF1F5F9),
              selectedColor: const Color(0xFF2563EB),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(
                  color: isSelected
                      ? const Color(0xFF2563EB)
                      : (isAvail ? const Color(0xFFCBD5E1) : const Color(0xFFE2E8F0)),
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

