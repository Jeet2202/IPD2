// File: lib/worker/jobs/arrival/mark_arrival_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkerMarkArrivalScreen extends StatefulWidget {
  const WorkerMarkArrivalScreen({super.key});

  @override
  State<WorkerMarkArrivalScreen> createState() =>
      _WorkerMarkArrivalScreenState();
}

class _WorkerMarkArrivalScreenState extends State<WorkerMarkArrivalScreen> {
  bool _gpsVerified = true;
  bool _selfieCaptured = false;
  final _arrivalNotesController = TextEditingController();

  @override
  void dispose() {
    _arrivalNotesController.dispose();
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
          'confirm_arrival'.tr(context),
          style: const TextStyle(
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
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Success Arrival Graphic Container
              Container(
                width: 100,
                height: 100,
                decoration: const BoxDecoration(
                  color: Color(0xFFD1FAE5),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.pin_drop_rounded,
                  size: 54,
                  color: Color(0xFF10B981),
                ),
              ),

              const SizedBox(height: 20),

              Text(
                'you_have_arrived'.tr(context),
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'mock_arrival_address'.tr(context),
                style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF64748B),
                ),
              ),

              const SizedBox(height: 24),

              // GPS Verification Badge Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: _gpsVerified
                      ? const Color(0xFFEFF6FF)
                      : const Color(0xFFFEF3C7),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _gpsVerified
                        ? const Color(0xFF2563EB).withOpacity(0.3)
                        : const Color(0xFFF59E0B),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      _gpsVerified
                          ? Icons.gps_fixed_rounded
                          : Icons.gps_not_fixed_rounded,
                      color: _gpsVerified
                          ? const Color(0xFF2563EB)
                          : const Color(0xFFD97706),
                      size: 22,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _gpsVerified
                            ? 'gps_location_confirmed'.tr(context)
                            : 'verifying_gps_proximity'.tr(context),
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: _gpsVerified
                              ? const Color(0xFF2563EB)
                              : const Color(0xFFB45309),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Optional Arrival Selfie Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.03),
                      blurRadius: 10,
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        color: _selfieCaptured
                            ? const Color(0xFFD1FAE5)
                            : const Color(0xFFF1F5F9),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        _selfieCaptured
                            ? Icons.check_circle_rounded
                            : Icons.camera_front_rounded,
                        color: _selfieCaptured
                            ? const Color(0xFF10B981)
                            : const Color(0xFF64748B),
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'arrival_selfie_photo'.tr(context),
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _selfieCaptured
                                ? 'photo_attached_successfully'.tr(context)
                                : 'optional_verification_photo'.tr(context),
                            style: const TextStyle(
                              fontSize: 12,
                              color: Color(0xFF64748B),
                            ),
                          ),
                        ],
                      ),
                    ),
                    OutlinedButton(
                      onPressed: () {
                        setState(() {
                          _selfieCaptured = !_selfieCaptured;
                        });
                      },
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 8),
                        side: const BorderSide(color: Color(0xFF2563EB)),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: Text(
                        _selfieCaptured ? 'retake'.tr(context) : 'capture'.tr(context),
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF2563EB),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Customer Note / Gate Instructions Field
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'arrival_remarks'.tr(context),
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF334155),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _arrivalNotesController,
                maxLines: 2,
                decoration: InputDecoration(
                  hintText: 'arrival_remarks_hint'.tr(context),
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
                    borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // Continue to Start Work Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/worker/jobs/start-work');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
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
                        'proceed_to_start_work'.tr(context),
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
