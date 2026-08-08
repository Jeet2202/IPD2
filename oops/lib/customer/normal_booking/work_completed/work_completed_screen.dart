// File:
// lib/customer/normal_booking/work_completed/work_completed_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkCompletedScreen extends StatelessWidget {
  const WorkCompletedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.close_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('service_completed'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(height: 10),

                // ── Hero Success Graphic / Badge ───────────────────────
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: const Color(0xFFDCFCE7),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(color: const Color(0xFF16A34A).withOpacity(0.2), blurRadius: 20, offset: const Offset(0, 6)),
                    ],
                  ),
                  child: Center(
                    child: Icon(Icons.task_alt_rounded, color: Color(0xFF16A34A), size: 60),
                  ),
                ),

                SizedBox(height: 20),

                Text('work_completed_successfully'.tr(context),
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF0F172A), letterSpacing: -0.4),
                ),
                SizedBox(height: 6),
                Text('ramesh_kumar_has_finished_the'.tr(context),
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                ),

                SizedBox(height: 28),

                // ── Duration & Summary Card ───────────────────────────
                Container(
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(Icons.electrical_services_rounded, color: Color(0xFF2563EB), size: 22),
                          SizedBox(width: 10),
                          Expanded(
                            child: Text('switchboard_wiring_repair'.tr(context),
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 16),
                      Divider(color: Color(0xFFE2E8F0), height: 1),
                      SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildMetaItem('Professional', 'Ramesh Kumar'),
                          _buildMetaItem('Total Time', '42 Minutes'),
                          _buildMetaItem('Finished At', '11:17 AM'),
                        ],
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Before & After Photos Gallery ──────────────────────
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text('before_after_proof_photos'.tr(context),
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                  ),
                ),
                SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(
                      child: Container(
                        height: 110,
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF2F2),
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: const Color(0xFFFCA5A5)),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.broken_image_rounded, color: Color(0xFFEF4444), size: 30),
                            SizedBox(height: 6),
                            Text('before'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
                          ],
                        ),
                      ),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Container(
                        height: 110,
                        decoration: BoxDecoration(
                          color: const Color(0xFFDCFCE7),
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: const Color(0xFF86EFAC)),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.verified_rounded, color: Color(0xFF16A34A), size: 30),
                            SizedBox(height: 6),
                            Text('after'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 24),

                // ── Completed Checklist Summary ────────────────────────
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text('completed_tasks_list'.tr(context),
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                  ),
                ),
                SizedBox(height: 10),

                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      _TaskRow(title: 'Replaced faulty 16A modular switchboard'),
                      SizedBox(height: 8),
                      _TaskRow(title: 'Fixed loose wire connections in main line'),
                      SizedBox(height: 8),
                      _TaskRow(title: 'Completed high-voltage safety audit'),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Proceed to Payment Button ────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
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
                  onPressed: () {
                    // Navigate to Payment
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('proceed_to_payment_377'.tr(context),
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                      ),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetaItem(String title, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
        SizedBox(height: 2),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
      ],
    );
  }
}

class _TaskRow extends StatelessWidget {
  final String title;
  const _TaskRow({required this.title});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(Icons.check_circle_rounded, color: Color(0xFF16A34A), size: 18),
        SizedBox(width: 10),
        Expanded(child: Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF0F172A)))),
      ],
    );
  }
}
