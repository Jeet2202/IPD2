// File: lib/worker/inspection/inspection_checklist/inspection_checklist_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';
import '../../../../widgets/language_selector_widget.dart';

class WorkerInspectionChecklistScreen extends StatefulWidget {
  const WorkerInspectionChecklistScreen({super.key});

  @override
  State<WorkerInspectionChecklistScreen> createState() =>
      _WorkerInspectionChecklistScreenState();
}

class _WorkerInspectionChecklistScreenState
    extends State<WorkerInspectionChecklistScreen> {
  final Map<String, bool> _checklist = {
    'chk_visual_indoor_outdoor': true,
    'chk_drain_pipe_blockage': true,
    'chk_compressor_noise': true,
    'chk_refrigerant_pressure': false,
    'chk_blower_fan_motor': false,
    'chk_electrical_wiring': true,
  };

  final _inspectionNotesController = TextEditingController(
      text: 'Drain tray clogged with dust sludge causing overflow. Gas pressure slightly low (55 PSI).');

  @override
  void dispose() {
    _inspectionNotesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'inspection_checklist'.tr(context),
          style: const TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF8B5CF6)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Progress Stepper Header
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFF8B5CF6),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFF8B5CF6),
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
              Text(
                'step_1_of_3_checklist'.tr(context),
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF8B5CF6),
                ),
              ),

              const SizedBox(height: 24),

              // Checklist Section
              Text(
                'diagnostic_check_items'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 12),

              ..._checklist.keys.map((item) {
                final isChecked = _checklist[item]!;
                return Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isChecked
                        ? const Color(0xFFF3E8FF)
                        : const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isChecked
                          ? const Color(0xFF8B5CF6)
                          : const Color(0xFFE2E8F0),
                      width: isChecked ? 1.5 : 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      Checkbox(
                        value: isChecked,
                        activeColor: const Color(0xFF8B5CF6),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(5),
                        ),
                        onChanged: (val) {
                          setState(() {
                            _checklist[item] = val ?? false;
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          item.tr(context),
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: isChecked
                                ? FontWeight.w700
                                : FontWeight.w500,
                            color: isChecked
                                ? const Color(0xFF5B21B6)
                                : const Color(0xFF334155),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),

              const SizedBox(height: 20),

              // Media Upload Section
              Text(
                'inspection_evidence'.tr(context),
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0F172A),
                ),
              ),
              const SizedBox(height: 10),

              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('inspection_photo_captured'.tr(context)),
                            backgroundColor: const Color(0xFF8B5CF6),
                          ),
                        );
                      },
                      icon: const Icon(Icons.camera_alt_outlined, size: 18),
                      label: Text('capture_photo'.tr(context)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF8B5CF6),
                        side: const BorderSide(color: Color(0xFF8B5CF6)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('inspection_video_recorded'.tr(context)),
                            backgroundColor: const Color(0xFF0EA5E9),
                          ),
                        );
                      },
                      icon: const Icon(Icons.videocam_outlined, size: 18),
                      label: Text('record_clip'.tr(context)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF0EA5E9),
                        side: const BorderSide(color: Color(0xFF0EA5E9)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Diagnostic Notes
              Text(
                'diagnostic_observations_notes'.tr(context),
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF334155),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _inspectionNotesController,
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'enter_technical_findings_hint'.tr(context),
                  hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding: const EdgeInsets.all(14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFF8B5CF6), width: 1.5),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // Continue to Create Report Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                        context, '/worker/inspection/create-report');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF8B5CF6),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'proceed_to_create_report'.tr(context),
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
