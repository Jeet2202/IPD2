// File:
// lib/customer/inspection_booking/quotation_review/quotation_review_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class QuotationReviewScreen extends StatelessWidget {
  const QuotationReviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('quotation_review'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.download_rounded, color: Color(0xFF2563EB)),
            onPressed: () {},
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Professional Header ────────────────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                        child: Icon(Icons.engineering_rounded, size: 28, color: Color(0xFF2563EB)),
                      ),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('quotation_by_sunil_verma'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('quote_ref_qt84920_30_july'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Itemized Cost Breakdown ────────────────────────────
                Text('itemized_cost_breakdown'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                SizedBox(height: 10),

                Container(
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      _buildCostRow('Labor & Repair Charges', '₹450.00'),
                      SizedBox(height: 10),
                      _buildCostRow('Havells 32A DP MCB Breaker', '₹550.00', subtitle: 'Genuine branded spare part'),
                      SizedBox(height: 10),
                      _buildCostRow('4sqmm Heavy Copper Wire (2m)', '₹100.00'),
                      SizedBox(height: 10),
                      _buildCostRow('Inspection Fee Adjustment', '-₹99.00', isDiscount: true, subtitle: '100% inspection fee credited'),
                      SizedBox(height: 10),
                      _buildCostRow('Taxes & Platform GST (18%)', '₹249.00'),

                      SizedBox(height: 16),
                      Divider(color: Color(0xFFE2E8F0), height: 1),
                      SizedBox(height: 14),

                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('final_quotation_total'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                          Text('125000'.tr(context), style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                        ],
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Warranty & Scope Card ──────────────────────────────
                Container(
                  padding: EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.shield_outlined, color: Color(0xFF2563EB), size: 20),
                          SizedBox(width: 8),
                          Text('includes_30day_warranty'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                        ],
                      ),
                      SizedBox(height: 6),
                      Text('covers_free_revisit_replacement_if'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.3)),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Decision Button ─────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.quotationDecision),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('make_decision_accept_negotiate'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCostRow(String title, String val, {bool isDiscount = false, String? subtitle}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: isDiscount ? const Color(0xFF16A34A) : const Color(0xFF0F172A))),
            Text(
              val,
              style: TextStyle(
                fontSize: 13,
                fontWeight: isDiscount ? FontWeight.w800 : FontWeight.w700,
                color: isDiscount ? const Color(0xFF16A34A) : const Color(0xFF0F172A),
              ),
            ),
          ],
        ),
        if (subtitle != null) ...[
          SizedBox(height: 2),
          Text(subtitle, style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
        ],
      ],
    );
  }
}
