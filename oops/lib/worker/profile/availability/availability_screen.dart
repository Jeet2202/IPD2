// File: lib/worker/profile/availability/availability_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class WorkerAvailabilityScreen extends StatefulWidget {
  const WorkerAvailabilityScreen({super.key});

  @override
  State<WorkerAvailabilityScreen> createState() =>
      _WorkerAvailabilityScreenState();
}

class _WorkerAvailabilityScreenState extends State<WorkerAvailabilityScreen> {
  bool _isOnline = true;
  final Set<String> _selectedDays = {
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat'
  };
  final List<String> _daysOfWeek = [
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun'
  ];

  TimeOfDay _startTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _endTime = const TimeOfDay(hour: 19, minute: 0);
  String _breakTime = '1 PM - 2 PM';

  bool _instantBooking = true;
  bool _emergencyJobs = false;
  int _maxJobsPerDay = 5;

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'availability_settings'.tr(context),
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF0F172A)),
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Online / Offline Master Switch Card
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: _isOnline
                      ? const Color(0xFF2563EB)
                      : const Color(0xFF64748B),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: (_isOnline
                              ? const Color(0xFF2563EB)
                              : const Color(0xFF64748B))
                          .withOpacity(0.25),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        _isOnline
                            ? Icons.sensors_rounded
                            : Icons.sensors_off_rounded,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _isOnline
                                ? 'status_online'.tr(context)
                                : 'status_offline'.tr(context),
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            _isOnline
                                ? 'receiving_new_booking_requests'.tr(context)
                                : 'will_not_receive_new_jobs'.tr(context),
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.white.withOpacity(0.85),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Switch(
                      value: _isOnline,
                      activeColor: Colors.white,
                      activeTrackColor: const Color(0xFF0EA5E9),
                      inactiveThumbColor: Colors.white,
                      inactiveTrackColor: Colors.white.withOpacity(0.3),
                      onChanged: (val) {
                        setState(() {
                          _isOnline = val;
                        });
                      },
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // Working Days Selector
              _buildCardSection(
                title: 'working_days'.tr(context),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'select_days_open_service'.tr(context),
                      style: TextStyle(
                        fontSize: 13,
                        color: Color(0xFF64748B),
                      ),
                    ),
                    SizedBox(height: 14),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _daysOfWeek.map((day) {
                        final isSelected = _selectedDays.contains(day);
                        final dayKey = '${day.toLowerCase()}_short';
                        return FilterChip(
                          label: Text(dayKey.tr(context)),
                          selected: isSelected,
                          selectedColor: const Color(0xFFEFF6FF),
                          backgroundColor: const Color(0xFFF8FAFC),
                          labelStyle: TextStyle(
                            fontSize: 13,
                            fontWeight: isSelected
                                ? FontWeight.w700
                                : FontWeight.w500,
                            color: isSelected
                                ? const Color(0xFF2563EB)
                                : const Color(0xFF475569),
                          ),
                          checkmarkColor: const Color(0xFF2563EB),
                          side: BorderSide(
                            color: isSelected
                                ? const Color(0xFF2563EB)
                                : const Color(0xFFE2E8F0),
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          onSelected: (bool selected) {
                            setState(() {
                              if (selected) {
                                _selectedDays.add(day);
                              } else {
                                _selectedDays.remove(day);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 18),

              // Working Hours Card
              _buildCardSection(
                title: 'working_hours_break'.tr(context),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: _buildTimePickerBox(
                            label: 'start_time'.tr(context),
                            time: _startTime,
                            onTap: () async {
                              final picked = await showTimePicker(
                                context: context,
                                initialTime: _startTime,
                              );
                              if (picked != null) {
                                setState(() => _startTime = picked);
                              }
                            },
                          ),
                        ),
                        SizedBox(width: 14),
                        Expanded(
                          child: _buildTimePickerBox(
                            label: 'end_time'.tr(context),
                            time: _endTime,
                            onTap: () async {
                              final picked = await showTimePicker(
                                context: context,
                                initialTime: _endTime,
                              );
                              if (picked != null) {
                                setState(() => _endTime = picked);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.free_breakfast_outlined,
                                size: 18, color: Color(0xFF64748B)),
                            SizedBox(width: 8),
                            Text(
                              'break_time_slot'.tr(context),
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF334155),
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Text(
                            _breakTime,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 18),

              // Booking Preferences Card
              _buildCardSection(
                title: 'booking_preferences'.tr(context),
                child: Column(
                  children: [
                    _buildSwitchTile(
                      title: 'instant_booking_acceptance'.tr(context),
                      subtitle: 'auto_accept_instant_jobs'.tr(context),
                      value: _instantBooking,
                      onChanged: (val) => setState(() => _instantBooking = val),
                    ),
                    Divider(height: 24, color: Color(0xFFF1F5F9)),
                    _buildSwitchTile(
                      title: 'emergency_after_hours_jobs'.tr(context),
                      subtitle: 'receive_urgent_jobs_higher_earnings'.tr(context),
                      value: _emergencyJobs,
                      onChanged: (val) => setState(() => _emergencyJobs = val),
                    ),
                    Divider(height: 24, color: Color(0xFFF1F5F9)),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'max_jobs_per_day'.tr(context),
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'daily_job_capacity_limit'.tr(context),
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF64748B),
                              ),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            IconButton(
                              onPressed: _maxJobsPerDay > 1
                                  ? () => setState(() => _maxJobsPerDay--)
                                  : null,
                              icon: Icon(Icons.remove_circle_outline),
                              color: const Color(0xFF2563EB),
                            ),
                            Text(
                              '$_maxJobsPerDay',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            IconButton(
                              onPressed: _maxJobsPerDay < 15
                                  ? () => setState(() => _maxJobsPerDay++)
                                  : null,
                              icon: Icon(Icons.add_circle_outline),
                              color: const Color(0xFF2563EB),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 32),

              // Save Availability Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('availability_settings_updated_success'.tr(context)),
                        backgroundColor: const Color(0xFF10B981),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    'save_availability'.tr(context),
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCardSection({
    required String title,
    required Widget child,
  }) {
    return Container(
      padding: EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
          SizedBox(height: 14),
          child,
        ],
      ),
    );
  }

  Widget _buildTimePickerBox({
    required String label,
    required TimeOfDay time,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Color(0xFF64748B),
              ),
            ),
            SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  time.format(context),
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                Icon(Icons.access_time_rounded,
                    size: 16, color: Color(0xFF2563EB)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF0F172A),
                ),
              ),
              SizedBox(height: 3),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
        ),
        Switch(
          value: value,
          activeColor: const Color(0xFF2563EB),
          onChanged: onChanged,
        ),
      ],
    );
  }
}
