// File:
// lib/customer/normal_booking/price_estimation/price_estimation_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../services/ai_service.dart';

class PriceEstimationScreen extends StatefulWidget {
  const PriceEstimationScreen({super.key});

  @override
  State<PriceEstimationScreen> createState() => _PriceEstimationScreenState();
}

class _PriceEstimationScreenState extends State<PriceEstimationScreen> {
  final TextEditingController _promoController = TextEditingController(text: 'ALLY50');
  bool _isCouponApplied = true;

  // AI Smart Pricing
  Map<String, dynamic>? _aiEstimate;
  bool _isLoadingAI = false;

  @override
  void initState() {
    super.initState();
    _fetchAIEstimate();
  }

  Future<void> _fetchAIEstimate() async {
    setState(() => _isLoadingAI = true);
    try {
      final res = await AIService.instance.getPriceEstimate(
        bookingId: 'current_booking',
        city: 'Mumbai',
      );
      if (mounted) setState(() { _aiEstimate = res; _isLoadingAI = false; });
    } catch (_) {
      if (mounted) setState(() => _isLoadingAI = false);
    }
  }

  @override
  void dispose() {
    _promoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const double baseService = 349.0;
    const double inspectionFee = 99.0;
    const double platformFee = 29.0;
    const double taxes = 47.0;
    final double discount = _isCouponApplied ? 100.0 : 0.0;
    final double totalEstimated = (baseService + inspectionFee + platformFee + taxes) - discount;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Column(
          children: [
            Text(
              'Step 4 of 4',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
            ),
            Text(
              'Price Estimation',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── AI Smart Price Card ───────────────────────────────
                if (_isLoadingAI)
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF5F3FF),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFDDD6FE)),
                    ),
                    child: const Row(
                      children: [
                        SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF7C3AED))),
                        SizedBox(width: 10),
                        Text('Getting AI Price Recommendation...', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF7C3AED))),
                      ],
                    ),
                  )
                else if (_aiEstimate != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF7C3AED), Color(0xFF6D28D9)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(color: const Color(0xFF7C3AED).withOpacity(0.25), blurRadius: 12, offset: const Offset(0, 4)),
                      ],
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.auto_awesome_rounded, color: Colors.white, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('AI Smart Price', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFFEDE9FE))),
                              const SizedBox(height: 2),
                              Text(
                                '₹${(_aiEstimate!['estimated_price'] as num?)?.toStringAsFixed(0) ?? 'N/A'} — ₹${(_aiEstimate!['price_range_max'] as num?)?.toStringAsFixed(0) ?? 'N/A'}',
                                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Colors.white),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(8)),
                          child: Text(
                            '${(_aiEstimate!['confidence_score'] as num? ?? 0.0) * 100 >= 1 ? ((_aiEstimate!['confidence_score'] as num) * 100).toStringAsFixed(0) : '85'}% Conf.',
                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                        ),
                      ],
                    ),
                  ),

                // ── Estimated Total Price Banner Card ─────────────────

                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1E40AF), Color(0xFF2563EB)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF2563EB).withOpacity(0.28),
                        blurRadius: 16,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Estimated Total',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFFDBEAFE)),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '₹${totalEstimated.toStringAsFixed(0)}',
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900, color: Colors.white),
                          ),
                          const SizedBox(height: 4),
                          const Text(
                            'Pay after service completion',
                            style: TextStyle(fontSize: 11, color: Color(0xFF93C5FD)),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.account_balance_wallet_rounded, color: Colors.white, size: 36),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ── Coupon / Promo Code Box ────────────────────────────
                const Text(
                  'Discount Coupon / Promo Code',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.local_offer_rounded, color: Color(0xFF2563EB), size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextField(
                          controller: _promoController,
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                          decoration: const InputDecoration(
                            hintText: 'Enter Coupon Code',
                            hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                            border: InputBorder.none,
                          ),
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () {
                          setState(() => _isCouponApplied = !_isCouponApplied);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _isCouponApplied ? const Color(0xFFEF4444) : const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: Text(
                          _isCouponApplied ? 'Remove' : 'Apply',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                ),

                if (_isCouponApplied) ...[
                  const SizedBox(height: 8),
                  const Padding(
                    padding: EdgeInsets.only(left: 4.0),
                    child: Text(
                      '🎉 ALLY50 applied: Saved ₹100!',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF16A34A)),
                    ),
                  ),
                ],

                const SizedBox(height: 28),

                // ── Detailed Price Breakdown ──────────────────────────
                const Text(
                  'Price Breakdown',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 14),

                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      _buildPriceRow('Service Base Charge', '₹$baseService'),
                      const SizedBox(height: 12),
                      _buildPriceRow('Inspection & Diagnosis Fee', '₹$inspectionFee'),
                      const SizedBox(height: 12),
                      _buildPriceRow('Platform & Safety Fee', '₹$platformFee'),
                      const SizedBox(height: 12),
                      _buildPriceRow('Taxes & GST (18%)', '₹$taxes'),
                      if (_isCouponApplied) ...[
                        const SizedBox(height: 12),
                        _buildPriceRow('Promo Discount (ALLY50)', '-₹$discount', isDiscount: true),
                      ],
                      const SizedBox(height: 14),
                      const Divider(color: Color(0xFFF1F5F9), height: 1),
                      const SizedBox(height: 14),
                      _buildPriceRow('Total Estimated Payable', '₹${totalEstimated.toStringAsFixed(0)}', isTotal: true),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // ── Important Notice Card ─────────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFFBEB),
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: const Color(0xFFFCD34D)),
                  ),
                  child: const Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.warning_amber_rounded, color: Color(0xFFD97706), size: 22),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Important Notice',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFFB45309)),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'Final price may vary depending on actual spare parts required during the repair. Additional work will be quoted before starting.',
                              style: TextStyle(fontSize: 12, color: Color(0xFF92400E), height: 1.4),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Bottom Button ────────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
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
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.bookingAddress),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Review Booking Summary',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                      ),
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

  Widget _buildPriceRow(String label, String price, {bool isDiscount = false, bool isTotal = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: isTotal ? 15 : 13,
            fontWeight: isTotal ? FontWeight.w800 : FontWeight.w500,
            color: isTotal ? const Color(0xFF0F172A) : (isDiscount ? const Color(0xFF16A34A) : const Color(0xFF475569)),
          ),
        ),
        Text(
          price,
          style: TextStyle(
            fontSize: isTotal ? 18 : 14,
            fontWeight: isTotal || isDiscount ? FontWeight.w800 : FontWeight.w700,
            color: isTotal
                ? const Color(0xFF2563EB)
                : (isDiscount ? const Color(0xFF16A34A) : const Color(0xFF0F172A)),
          ),
        ),
      ],
    );
  }
}
