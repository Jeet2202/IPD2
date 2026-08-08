// File: lib/worker/profile/documents/documents_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class WorkerDocumentsScreen extends StatelessWidget {
  const WorkerDocumentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'document_manager'.tr(context),
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF0F172A)),
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Overall Status Banner
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFD1FAE5),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFF10B981).withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.verified_rounded,
                        color: Color(0xFF10B981), size: 24),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'mandatory_docs_verified'.tr(context),
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF065F46),
                            ),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'account_active_clear'.tr(context),
                            style: TextStyle(
                              fontSize: 12,
                              color: Color(0xFF047857),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              Text(
                'uploaded_documents'.tr(context),
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              SizedBox(height: 14),

              _buildDocumentCard(
                title: 'aadhaar_card'.tr(context),
                status: 'verified'.tr(context),
                date: '${'uploaded_on_prefix'.tr(context)}15 Jan 2026',
                icon: Icons.badge_rounded,
                isVerified: true,
              ),
              SizedBox(height: 12),
              _buildDocumentCard(
                title: 'pan_card'.tr(context),
                status: 'verified'.tr(context),
                date: '${'uploaded_on_prefix'.tr(context)}15 Jan 2026',
                icon: Icons.credit_card_rounded,
                isVerified: true,
              ),
              SizedBox(height: 12),
              _buildDocumentCard(
                title: 'police_clearance'.tr(context),
                status: 'expires_in_45_days'.tr(context),
                date: '${'uploaded_on_prefix'.tr(context)}20 Feb 2026',
                icon: Icons.security_rounded,
                isVerified: false,
                isWarning: true,
              ),
              SizedBox(height: 12),
              _buildDocumentCard(
                title: 'iti_trade_cert'.tr(context),
                status: 'verified'.tr(context),
                date: '${'uploaded_on_prefix'.tr(context)}15 Jan 2026',
                icon: Icons.workspace_premium_rounded,
                isVerified: true,
              ),

              SizedBox(height: 24),

              // Upload New Document Button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, '/worker/verification/kyc'),
                  icon: Icon(Icons.upload_file_rounded, size: 18),
                  label: Text('upload_additional_doc'.tr(context)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF2563EB),
                    side: BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),

              SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDocumentCard({
    required String title,
    required String status,
    required String date,
    required IconData icon,
    bool isVerified = false,
    bool isWarning = false,
  }) {
    final statusColor = isVerified
        ? const Color(0xFF10B981)
        : (isWarning ? const Color(0xFFF59E0B) : const Color(0xFF64748B));

    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
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
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: statusColor, size: 22),
          ),
          SizedBox(width: 14),
          Expanded(
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
                SizedBox(height: 2),
                Text(
                  date,
                  style: TextStyle(
                    fontSize: 11,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              status,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w800,
                color: statusColor,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
