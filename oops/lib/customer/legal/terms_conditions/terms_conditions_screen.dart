// File:
// lib/customer/legal/terms_conditions/terms_conditions_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class TermsConditionsScreen extends StatelessWidget {
  TermsConditionsScreen({super.key});

  final List<Map<String, String>> _terms = [
    {
      'title': '1. Acceptance of Terms & Platform Use',
      'body': 'By downloading, accessing, or using the Ally application, you agree to be bound by these legal terms. Ally acts as an intermediary platform connecting users with verified independent service professionals across India.',
    },
    {
      'title': '2. Diagnostic Inspection & Quotation Policy',
      'body': 'Customers opting for diagnostic inspections agree to pay the standard inspection fee of ₹99. If the customer accepts the repair quotation provided post-inspection, the inspection fee will be fully waived off against the final invoice.',
    },
    {
      'title': '3. Payments, Wallet Credits & Cancellations',
      'body': 'Payments can be made via UPI, cards, net banking, or Ally Wallet. Cancellations made prior to technician dispatch incur 0 cancellation penalty. Instant refunds are processed to your Ally Pay Wallet within 15 minutes.',
    },
    {
      'title': '4. 30-Day Service Warranty & Liability',
      'body': 'Services completed by verified technicians carry an official 30-day Ally warranty covering labor defects and verified spare parts replacements.',
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
        title: Text('terms_conditions'.tr(context),
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
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.gavel_rounded, color: Color(0xFF2563EB)),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('ally_legal_agreement'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF1E3A8A))),
                          SizedBox(height: 2),
                          Text('last_updated_july_15_2026_2'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF1E40AF))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              Column(
                children: _terms.map((term) {
                  return Container(
                    margin: EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: ExpansionTile(
                      title: Text(term['title']!, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      childrenPadding: EdgeInsets.fromLTRB(16, 0, 16, 16),
                      children: [
                        Text(term['body']!, style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.5)),
                      ],
                    ),
                  );
                }).toList(),
              ),

              SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: Icon(Icons.check_circle_rounded, size: 18),
                  label: Text('i_agree_accept_terms'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
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
