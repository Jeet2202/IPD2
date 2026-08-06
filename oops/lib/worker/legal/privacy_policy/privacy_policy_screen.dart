// File: lib/worker/legal/privacy_policy/privacy_policy_screen.dart

import 'package:flutter/material.dart';

class WorkerPrivacyPolicyScreen extends StatelessWidget {
  const WorkerPrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Worker Privacy Policy',
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
                          Icon(Icons.shield_outlined,
                              color: Color(0xFF2563EB), size: 20),
                          SizedBox(width: 10),
                          Text(
                            'Data Protection Compliant (DPDP Act 2023)',
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

                    _buildPolicySection(
                      title: '1. Information We Collect',
                      content:
                          'We collect partner registration details (Name, Phone, Email), identity documents for KYC (Aadhaar, PAN), bank settlement details, and background verification records.',
                    ),
                    _buildPolicySection(
                      title: '2. Real-Time Location Tracking',
                      content:
                          'Background and foreground location permissions are required while ON DUTY to dispatch nearby job requests, provide turn-by-turn navigation, and calculate travel distance allowances.',
                    ),
                    _buildPolicySection(
                      title: '3. Data Security & Storage',
                      content:
                          'All sensitive documents (Aadhaar & Bank details) are encrypted at rest using AES-256 encryption. We never share partner personal numbers directly with customers.',
                    ),
                    _buildPolicySection(
                      title: '4. Your Data Rights & Deletion',
                      content:
                          'Partners can request a copy of stored data or submit account deletion requests at any time via Partner Desk settings.',
                    ),

                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),

            // Bottom Policy Download Bar
            Container(
              padding: const EdgeInsets.fromLTRB(24, 14, 24, 24),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(
                  top: BorderSide(color: Color(0xFFF1F5F9), width: 1.5),
                ),
              ),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Downloading Privacy Policy PDF...'),
                        backgroundColor: Color(0xFF2563EB),
                      ),
                    );
                  },
                  icon: const Icon(Icons.download_rounded, size: 18),
                  label: const Text('Download Full Policy PDF'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPolicySection({required String title, required String content}) {
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
