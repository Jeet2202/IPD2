// File: lib/worker/inspection/create_quotation/create_quotation_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';
import '../../../../widgets/language_selector_widget.dart';

class WorkerCreateQuotationScreen extends StatefulWidget {
  const WorkerCreateQuotationScreen({super.key});

  @override
  State<WorkerCreateQuotationScreen> createState() =>
      _WorkerCreateQuotationScreenState();
}

class _WorkerCreateQuotationScreenState
    extends State<WorkerCreateQuotationScreen> {
  final _materialCostController = TextEditingController(text: '450');
  final _labourCostController = TextEditingController(text: '800');
  final _travelCostController = TextEditingController(text: '50');
  final _discountController = TextEditingController(text: '50');
  final _validityDaysController = TextEditingController(text: '7');
  final _customerNotesController = TextEditingController(
      text: 'Includes 90-day warranty on newly installed drain line & 30-day warranty on gas refill.');

  double get _subtotal {
    final m = double.tryParse(_materialCostController.text) ?? 0;
    final l = double.tryParse(_labourCostController.text) ?? 0;
    final t = double.tryParse(_travelCostController.text) ?? 0;
    return m + l + t;
  }

  double get _discount {
    return double.tryParse(_discountController.text) ?? 0;
  }

  double get _gstTax {
    return (_subtotal - _discount) * 0.18; // 18% GST
  }

  double get _grandTotal {
    return (_subtotal - _discount) + _gstTax;
  }

  @override
  void dispose() {
    _materialCostController.dispose();
    _labourCostController.dispose();
    _travelCostController.dispose();
    _discountController.dispose();
    _validityDaysController.dispose();
    _customerNotesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'generate_official_quotation'.tr(context),
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
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
              // Quotation Header Card
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF2563EB).withOpacity(0.25),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'estimated_quotation'.tr(context),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                            letterSpacing: 0.8,
                          ),
                        ),
                        Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'ally_verified'.tr(context),
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 14),
                    Text(
                      '₹ ${_grandTotal.toStringAsFixed(0)}',
                      style: TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: -0.8,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'total_price_gst_warranty'.tr(context),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.white.withOpacity(0.85),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // Itemized Cost Breakdown Inputs
              Text(
                'itemized_cost_breakdown'.tr(context),
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              SizedBox(height: 14),

              _buildCostInputRow(
                label: 'spare_parts_materials'.tr(context),
                controller: _materialCostController,
              ),
              SizedBox(height: 12),
              _buildCostInputRow(
                label: 'labour_repair_charges'.tr(context),
                controller: _labourCostController,
              ),
              SizedBox(height: 12),
              _buildCostInputRow(
                label: 'travel_convenience_fee'.tr(context),
                controller: _travelCostController,
              ),
              SizedBox(height: 12),
              _buildCostInputRow(
                label: 'special_discount_coupon'.tr(context),
                controller: _discountController,
                isDiscount: true,
              ),

              SizedBox(height: 20),

              // Calculation Summary Box
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('subtotal'.tr(context),
                            style: TextStyle(
                                fontSize: 13, color: Color(0xFF64748B))),
                        Text('₹ ${_subtotal.toStringAsFixed(0)}',
                            style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A))),
                      ],
                    ),
                    SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('applicable_gst_18'.tr(context),
                            style: TextStyle(
                                fontSize: 13, color: Color(0xFF64748B))),
                        Text('₹ ${_gstTax.toStringAsFixed(0)}',
                            style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A))),
                      ],
                    ),
                    SizedBox(height: 8),
                    Divider(color: Color(0xFFE2E8F0)),
                    SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('final_customer_price'.tr(context),
                            style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0F172A))),
                        Text('₹ ${_grandTotal.toStringAsFixed(0)}',
                            style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFF10B981))),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 20),

              // Market Rate Comparison Card
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
                    Icon(Icons.compare_arrows_rounded,
                        color: Color(0xFF2563EB), size: 22),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'fair_price_indicator'.tr(context),
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1E40AF),
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 20),

              // Additional Terms & Warranty Notes
              Text(
                'warranty_terms_note'.tr(context),
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF334155),
                ),
              ),
              SizedBox(height: 8),
              TextField(
                controller: _customerNotesController,
                maxLines: 2,
                decoration: InputDecoration(
                  hintText: 'add_warranty_period_hint'.tr(context),
                  hintStyle: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding: EdgeInsets.all(14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: Color(0xFF2563EB), width: 1.5),
                  ),
                ),
              ),

              SizedBox(height: 32),

              // Submit Quotation Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                        context, '/worker/inspection/submission');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.send_rounded, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'submit_quotation_customer'.tr(context),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
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

  Widget _buildCostInputRow({
    required String label,
    required TextEditingController controller,
    bool isDiscount = false,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: isDiscount
                ? const Color(0xFF10B981)
                : const Color(0xFF334155),
          ),
        ),
        SizedBox(
          width: 120,
          height: 44,
          child: TextField(
            controller: controller,
            keyboardType: TextInputType.number,
            textAlign: TextAlign.end,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: isDiscount
                  ? const Color(0xFF10B981)
                  : const Color(0xFF0F172A),
            ),
            decoration: InputDecoration(
              prefixText: isDiscount ? '- ₹ ' : '₹ ',
              prefixStyle: TextStyle(
                color: isDiscount
                    ? const Color(0xFF10B981)
                    : const Color(0xFF0F172A),
                fontWeight: FontWeight.w700,
              ),
              contentPadding:
                  EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Color(0xFFE2E8F0)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Color(0xFF2563EB)),
              ),
            ),
            onChanged: (_) => setState(() {}),
          ),
        ),
      ],
    );
  }
}
