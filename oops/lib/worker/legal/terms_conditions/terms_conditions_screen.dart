// File: lib/worker/legal/terms_conditions/terms_conditions_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class WorkerTermsConditionsScreen extends StatelessWidget {
  const WorkerTermsConditionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'worker_terms_conditions'.tr(context),
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
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                            color: const Color(0xFF2563EB).withOpacity(0.2)),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.gavel_rounded,
                              color: Color(0xFF2563EB), size: 20),
                          SizedBox(width: 10),
                          Text(
                            'last_updated_terms'.tr(context),
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ],
                      ),
                    ),

                    SizedBox(height: 24),

                    _buildLegalSection(
                      title: 'term1_title'.tr(context),
                      content: 'term1_content'.tr(context),
                    ),
                    _buildLegalSection(
                      title: 'term2_title'.tr(context),
                      content: 'term2_content'.tr(context),
                    ),
                    _buildLegalSection(
                      title: 'term3_title'.tr(context),
                      content: 'term3_content'.tr(context),
                    ),
                    _buildLegalSection(
                      title: 'term4_title'.tr(context),
                      content: 'term4_content'.tr(context),
                    ),
                    _buildLegalSection(
                      title: 'term5_title'.tr(context),
                      content: 'term5_content'.tr(context),
                    ),

                    SizedBox(height: 24),
                  ],
                ),
              ),
            ),

            // Accept & Download Buttons Bar
            Container(
              padding: EdgeInsets.fromLTRB(24, 14, 24, 24),
              decoration: BoxDecoration(
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
                          SnackBar(
                            content: Text('downloading_terms_pdf'.tr(context)),
                            backgroundColor: const Color(0xFF2563EB),
                          ),
                        );
                      },
                      icon: Icon(Icons.download_rounded, size: 16),
                      label: Text('download_pdf'.tr(context)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF2563EB),
                        side: BorderSide(color: Color(0xFF2563EB)),
                        padding: EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: Text(
                        'i_accept_terms'.tr(context),
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
      margin: EdgeInsets.only(bottom: 16),
      padding: EdgeInsets.all(16),
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
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
          SizedBox(height: 8),
          Text(
            content,
            style: TextStyle(
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
