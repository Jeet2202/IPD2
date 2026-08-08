// File:
// lib/customer/inspection_booking/revised_quotation/revised_quotation_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class RevisedQuotationScreen extends StatelessWidget {
  const RevisedQuotationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('revised_quotation'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Success Highlight Banner ───────────────────────────
                Container(
                  padding: EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: const Color(0xFFDCFCE7),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFF86EFAC)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.handshake_rounded, color: Color(0xFF16A34A), size: 30),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('revised_offer_ready'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF15803D))),
                            SizedBox(height: 2),
                            Text('sunil_submitted_a_discount_offer'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF14532D))),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Savings Highlight Comparison Card ─────────────────
                Container(
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('original_quote'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
                              SizedBox(height: 2),
                              Text('5200'.tr(context),
                                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF94A3B8), decoration: TextDecoration.lineThrough),
                              ),
                            ],
                          ),
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
                            child: Text('saved_350_67'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text('revised_quote'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                              SizedBox(height: 2),
                              Text('4850'.tr(context), style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Itemized Revised Breakdown ─────────────────────────
                Text('updated_breakdown'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
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
                      _CostItem(title: 'Labor & Technical Charges', val: '₹1,800.00'),
                      SizedBox(height: 10),
                      _CostItem(title: 'Branded Havells Parts (Wholesale)', val: '₹2,800.00'),
                      SizedBox(height: 10),
                      _CostItem(title: 'GST & Platform Tax', val: '₹250.00'),
                      SizedBox(height: 14),
                      Divider(color: Color(0xFFE2E8F0), height: 1),
                      SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('final_amount'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          Text('485000'.tr(context), style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                        ],
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Warranty Card ──────────────────────────────────────
                Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.shield_rounded, color: Color(0xFF2563EB), size: 22),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text('includes_full_30day_ally_service'.tr(context),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF1E40AF)),
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Accept Button ───────────────────────────────────
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
                  onPressed: () {
                    // Navigate to Repair Confirmation
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF16A34A),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('approve_start_repair_4850'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CostItem extends StatelessWidget {
  final String title;
  final String val;

  const _CostItem({required this.title, required this.val});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: TextStyle(fontSize: 13, color: Color(0xFF0F172A))),
        Text(val, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
      ],
    );
  }
}
