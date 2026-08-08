// File:
// lib/customer/legal/privacy_policy/privacy_policy_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  PrivacyPolicyScreen({super.key});

  final List<Map<String, String>> _privacySections = [
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
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('privacy_policy'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.shield_outlined, color: Color(0xFF16A34A)),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('your_privacy_is_protected'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF14532D))),
                          SizedBox(height: 2),
                          Text('last_updated_july_15_2026'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF15803D))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              Column(
                children: _privacySections.map((sec) {
                  return Container(
                    margin: EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: ExpansionTile(
                      title: Text(sec['title']!, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      childrenPadding: EdgeInsets.fromLTRB(16, 0, 16, 16),
                      children: [
                        Text(sec['body']!, style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.5)),
                      ],
                    ),
                  );
                }).toList(),
              ),

              SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: Icon(Icons.download_rounded, size: 18),
                  label: Text('download_policy_pdf'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(color: Color(0xFF2563EB)),
                    foregroundColor: const Color(0xFF2563EB),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
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
}
