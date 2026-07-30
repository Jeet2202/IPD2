// File:
// lib/customer/legal/privacy_policy/privacy_policy_screen.dart

import 'package:flutter/material.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  final List<Map<String, String>> _privacySections = const [
    {
      'title': '1. Information We Collect',
      'body': 'We collect profile details (name, email, verified phone number), GPS location data to assign nearby technicians, diagnostic photos/videos uploaded for inspection, and payment transaction tokens.',
    },
    {
      'title': '2. How We Use Your Data',
      'body': 'Your data is strictly utilized to match you with nearby service professionals, process secure digital payments, dispatch emergency safety assistance, and provide service updates via WhatsApp/SMS.',
    },
    {
      'title': '3. Data Security & Storage',
      'body': 'All user data is encrypted in transit and at rest using bank-grade AES-256 bit encryption standards. We never sell your personal contact information to third-party telemarketers.',
    },
    {
      'title': '4. Data Retention & Deletion Rights',
      'body': 'You retain total control over your personal data. You may request complete account data deletion or download your activity history directly from the Privacy & Security settings screen at any time.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Privacy Policy',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.shield_outlined, color: Color(0xFF16A34A)),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Your Privacy is Protected', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF14532D))),
                          SizedBox(height: 2),
                          Text('Last Updated: July 15, 2026 • Encrypted Architecture', style: TextStyle(fontSize: 11, color: Color(0xFF15803D))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Column(
                children: _privacySections.map((sec) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: ExpansionTile(
                      title: Text(sec['title']!, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                      children: [
                        Text(sec['body']!, style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.5)),
                      ],
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.download_rounded, size: 18),
                  label: const Text('Download Policy PDF', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF2563EB)),
                    foregroundColor: const Color(0xFF2563EB),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
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
}
