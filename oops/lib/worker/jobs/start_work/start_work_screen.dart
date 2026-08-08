// File: lib/worker/jobs/start_work/start_work_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkerStartWorkScreen extends StatefulWidget {
  const WorkerStartWorkScreen({super.key});

  @override
  State<WorkerStartWorkScreen> createState() => _WorkerStartWorkScreenState();
}

class _WorkerStartWorkScreenState extends State<WorkerStartWorkScreen> {
  bool _safetyGear = true;
  bool _toolsCheck = true;
  bool _materialsReady = true;

  int _beforePhotosCount = 2;

  @override
  Widget build(BuildContext context) {
    final canStart = _safetyGear && _toolsCheck && _materialsReady;

    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'start_job_mock'.tr(context),
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
          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary Header Banner
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                      color: const Color(0xFF2563EB).withOpacity(0.2)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Color(0xFF2563EB),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.engineering_rounded,
                        color: Colors.white,
                        size: 26,
                      ),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'mcb_tripping_repair'.tr(context),
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'mock_customer_name_dwarka'.tr(context),
                            style: TextStyle(
                              fontSize: 12,
                              color: Color(0xFF64748B),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // Safety & Pre-work Checklist
              Text(
                'pre_start_verification'.tr(context),
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              SizedBox(height: 12),

              _buildCheckItem(
                title: 'checklist_safety_gear'.tr(context),
                value: _safetyGear,
                onChanged: (val) => setState(() => _safetyGear = val),
              ),
              SizedBox(height: 10),
              _buildCheckItem(
                title: 'checklist_tools_ready'.tr(context),
                value: _toolsCheck,
                onChanged: (val) => setState(() => _toolsCheck = val),
              ),
              SizedBox(height: 10),
              _buildCheckItem(
                title: 'checklist_materials_ready'.tr(context),
                value: _materialsReady,
                onChanged: (val) => setState(() => _materialsReady = val),
              ),

              SizedBox(height: 24),

              // Capture Before Photos Card
              Text(
                'capture_before_work_photos'.tr(context),
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0F172A),
                ),
              ),
              SizedBox(height: 6),
              Text(
                'capture_before_work_desc'.tr(context),
                style: TextStyle(
                  fontSize: 12,
                  color: Color(0xFF64748B),
                  height: 1.4,
                ),
              ),
              SizedBox(height: 12),

              Row(
                children: [
                  ...List.generate(_beforePhotosCount, (idx) {
                    return Container(
                      width: 84,
                      height: 84,
                      margin: EdgeInsets.only(right: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFD1FAE5),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFF10B981)),
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Icon(Icons.image_rounded,
                              color: Color(0xFF10B981), size: 32),
                          Positioned(
                            top: 4,
                            right: 4,
                            child: Container(
                              padding: EdgeInsets.all(2),
                              decoration: BoxDecoration(
                                color: Color(0xFF10B981),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(Icons.check,
                                  color: Colors.white, size: 10),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        _beforePhotosCount++;
                      });
                    },
                    child: Container(
                      width: 84,
                      height: 84,
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                            color: const Color(0xFF2563EB), width: 1.5),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_a_photo_outlined,
                              color: Color(0xFF2563EB), size: 24),
                          SizedBox(height: 4),
                          Text(
                            'add_photo'.tr(context),
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 32),

              // Start Work Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: canStart
                      ? () {
                          Navigator.pushNamed(
                              context, '/worker/jobs/work-progress');
                        }
                      : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: const Color(0xFFE2E8F0),
                    disabledForegroundColor: const Color(0xFF94A3B8),
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.play_arrow_rounded, size: 24),
                      SizedBox(width: 8),
                      Text(
                        'start_work_timer'.tr(context),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCheckItem({
    required String title,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      padding: EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: value ? const Color(0xFFEFF6FF) : const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: value ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
          width: value ? 1.5 : 1,
        ),
      ),
      child: Row(
        children: [
          Checkbox(
            value: value,
            activeColor: const Color(0xFF2563EB),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(5),
            ),
            onChanged: (v) => onChanged(v ?? false),
          ),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              title,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: Color(0xFF0F172A),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
