// File:
// lib/customer/normal_booking/work_in_progress/work_in_progress_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkInProgressScreen extends StatefulWidget {
  const WorkInProgressScreen({super.key});

  @override
  State<WorkInProgressScreen> createState() => _WorkInProgressScreenState();
}

class _WorkInProgressScreenState extends State<WorkInProgressScreen> {
  final List<Map<String, dynamic>> _checklist = [
    {'title': 'Main MCB Power Isolation', 'done': true},
    {'title': 'Dismantling old switchboard', 'done': true},
    {'title': 'New Havells 16A modular board installation', 'done': true},
    {'title': 'Internal copper wiring connection', 'done': false, 'active': true},
    {'title': 'Voltage load testing & safety check', 'done': false},
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
        title: Text('work_in_progress'.tr(context),
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
              // ── Live Status Banner Card ──────────────────────────────
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
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.25), blurRadius: 16, offset: const Offset(0, 6)),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), shape: BoxShape.circle),
                      child: Icon(Icons.build_circle_rounded, color: Colors.white, size: 30),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('live_service_active'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFDBEAFE))),
                          SizedBox(height: 2),
                          Text('work_in_progress_65'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Colors.white)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Worker Info Card ──────────────────────────────────────
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
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                      child: Icon(Icons.person_rounded, size: 32, color: Color(0xFF2563EB)),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('ramesh_kumar'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('senior_electrician_on_site'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: Container(
                        padding: EdgeInsets.all(8),
                        decoration: BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                        child: Icon(Icons.call_rounded, color: Color(0xFF2563EB), size: 18),
                      ),
                      onPressed: () {},
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Time & Progress Card ──────────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('work_progress'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                        Text('65'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                      ],
                    ),
                    SizedBox(height: 12),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: const LinearProgressIndicator(
                        value: 0.65,
                        minHeight: 10,
                        backgroundColor: Color(0xFFF1F5F9),
                        color: Color(0xFF2563EB),
                      ),
                    ),
                    SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('started_at'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                            SizedBox(height: 2),
                            Text('1035_am'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                          ],
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text('est_completion'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                            SizedBox(height: 2),
                            Text('1115_am_15_mins'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Task Checklist ────────────────────────────────────────
              Text('live_task_checklist'.tr(context),
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
              SizedBox(height: 12),

              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: List.generate(_checklist.length, (index) {
                    final task = _checklist[index];
                    final isDone = task['done'] as bool;
                    final isActive = task['active'] == true;

                    return Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Row(
                        children: [
                          Icon(
                            isDone
                                ? Icons.check_circle_rounded
                                : (isActive ? Icons.play_circle_fill_rounded : Icons.radio_button_unchecked_rounded),
                            color: isDone
                                ? const Color(0xFF16A34A)
                                : (isActive ? const Color(0xFF2563EB) : const Color(0xFFCBD5E1)),
                            size: 22,
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              task['title'] as String,
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: isDone || isActive ? FontWeight.w700 : FontWeight.w500,
                                color: isDone || isActive ? const Color(0xFF0F172A) : const Color(0xFF94A3B8),
                              ),
                            ),
                          ),
                          if (isActive)
                            Container(
                              padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(6)),
                              child: Text('in_progress'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                            ),
                        ],
                      ),
                    );
                  }),
                ),
              ),

              SizedBox(height: 24),

              // ── Professional Notes ────────────────────────────────────
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
                          Text('note_from_ramesh'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFFB45309))),
                          SizedBox(height: 2),
                          Text(
                            '"Replaced damaged copper terminal wire. Board installation almost ready for testing."',
                            style: TextStyle(fontSize: 12, color: Color(0xFF92400E), height: 1.4),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Action Buttons ────────────────────────────────────────
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: Icon(Icons.add_circle_outline_rounded, size: 18),
                      label: Text('add_more_work'.tr(context)),
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
                      onPressed: () {},
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

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
