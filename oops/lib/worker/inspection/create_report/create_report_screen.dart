// File: lib/worker/inspection/create_report/create_report_screen.dart

import 'package:flutter/material.dart';

class WorkerCreateReportScreen extends StatefulWidget {
  const WorkerCreateReportScreen({super.key});

  @override
  State<WorkerCreateReportScreen> createState() =>
      _WorkerCreateReportScreenState();
}

class _WorkerCreateReportScreenState extends State<WorkerCreateReportScreen> {
  String _rootCause = 'Drain Pipe Clogged with Debris';
  String _severity = 'Moderate';

  final List<String> _rootCauses = [
    'Drain Pipe Clogged with Debris',
    'Refrigerant Gas Leakage',
    'Faulty Blower Motor',
    'Compressor Capacitor Failure',
    'Damaged Insulation Coil',
  ];

  final List<String> _severities = ['Minor', 'Moderate', 'Critical'];

  final _findingsController = TextEditingController(
      text: 'Water drain outlet completely blocked by dust accumulation over 8 months. Minor oil residue found on suction valve indicating mild gas seep.');
  final _recommendationsController = TextEditingController(
      text: 'Deep chemical jet cleaning of drain line + Pressure testing & R32 gas refill (250g).');
  final _materialsController = TextEditingController(
      text: '1x Flexible Drain Pipe 3ft, R32 Refrigerant Can (250g), Foam Cleaner Spray');

  @override
  void dispose() {
    _findingsController.dispose();
    _recommendationsController.dispose();
    _materialsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Prepare Inspection Report',
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
              const Text(
                'Step 2 of 3: Formal Technical Report',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF8B5CF6),
                ),
              ),

              const SizedBox(height: 24),

              // Root Cause Dropdown Card
              _buildFieldLabel('Identified Root Cause'),
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
              _buildFieldLabel('Issue Severity Level'),
              const SizedBox(height: 8),
              Row(
                children: _severities.map((sev) {
                  final isSelected = _severity == sev;
                  final color = sev == 'Critical'
                      ? const Color(0xFFEF4444)
                      : (sev == 'Moderate'
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
              _buildFieldLabel('Detailed Technical Findings'),
              const SizedBox(height: 8),
              _buildTextArea(
                controller: _findingsController,
                hintText: 'Describe physical state of components...',
              ),

              const SizedBox(height: 18),

              // Recommended Solution
              _buildFieldLabel('Recommended Solution & Repairs'),
              const SizedBox(height: 8),
              _buildTextArea(
                controller: _recommendationsController,
                hintText: 'Outline action plan for repair...',
              ),

              const SizedBox(height: 18),

              // Required Spare Parts / Materials
              _buildFieldLabel('Required Materials & Spare Parts'),
              const SizedBox(height: 8),
              _buildTextArea(
                controller: _materialsController,
                hintText: 'List parts needed with specifications...',
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
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Generate Price Quotation',
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
