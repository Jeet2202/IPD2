// File:
// lib/customer/inspection_booking/inspection_schedule/inspection_schedule_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

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

  final List<Map<String, String>> _dateCards = [
    {'day': 'Today', 'date': '31 Jul'},
    {'day': 'Fri', 'date': '01 Aug'},
    {'day': 'Sat', 'date': '02 Aug'},
    {'day': 'Sun', 'date': '03 Aug'},
    {'day': 'Mon', 'date': '04 Aug'},
  ];

  final List<String> _morningSlots = ['08:00 AM - 09:00 AM', '09:30 AM - 10:30 AM', '11:00 AM - 12:00 PM'];
  final List<String> _afternoonSlots = ['01:00 PM - 02:00 PM', '02:30 PM - 03:30 PM', '04:00 PM - 05:00 PM'];
  final List<String> _eveningSlots = ['05:30 PM - 06:30 PM', '07:00 PM - 08:00 PM'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Schedule Visit',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Express Visit Banner Toggle ────────────────────────
                GestureDetector(
                  onTap: () => setState(() => _isExpressVisit = !_isExpressVisit),
                  child: Container(
                    padding: const EdgeInsets.all(16),
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
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: _isExpressVisit ? const Color(0xFF2563EB) : const Color(0xFFF1F5F9),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.flash_on_rounded, color: _isExpressVisit ? Colors.white : const Color(0xFF2563EB), size: 22),
                        ),
                        const SizedBox(width: 14),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Express Inspection (Within 45 Mins)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                              SizedBox(height: 2),
                              Text('Nearest expert assigned immediately', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
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

                const SizedBox(height: 24),

                if (!_isExpressVisit) ...[
                  // ── Date Selector ────────────────────────────────────
                  const Text('Select Date', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                  const SizedBox(height: 12),

                  SizedBox(
                    height: 80,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      physics: const BouncingScrollPhysics(),
                      itemCount: _dateCards.length,
                      itemBuilder: (context, index) {
                        final isSelected = _selectedDateIndex == index;
                        final item = _dateCards[index];
                        return GestureDetector(
                          onTap: () => setState(() => _selectedDateIndex = index),
                          child: Container(
                            width: 72,
                            margin: const EdgeInsets.only(right: 12),
                            decoration: BoxDecoration(
                              color: isSelected ? const Color(0xFF2563EB) : Colors.white,
                              borderRadius: BorderRadius.circular(18),
                              border: Border.all(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  item['day']!,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isSelected ? const Color(0xFFDBEAFE) : const Color(0xFF64748B),
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  item['date']!,
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.w800,
                                    color: isSelected ? Colors.white : const Color(0xFF0F172A),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),

                  const SizedBox(height: 24),

                  // ── Time Slots ───────────────────────────────────────
                  const Text('Select Time Slot', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                  const SizedBox(height: 12),

                  _buildSlotGroup('Morning', _morningSlots),
                  const SizedBox(height: 12),
                  _buildSlotGroup('Afternoon', _afternoonSlots),
                  const SizedBox(height: 12),
                  _buildSlotGroup('Evening', _eveningSlots),

                  const SizedBox(height: 24),
                ],

                // ── Technician Preferences ────────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.star_rounded, color: Color(0xFFFBBF24), size: 24),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Assign Top-Rated Inspector', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('4.8+ rated certified experts only', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                      Switch(
                        value: _preferSeniorTech,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _preferSeniorTech = val),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // ── Address Preview ──────────────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(12)),
                        child: const Icon(Icons.location_on_rounded, color: Color(0xFF2563EB), size: 20),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Inspection Address', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                            SizedBox(height: 2),
                            Text('House #402, Green Avenue, HSR Sector 6', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          ],
                        ),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.savedAddresses),
                        child: const Text('Change', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Confirm Button ──────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.searchingProfessional),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text(
                    'Confirm & Find Inspector (₹99)',
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

  Widget _buildSlotGroup(String groupTitle, List<String> slots) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(groupTitle, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF94A3B8))),
        const SizedBox(height: 6),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: slots.map((slot) {
            final isSelected = _selectedTimeSlot == slot;
            return ChoiceChip(
              label: Text(slot),
              selected: isSelected,
              selectedColor: const Color(0xFF2563EB),
              labelStyle: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                color: isSelected ? Colors.white : const Color(0xFF0F172A),
              ),
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFCBD5E1)),
              ),
              onSelected: (_) => setState(() => _selectedTimeSlot = slot),
            );
          }).toList(),
        ),
      ],
    );
  }
}
