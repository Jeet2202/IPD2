// File:
// lib/customer/inspection_booking/market_price_comparison/market_price_comparison_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class MarketPriceComparisonScreen extends StatelessWidget {
  const MarketPriceComparisonScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('price_audit_comparison'.tr(context),
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
                // ── AI Price Guarantee Banner ──────────────────────────
                Container(
                  padding: EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF059669), Color(0xFF10B981)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(color: const Color(0xFF059669).withOpacity(0.25), blurRadius: 16, offset: const Offset(0, 6)),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), shape: BoxShape.circle),
                        child: Icon(Icons.verified_rounded, color: Colors.white, size: 28),
                      ),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('ai_market_audit'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFFA7F3D0))),
                            SizedBox(height: 2),
                            Text('fair_standard_quotation'.tr(context), style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900, color: Colors.white)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Price Comparison Card ──────────────────────────────
                Container(
                  padding: EdgeInsets.all(22),
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
                              Text('sunil'.tr(context)s Quote', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                              SizedBox(height: 4),
                              Text('1250'.tr(context), style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text('hsr_avg_market_rate'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                              SizedBox(height: 4),
                              Text('1200_1350'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                            ],
                          ),
                        ],
                      ),

                      SizedBox(height: 20),

                      // Pricing Meter Bar
                      Stack(
                        children: [
                          Container(
                            height: 12,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(6),
                              gradient: const LinearGradient(
                                colors: [Color(0xFF10B981), Color(0xFFFBBF24), Color(0xFFEF4444)],
                              ),
                            ),
                          ),
                          Positioned(
                            left: 110,
                            top: -2,
                            child: Container(
                              width: 16,
                              height: 16,
                              decoration: BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                                border: Border.all(color: const Color(0xFF0F172A), width: 3),
                              ),
                            ),
                          ),
                        ],
                      ),

                      SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('great_value'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: Color(0xFF10B981))),
                          Text('fair_market_price_ideal'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                          Text('overpriced'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: Color(0xFFEF4444))),
                        ],
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── AI Explanation Card ────────────────────────────────
                Container(
                  padding: EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFBFDBFE)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.auto_awesome_rounded, color: Color(0xFF2563EB), size: 22),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('ai_audit_explanation'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF1E40AF))),
                            SizedBox(height: 4),
                            Text('this_quotation_is_100_compliant'.tr(context),
                              style: TextStyle(fontSize: 12, color: Color(0xFF1E3A8A), height: 1.4),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Proceed to Quote Button ─────────────────────────
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
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.quotationReview),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('review_itemized_quotation'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
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
}
