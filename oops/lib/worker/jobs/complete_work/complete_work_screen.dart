// File: lib/worker/jobs/complete_work/complete_work_screen.dart

import 'package:flutter/material.dart';

class WorkerCompleteWorkScreen extends StatefulWidget {
  const WorkerCompleteWorkScreen({super.key});

  @override
  State<WorkerCompleteWorkScreen> createState() =>
      _WorkerCompleteWorkScreenState();
}

class _WorkerCompleteWorkScreenState extends State<WorkerCompleteWorkScreen> {
  final _labourChargeController = TextEditingController(text: '850');
  final _partsChargeController = TextEditingController(text: '350');
  final _completionNotesController = TextEditingController(
      text: 'Replaced burnt MCB unit with 32A Havells single pole switch. Tested voltage across all phases.');

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
          'Complete Job & Invoice',
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
              // Completion Illustration Card
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 90,
                      height: 90,
                      decoration: const BoxDecoration(
                        color: Color(0xFFD1FAE5),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.verified_rounded,
                        size: 52,
                        color: Color(0xFF10B981),
                      ),
                    ),
                    const SizedBox(height: 14),
                    const Text(
                      'Work Finished Successfully!',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Job Duration: 38 Minutes',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF64748B),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // Final Bill Breakdown Card
              _buildCardSection(
                title: 'Payment & Invoice Breakdown',
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Labour / Service Charge',
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
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                            decoration: InputDecoration(
                              prefixText: '₹ ',
                              contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 8),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    const BorderSide(color: Color(0xFFE2E8F0)),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    const BorderSide(color: Color(0xFF2563EB)),
                              ),
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Materials / Spare Parts',
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
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                            decoration: InputDecoration(
                              prefixText: '₹ ',
                              contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 8),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    const BorderSide(color: Color(0xFFE2E8F0)),
                              ),
                              focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                                borderSide:
                                    const BorderSide(color: Color(0xFF2563EB)),
                              ),
                            ),
                            onChanged: (_) => setState(() {}),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Divider(color: Color(0xFFE2E8F0)),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Total Receivable Amount',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        Text(
                          '₹ $_totalAmount',
                          style: const TextStyle(
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

              const SizedBox(height: 18),

              // Upload After Photos Card
              _buildCardSection(
                title: 'Upload After Work Photos',
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
                      child: const Icon(Icons.check_circle_rounded,
                          color: Color(0xFF10B981), size: 32),
                    ),
                    const SizedBox(width: 12),
                    GestureDetector(
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Photo attached successfully!'),
                            backgroundColor: Color(0xFF10B981),
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
                        child: const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.add_a_photo_outlined,
                                color: Color(0xFF2563EB), size: 22),
                            SizedBox(height: 4),
                            Text('Add Photo',
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

              const SizedBox(height: 18),

              // Customer Signature Placeholder Card
              _buildCardSection(
                title: 'Customer Sign-off Signature',
                child: Container(
                  height: 100,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFCBD5E1)),
                  ),
                  child: const Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.draw_rounded,
                            color: Color(0xFF94A3B8), size: 22),
                        SizedBox(width: 8),
                        Text(
                          'Customer Signature Verified (Sunil V.)',
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

              const SizedBox(height: 18),

              // Completion Notes
              _buildCardSection(
                title: 'Completion Report Remarks',
                child: TextField(
                  controller: _completionNotesController,
                  maxLines: 2,
                  decoration: InputDecoration(
                    hintText: 'Final remarks on work done...',
                    hintStyle:
                        const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                    filled: true,
                    fillColor: const Color(0xFFF8FAFC),
                    contentPadding: const EdgeInsets.all(12),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide:
                          const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 32),

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
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.task_alt_rounded, size: 24),
                      SizedBox(width: 8),
                      Text(
                        'Submit Final Invoice & Finish',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),
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
      padding: const EdgeInsets.all(18),
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
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 14),
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
            const SizedBox(height: 12),
            Container(
              width: 80,
              height: 80,
              decoration: const BoxDecoration(
                color: Color(0xFFD1FAE5),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.stars_rounded,
                size: 52,
                color: Color(0xFF10B981),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              '₹ 1,200 Earned!',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w900,
                color: Color(0xFF10B981),
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Payment credited to KaamSetu Wallet.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: Color(0xFF64748B),
              ),
            ),
            const SizedBox(height: 24),
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
                child: const Text(
                  'Back to Partner Dashboard',
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
