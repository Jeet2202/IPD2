// File: lib/worker/jobs/complete_work/complete_work_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkerCompleteWorkScreen extends StatefulWidget {
  const WorkerCompleteWorkScreen({super.key});

  @override
  State<WorkerCompleteWorkScreen> createState() =>
      _WorkerCompleteWorkScreenState();
}

class _WorkerCompleteWorkScreenState extends State<WorkerCompleteWorkScreen> {
  final _labourChargeController = TextEditingController(text: '850');
  final _partsChargeController = TextEditingController(text: '350');
  late final TextEditingController _completionNotesController;

  @override
  void initState() {
    super.initState();
    // Use addPostFrameCallback if context is not available immediately, but in initState for a stateful widget, we can access context in didChangeDependencies. Wait, actually we can just leave it uninitialized and initialize it in didChangeDependencies or build. Better yet, let's just initialize it empty here and set text in initState if possible? No, we can't use tr(context) in initState.
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _completionNotesController = TextEditingController(
      text: 'mock_completion_notes'.tr(context)
    );
  }

  int get _totalAmount {
    final l = int.tryParse(_labourChargeController.text) ?? 0;
    final p = int.tryParse(_partsChargeController.text) ?? 0;
    return l + p;
  }

  @override
  void dispose() {
    _labourChargeController.dispose();
    _partsChargeController.dispose();
    _completionNotesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'complete_job_invoice'.tr(context),
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
              // Completion Illustration Card
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 90,
                      height: 90,
                      decoration: BoxDecoration(
                        color: Color(0xFFD1FAE5),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.verified_rounded,
                        size: 52,
                        color: Color(0xFF10B981),
                      ),
                    ),
                    SizedBox(height: 14),
                    Text(
                      'work_finished_successfully'.tr(context),
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                        letterSpacing: -0.5,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'job_duration_mock'.tr(context),
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF64748B),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // Final Bill Breakdown Card
              _buildCardSection(
                title: 'payment_invoice_breakdown'.tr(context),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'labour_service_charge'.tr(context),
                          style: TextStyle(
                            fontSize: 13,
                            color: Color(0xFF64748B),
                          ),
                        ),
                        SizedBox(
                          width: 100,
                          height: 40,
                          child: TextField(
                            controller: _labourChargeController,
                            keyboardType: TextInputType.number,
                            textAlign: TextAlign.end,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                            decoration: InputDecoration(
                              prefixText: '₹ ',
                              contentPadding: EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 8),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    BorderSide(color: Color(0xFFE2E8F0)),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    BorderSide(color: Color(0xFF2563EB)),
                              ),
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'materials_spare_parts'.tr(context),
                          style: TextStyle(
                            fontSize: 13,
                            color: Color(0xFF64748B),
                          ),
                        ),
                        SizedBox(
                          width: 100,
                          height: 40,
                          child: TextField(
                            controller: _partsChargeController,
                            keyboardType: TextInputType.number,
                            textAlign: TextAlign.end,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                            decoration: InputDecoration(
                              prefixText: '₹ ',
                              contentPadding: EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 8),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    BorderSide(color: Color(0xFFE2E8F0)),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    BorderSide(color: Color(0xFF2563EB)),
                              ),
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 12),
                    Divider(color: Color(0xFFE2E8F0)),
                    SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'total_receivable_amount'.tr(context),
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        Text(
                          '₹ $_totalAmount',
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF10B981),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 18),

              // Upload After Photos Card
              _buildCardSection(
                title: 'upload_after_work_photos'.tr(context),
                child: Row(
                  children: [
                    Container(
                      width: 76,
                      height: 76,
                      decoration: BoxDecoration(
                        color: const Color(0xFFD1FAE5),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFF10B981)),
                      ),
                      child: Icon(Icons.check_circle_rounded,
                          color: Color(0xFF10B981), size: 32),
                    ),
                    SizedBox(width: 12),
                    GestureDetector(
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('photo_attached_successfully'.tr(context)),
                            backgroundColor: const Color(0xFF10B981),
                          ),
                        );
                      },
                      child: Container(
                        width: 76,
                        height: 76,
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
                                color: Color(0xFF2563EB), size: 22),
                            SizedBox(height: 4),
                            Text('add_photo'.tr(context),
                                style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF2563EB))),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 18),

              // Customer Signature Placeholder Card
              _buildCardSection(
                title: 'customer_sign_off_signature'.tr(context),
                child: Container(
                  height: 100,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFCBD5E1)),
                  ),
                  child: Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.draw_rounded,
                            color: Color(0xFF94A3B8), size: 22),
                        SizedBox(width: 8),
                        Text(
                          'customer_signature_verified'.tr(context),
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF475569),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              SizedBox(height: 18),

              // Completion Notes
              _buildCardSection(
                title: 'completion_report_remarks'.tr(context),
                child: TextField(
                  controller: _completionNotesController,
                  maxLines: 2,
                  decoration: InputDecoration(
                    hintText: 'final_remarks_hint'.tr(context),
                    hintStyle:
                        TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                    contentPadding: EdgeInsets.all(12),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide(color: Color(0xFFE2E8F0)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide:
                          BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    ),
                  ),
                ),
              ),

              SizedBox(height: 32),

              // Mark Job Completed Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    _showCompletionSuccessDialog(context);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF10B981),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.task_alt_rounded, size: 24),
                      SizedBox(width: 8),
                      Text(
                        'submit_final_invoice'.tr(context),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
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

  Widget _buildCardSection({
    required String title,
    required Widget child,
  }) {
    return Container(
      padding: EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
          SizedBox(height: 14),
          child,
        ],
      ),
    );
  }

  void _showCompletionSuccessDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(height: 12),
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Color(0xFFD1FAE5),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.stars_rounded,
                size: 52,
                color: Color(0xFF10B981),
              ),
            ),
            SizedBox(height: 20),
            Text(
              'mock_earned_amount'.tr(context),
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w900,
                color: Color(0xFF10B981),
              ),
            ),
            SizedBox(height: 6),
            Text(
              'payment_credited_to_wallet'.tr(context),
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: Color(0xFF64748B),
              ),
            ),
            SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pushReplacementNamed(context, '/worker/dashboard');
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Text(
                  'back_to_partner_dashboard'.tr(context),
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
