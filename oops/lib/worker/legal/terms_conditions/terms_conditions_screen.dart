// File: lib/worker/legal/terms_conditions/terms_conditions_screen.dart

import 'package:flutter/material.dart';

class WorkerTermsConditionsScreen extends StatelessWidget {
  const WorkerTermsConditionsScreen({super.key});

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
          'Worker Terms & Conditions',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                            color: const Color(0xFF2563EB).withOpacity(0.2)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.gavel_rounded,
                              color: Color(0xFF2563EB), size: 20),
                          SizedBox(width: 10),
                          Text(
                            'Last Updated: July 1, 2026 • Version 1.4',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 24),

                    _buildLegalSection(
                      title: '1. Partner Registration & KYC Verification',
                      content:
                          'All service partners must upload valid government identity proof (Aadhaar Card & PAN Card) along with trade skill certifications. Account activation is contingent on background verification.',
                    ),
                    _buildLegalSection(
                      title: '2. Inspection & Quotation Standards',
                      content:
                          'When accepting pre-repair inspection jobs, partners must conduct honest diagnostics, generate itemized quotations using the KaamSetu app, and strictly honor approved estimates.',
                    ),
                    _buildLegalSection(
                      title: '3. Payments & Weekly Escrow Settlements',
                      content:
                          'Payments for completed jobs are credited to KaamSetu wallet upon customer sign-off. Weekly payouts are processed every Monday directly to registered bank accounts.',
                    ),
                    _buildLegalSection(
                      title: '4. Code of Conduct & Customer Safety',
                      content:
                          'Partners must maintain professional decorum, arrive punctually at customer premises, wear proper safety gear, and adhere to KaamSetu safety protocols.',
                    ),
                    _buildLegalSection(
                      title: '5. Cancellation & Deactivation Policy',
                      content:
                          'Repeated job cancellations after acceptance (>5% cancellation rate) or customer safety violations will result in temporary suspension or permanent account deactivation.',
                    ),

                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),

            // Accept & Download Buttons Bar
            Container(
              padding: const EdgeInsets.fromLTRB(24, 14, 24, 24),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(
                  top: BorderSide(color: Color(0xFFF1F5F9), width: 1.5),
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Downloading Terms PDF...'),
                            backgroundColor: Color(0xFF2563EB),
                          ),
                        );
                      },
                      icon: const Icon(Icons.download_rounded, size: 16),
                      label: const Text('Download PDF'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF2563EB),
                        side: const BorderSide(color: Color(0xFF2563EB)),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: const Text(
                        'I Accept Terms',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLegalSection({required String title, required String content}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE2E8F0)),
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
          const SizedBox(height: 8),
          Text(
            content,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xFF475569),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}
