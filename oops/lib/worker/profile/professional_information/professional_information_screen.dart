// File: lib/worker/profile/professional_information/professional_information_screen.dart

import 'package:flutter/material.dart';

class WorkerProfessionalInformationScreen extends StatefulWidget {
  const WorkerProfessionalInformationScreen({super.key});

  @override
  State<WorkerProfessionalInformationScreen> createState() =>
      _WorkerProfessionalInformationScreenState();
}

class _WorkerProfessionalInformationScreenState
    extends State<WorkerProfessionalInformationScreen> {
  String _selectedProfession = 'Electrician';
  String _selectedExperience = '3-5 Years';
  String _selectedSkillLevel = 'Expert';

  final List<String> _professions = [
    'Electrician',
    'Plumber',
    'Painter',
    'Carpenter',
    'Mechanic',
    'AC Technician',
    'Welder',
    'Cleaning',
    'Gardening'
  ];

  final List<String> _experienceLevels = [
    '0-1 Year',
    '1-3 Years',
    '3-5 Years',
    '5+ Years'
  ];

  final List<String> _skillLevels = ['Beginner', 'Intermediate', 'Expert'];

  final List<String> _languages = ['Hindi', 'English', 'Punjabi', 'Bengali'];
  final Set<String> _selectedLanguages = {'Hindi', 'English'};

  double _workingRadius = 15.0; // in Km
  bool _ownVehicle = true;
  bool _ownTools = true;
  bool _availableFullTime = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Professional Details',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Onboarding Progress Header
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFF2563EB),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFF2563EB),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E8F0),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Text(
                'Step 2 of 3: Professional Skills & Work Setup',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2563EB),
                ),
              ),

              const SizedBox(height: 24),

              // Profession Selection Card
              _buildCardSection(
                title: 'Primary Profession',
                child: DropdownButtonFormField<String>(
                  value: _selectedProfession,
                  decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.work_outline_rounded,
                        color: Color(0xFF64748B)),
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide:
                          const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    ),
                  ),
                  icon: const Icon(Icons.keyboard_arrow_down_rounded,
                      color: Color(0xFF64748B)),
                  items: _professions.map((prof) {
                    return DropdownMenuItem(
                      value: prof,
                      child: Text(
                        prof,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) {
                      setState(() {
                        _selectedProfession = val;
                      });
                    }
                  },
                ),
              ),

              const SizedBox(height: 18),

              // Experience & Skill Level Card
              _buildCardSection(
                title: 'Experience & Skill Level',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Years of Experience',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF64748B),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _experienceLevels.map((exp) {
                        final selected = _selectedExperience == exp;
                        return ChoiceChip(
                          label: Text(exp),
                          selected: selected,
                          selectedColor: const Color(0xFFEFF6FF),
                          backgroundColor: const Color(0xFFF8FAFC),
                          labelStyle: TextStyle(
                            fontSize: 13,
                            fontWeight:
                                selected ? FontWeight.w700 : FontWeight.w500,
                            color: selected
                                ? const Color(0xFF2563EB)
                                : const Color(0xFF475569),
                          ),
                          side: BorderSide(
                            color: selected
                                ? const Color(0xFF2563EB)
                                : const Color(0xFFE2E8F0),
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          onSelected: (_) {
                            setState(() {
                              _selectedExperience = exp;
                            });
                          },
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Skill Level',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF64748B),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _skillLevels.map((lvl) {
                        final selected = _selectedSkillLevel == lvl;
                        return ChoiceChip(
                          label: Text(lvl),
                          selected: selected,
                          selectedColor: const Color(0xFFE0F2FE),
                          backgroundColor: const Color(0xFFF8FAFC),
                          labelStyle: TextStyle(
                            fontSize: 13,
                            fontWeight:
                                selected ? FontWeight.w700 : FontWeight.w500,
                            color: selected
                                ? const Color(0xFF0EA5E9)
                                : const Color(0xFF475569),
                          ),
                          side: BorderSide(
                            color: selected
                                ? const Color(0xFF0EA5E9)
                                : const Color(0xFFE2E8F0),
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          onSelected: (_) {
                            setState(() {
                              _selectedSkillLevel = lvl;
                            });
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Languages Known Card
              _buildCardSection(
                title: 'Languages Known',
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _languages.map((lang) {
                    final selected = _selectedLanguages.contains(lang);
                    return FilterChip(
                      label: Text(lang),
                      selected: selected,
                      selectedColor: const Color(0xFFEFF6FF),
                      backgroundColor: const Color(0xFFF8FAFC),
                      labelStyle: TextStyle(
                        fontSize: 13,
                        fontWeight:
                            selected ? FontWeight.w700 : FontWeight.w500,
                        color: selected
                            ? const Color(0xFF2563EB)
                            : const Color(0xFF475569),
                      ),
                      checkmarkColor: const Color(0xFF2563EB),
                      side: BorderSide(
                        color: selected
                            ? const Color(0xFF2563EB)
                            : const Color(0xFFE2E8F0),
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      onSelected: (bool value) {
                        setState(() {
                          if (value) {
                            _selectedLanguages.add(lang);
                          } else {
                            _selectedLanguages.remove(lang);
                          }
                        });
                      },
                    );
                  }).toList(),
                ),
              ),

              const SizedBox(height: 18),

              // Working Radius Slider Card
              _buildCardSection(
                title: 'Service Working Radius',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Maximum Distance',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            color: Color(0xFF64748B),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '${_workingRadius.round()} Km',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ),
                      ],
                    ),
                    SliderTheme(
                      data: SliderTheme.of(context).copyWith(
                        activeTrackColor: const Color(0xFF2563EB),
                        inactiveTrackColor: const Color(0xFFE2E8F0),
                        thumbColor: const Color(0xFF2563EB),
                        overlayColor: const Color(0xFF2563EB).withOpacity(0.12),
                      ),
                      child: Slider(
                        value: _workingRadius,
                        min: 3,
                        max: 50,
                        divisions: 47,
                        onChanged: (val) {
                          setState(() {
                            _workingRadius = val;
                          });
                        },
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Equipment & Availability Toggles Card
              _buildCardSection(
                title: 'Work Equipment & Schedule',
                child: Column(
                  children: [
                    _buildSwitchTile(
                      title: 'Own Transportation / Vehicle',
                      subtitle: 'Do you have a bike, scooter or van for travel?',
                      value: _ownVehicle,
                      onChanged: (val) => setState(() => _ownVehicle = val),
                    ),
                    const Divider(height: 24, color: Color(0xFFF1F5F9)),
                    _buildSwitchTile(
                      title: 'Own Toolkit & Equipment',
                      subtitle: 'Do you possess professional tools for jobs?',
                      value: _ownTools,
                      onChanged: (val) => setState(() => _ownTools = val),
                    ),
                    const Divider(height: 24, color: Color(0xFFF1F5F9)),
                    _buildSwitchTile(
                      title: 'Full-Time Daily Availability',
                      subtitle: 'Available to take bookings 6+ days a week?',
                      value: _availableFullTime,
                      onChanged: (val) =>
                          setState(() => _availableFullTime = val),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // Continue Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/worker/verification/kyc');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Continue to Identity Verification',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),
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
      padding: const EdgeInsets.all(18),
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
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 14),
          child,
        ],
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
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF0F172A),
                ),
              ),
              const SizedBox(height: 3),
              Text(
                subtitle,
                style: const TextStyle(
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
