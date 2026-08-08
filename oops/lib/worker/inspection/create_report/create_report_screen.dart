// File: lib/worker/inspection/create_report/create_report_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';
import '../../../../widgets/language_selector_widget.dart';

class WorkerCreateReportScreen extends StatefulWidget {
  const WorkerCreateReportScreen({super.key});

  @override
  State<WorkerCreateReportScreen> createState() =>
      _WorkerCreateReportScreenState();
}

class _WorkerCreateReportScreenState extends State<WorkerCreateReportScreen> {
  late String _rootCause;
  late String _severity;

  List<String> get _rootCauses => [
    'root_cause_drain_pipe_clogged'.tr(context),
    'root_cause_refrigerant_gas_leakage'.tr(context),
    'root_cause_faulty_blower_motor'.tr(context),
    'root_cause_compressor_capacitor_failure'.tr(context),
    'root_cause_damaged_insulation_coil'.tr(context),
  ];

  List<String> get _severities => [
    'severity_minor'.tr(context),
    'severity_moderate'.tr(context),
    'severity_critical'.tr(context),
  ];

  final _findingsController = TextEditingController(
      text: 'Water drain outlet completely blocked by dust accumulation over 8 months. Minor oil residue found on suction valve indicating mild gas seep.');
  final _recommendationsController = TextEditingController(
      text: 'Deep chemical jet cleaning of drain line + Pressure testing & R32 gas refill (250g).');
  final _materialsController = TextEditingController(
      text: '1x Flexible Drain Pipe 3ft, R32 Refrigerant Can (250g), Foam Cleaner Spray');

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _rootCause = 'root_cause_drain_pipe_clogged'.tr(context);
    _severity = 'severity_moderate'.tr(context);
  }

  @override
  void dispose() {
    _findingsController.dispose();
    _recommendationsController.dispose();
    _materialsController.dispose();
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
          'prepare_inspection_report'.tr(context),
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
                        color: const Color(0xFF8B5CF6),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                'step_2_of_3_formal_technical_report'.tr(context),
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF8B5CF6),
                ),
              ),

              const SizedBox(height: 24),

              // Root Cause Dropdown Card
              _buildFieldLabel('identified_root_cause'.tr(context)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _rootCause,
                decoration: InputDecoration(
                  prefixIcon: const Icon(Icons.psychology_outlined,
                      color: Color(0xFF8B5CF6)),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide:
                        const BorderSide(color: Color(0xFF8B5CF6), width: 1.5),
                  ),
                ),
                icon: const Icon(Icons.keyboard_arrow_down_rounded,
                    color: Color(0xFF64748B)),
                items: _rootCauses.map((cause) {
                  return DropdownMenuItem(
                    value: cause,
                    child: Text(
                      cause,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() => _rootCause = val);
                  }
                },
              ),

              const SizedBox(height: 20),

              // Issue Severity Selector
              _buildFieldLabel('issue_severity_level'.tr(context)),
              const SizedBox(height: 8),
              Row(
                children: _severities.map((sev) {
                  final isSelected = _severity == sev;
                  final color = sev == 'severity_critical'.tr(context)
                      ? const Color(0xFFEF4444)
                      : (sev == 'severity_moderate'.tr(context)
                          ? const Color(0xFFF59E0B)
                          : const Color(0xFF10B981));

                  return Expanded(
                    child: GestureDetector(
                      onTap: () {
                        setState(() => _severity = sev);
                      },
                      child: Container(
                        margin: const EdgeInsets.only(right: 8),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? color.withOpacity(0.12)
                              : const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: isSelected ? color : const Color(0xFFE2E8F0),
                            width: isSelected ? 1.5 : 1,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            sev,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: isSelected
                                  ? FontWeight.w800
                                  : FontWeight.w500,
                              color: isSelected ? color : const Color(0xFF475569),
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 20),

              // Inspection Findings
              _buildFieldLabel('detailed_technical_findings'.tr(context)),
              const SizedBox(height: 8),
              _buildTextArea(
                controller: _findingsController,
                hintText: 'describe_physical_state_hint'.tr(context),
              ),

              const SizedBox(height: 18),

              // Recommended Solution
              _buildFieldLabel('recommended_solution_repairs'.tr(context)),
              const SizedBox(height: 8),
              _buildTextArea(
                controller: _recommendationsController,
                hintText: 'outline_action_plan_hint'.tr(context),
              ),

              const SizedBox(height: 18),

              // Required Spare Parts / Materials
              _buildFieldLabel('required_materials_spare_parts'.tr(context)),
              const SizedBox(height: 8),
              _buildTextArea(
                controller: _materialsController,
                hintText: 'list_parts_needed_hint'.tr(context),
              ),

              const SizedBox(height: 32),

              // Continue to Quotation Generation Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                        context, '/worker/inspection/create-quotation');
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
                        'generate_price_quotation'.tr(context),
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

  Widget _buildFieldLabel(String label) {
    return Text(
      label,
      style: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: Color(0xFF334155),
      ),
    );
  }

  Widget _buildTextArea({
    required TextEditingController controller,
    required String hintText,
  }) {
    return TextField(
      controller: controller,
      maxLines: 3,
      decoration: InputDecoration(
        hintText: hintText,
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
    );
  }
}
