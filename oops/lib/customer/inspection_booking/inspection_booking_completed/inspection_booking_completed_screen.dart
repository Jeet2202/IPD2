// File:
// lib/customer/inspection_booking/inspection_booking_completed/inspection_booking_completed_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class InspectionBookingCompletedScreen extends StatefulWidget {
  const InspectionBookingCompletedScreen({super.key});

  @override
  State<InspectionBookingCompletedScreen> createState() => _InspectionBookingCompletedScreenState();
}

class _InspectionBookingCompletedScreenState extends State<InspectionBookingCompletedScreen> {
  int _userRating = 5;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        automaticallyImplyLeading: false,
        title: Text('booking_complete'.tr(context),
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

              // ── Success Celebration Graphic ───────────────────────────
              Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  color: Color(0xFFDCFCE7),
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.verified_rounded, size: 60, color: Color(0xFF16A34A)),
              ),

              SizedBox(height: 18),

              Text('repair_successfully_completed'.tr(context),
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF0F172A), letterSpacing: -0.4),
              ),

              SizedBox(height: 6),

              Text('your_main_db_box_repair'.tr(context),
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
              ),

              SizedBox(height: 28),

              // ── Rating Professional Card ──────────────────────────────
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
                    Text('rate_sunils_work'.tr(context), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                    SizedBox(height: 12),

                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(5, (index) {
                        final starIndex = index + 1;
                        return IconButton(
                          icon: Icon(
                            starIndex <= _userRating ? Icons.star_rounded : Icons.star_outline_rounded,
                            color: const Color(0xFFFBBF24),
                            size: 32,
                          ),
                          onPressed: () => setState(() => _userRating = starIndex),
                        );
                      }),
                    ),

                    SizedBox(height: 6),
                    Text('great_quality_work'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF16A34A))),
                  ],
                ),
              ),

              SizedBox(height: 20),

              // ── Payment & Invoice Summary ──────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('total_amount_paid'.tr(context), style: TextStyle(fontSize: 14, color: Color(0xFF64748B))),
                        Text('485000'.tr(context), style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                      ],
                    ),
                    SizedBox(height: 16),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 14),

                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => Navigator.pushNamed(context, AppRoutes.bookingDetails),
                            icon: Icon(Icons.receipt_long_rounded, size: 18),
                            label: Text('download_invoice'.tr(context)),
                            style: OutlinedButton.styleFrom(
                              padding: EdgeInsets.symmetric(vertical: 12),
                              side: BorderSide(color: Color(0xFFE2E8F0)),
                              foregroundColor: const Color(0xFF0F172A),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ),
                        SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => Navigator.pushNamed(context, AppRoutes.inspectionReport),
                            icon: Icon(Icons.assessment_outlined, size: 18),
                            label: Text('full_report'.tr(context)),
                            style: OutlinedButton.styleFrom(
                              padding: EdgeInsets.symmetric(vertical: 12),
                              side: BorderSide(color: Color(0xFFE2E8F0)),
                              foregroundColor: const Color(0xFF0F172A),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Action Buttons ─────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerHome, (route) => false);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('return_to_home'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                ),
              ),

              SizedBox(height: 12),

              TextButton(
                onPressed: () => Navigator.pushNamed(context, AppRoutes.customerServices),
                child: Text('book_another_inspection_service'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
