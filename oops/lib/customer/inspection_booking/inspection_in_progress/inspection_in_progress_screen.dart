// File:
// lib/customer/inspection_booking/inspection_in_progress/inspection_in_progress_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class InspectionInProgressScreen extends StatefulWidget {
  const InspectionInProgressScreen({super.key});

  @override
  State<InspectionInProgressScreen> createState() => _InspectionInProgressScreenState();
}

class _InspectionInProgressScreenState extends State<InspectionInProgressScreen> {
  final List<Map<String, dynamic>> _steps = [
    {'title': 'Arrived at Location', 'time': '10:15 AM', 'done': true},
    {'title': 'Started Safety Audit & Testing', 'time': '10:18 AM', 'done': true},
    {'title': 'Testing Multimeter & Equipment', 'time': '10:25 AM', 'done': true},
    {'title': 'Identifying Root Cause of Issue', 'time': '10:32 AM', 'done': true},
    {'title': 'Preparing Digital Report & Quote', 'time': '10:40 AM', 'done': false, 'active': true},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('live_inspection_status'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Active Status Highlight ──────────────────────────────
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.28), blurRadius: 16, offset: const Offset(0, 6)),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), shape: BoxShape.circle),
                      child: Icon(Icons.saved_search_rounded, color: Colors.white, size: 30),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('diagnosis_active'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFDBEAFE))),
                          SizedBox(height: 2),
                          Text('inspecting_main_db_80'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.white)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Inspector Profile Card ─────────────────────────────
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
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                      child: Icon(Icons.engineering_rounded, size: 30, color: Color(0xFF2563EB)),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('sunil_verma'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('senior_inspector_on_site'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: Container(
                        padding: EdgeInsets.all(8),
                        decoration: BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                        child: Icon(Icons.call_rounded, color: Color(0xFF2563EB), size: 18),
                      ),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('calling_inspector_sunil_verma_91'.tr(context)), backgroundColor: Color(0xFF16A34A)),
                        );
                      },
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Timeline Card ───────────────────────────────────────
              Text('inspection_timeline'.tr(context), style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              SizedBox(height: 12),

              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: List.generate(_steps.length, (index) {
                    final step = _steps[index];
                    final isLast = index == _steps.length - 1;
                    final isDone = step['done'] as bool;
                    final isActive = step['active'] == true;

                    return IntrinsicHeight(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Column(
                            children: [
                              Container(
                                width: 26,
                                height: 26,
                                decoration: BoxDecoration(
                                  color: isDone
                                      ? const Color(0xFF16A34A)
                                      : (isActive ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                                  shape: BoxShape.circle,
                                ),
                                child: Center(
                                  child: isDone
                                      ? Icon(Icons.check_rounded, color: Colors.white, size: 14)
                                      : (isActive
                                          ? Container(width: 8, height: 8, decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle))
                                          : null),
                                ),
                              ),
                              if (!isLast)
                                Expanded(
                                  child: Container(
                                    width: 2,
                                    margin: EdgeInsets.symmetric(vertical: 4),
                                    color: isDone ? const Color(0xFF16A34A) : const Color(0xFFE2E8F0),
                                  ),
                                ),
                            ],
                          ),
                          SizedBox(width: 14),
                          Expanded(
                            child: Padding(
                              padding: EdgeInsets.only(bottom: 18.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        step['title'] as String,
                                        style: TextStyle(
                                          fontSize: 14,
                                          fontWeight: isDone || isActive ? FontWeight.w800 : FontWeight.w500,
                                          color: isDone || isActive ? const Color(0xFF0F172A) : const Color(0xFF94A3B8),
                                        ),
                                      ),
                                      Text(
                                        step['time'] as String,
                                        style: TextStyle(
                                          fontSize: 11,
                                          fontWeight: FontWeight.w700,
                                          color: isActive ? const Color(0xFF2563EB) : const Color(0xFF94A3B8),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ),
              ),

              SizedBox(height: 24),

              // ── Inspector Notes Card ─────────────────────────────────
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFFBEB),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFFFCD34D)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.notes_rounded, color: Color(0xFFD97706), size: 20),
                    SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('live_observation_by_sunil'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFFB45309))),
                          SizedBox(height: 2),
                          Text(
                            '"Detected thermal burn on 32A DP MCB terminal. Generating itemized repair quote..."',
                            style: TextStyle(fontSize: 12, color: Color(0xFF92400E), height: 1.4),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Support Row ──────────────────────────────────────────
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.customerChat),
                      icon: Icon(Icons.chat_outlined, size: 18),
                      label: Text('chat_with_sunil'.tr(context)),
                      style: OutlinedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 14),
                        side: BorderSide(color: Color(0xFF2563EB)),
                        foregroundColor: const Color(0xFF2563EB),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.helpSupport),
                      icon: Icon(Icons.support_agent_rounded, size: 18),
                      label: Text('contact_support'.tr(context)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.inspectionReport),
                  icon: Icon(Icons.assessment_rounded, size: 20),
                  label: Text('view_diagnostic_report_quote'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF16A34A),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
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
}
