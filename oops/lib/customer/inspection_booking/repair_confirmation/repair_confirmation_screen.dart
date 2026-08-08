// File:
// lib/customer/inspection_booking/repair_confirmation/repair_confirmation_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class RepairConfirmationScreen extends StatelessWidget {
  const RepairConfirmationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        automaticallyImplyLeading: false,
        title: Text('repair_confirmed'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            children: [
              SizedBox(height: 10),

              // ── Hero Celebration Icon ─────────────────────────────────
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Color(0xFFDCFCE7),
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.check_circle_rounded, size: 54, color: Color(0xFF16A34A)),
              ),

              SizedBox(height: 18),

              Text('quotation_approved'.tr(context),
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF0F172A), letterSpacing: -0.4),
              ),

              SizedBox(height: 6),

              Text('sunil_verma_has_received_your'.tr(context),
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
              ),

              SizedBox(height: 28),

              // ── Summary Card ───────────────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('booking_id'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
                        Text('rep94812'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      ],
                    ),
                    SizedBox(height: 12),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 12),

                    Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                          child: Icon(Icons.engineering_rounded, color: Color(0xFF2563EB), size: 24),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('sunil_verma'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                              SizedBox(height: 2),
                              Text('senior_electrical_technician'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 16),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 12),

                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('agreed_total'.tr(context), style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                        Text('485000'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                      ],
                    ),
                    SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('est_work_duration'.tr(context), style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                        Text('45_minutes'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Action Buttons ─────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.repairTracking),
                  icon: Icon(Icons.speed_rounded, size: 20),
                  label: Text('track_live_repair_progress'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ),

              SizedBox(height: 12),

              SizedBox(
                width: double.infinity,
                height: 50,
                child: OutlinedButton(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.bookingDetails),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF64748B),
                    side: BorderSide(color: Color(0xFFCBD5E1)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('view_booking_summary'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
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
