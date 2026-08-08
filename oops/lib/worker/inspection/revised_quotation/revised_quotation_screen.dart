// File: lib/worker/inspection/revised_quotation/revised_quotation_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';
import '../../../../widgets/language_selector_widget.dart';

class WorkerRevisedQuotationScreen extends StatefulWidget {
  const WorkerRevisedQuotationScreen({super.key});

  @override
  State<WorkerRevisedQuotationScreen> createState() =>
      _WorkerRevisedQuotationScreenState();
}

class _WorkerRevisedQuotationScreenState
    extends State<WorkerRevisedQuotationScreen> {
  final _materialCostController = TextEditingController(text: '450');
  final _labourCostController = TextEditingController(text: '700'); // Reduced by 100
  final _travelCostController = TextEditingController(text: '50');
  final _discountController = TextEditingController(text: '50');
  final _reasonController = TextEditingController(
      text: 'Negotiated goodwill discount of ₹100 on labour charges per customer request.');

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
    return (_subtotal - _discount) * 0.18;
  }

  double get _revisedTotal {
    return (_subtotal - _discount) + _gstTax;
  }

  @override
  void dispose() {
    _materialCostController.dispose();
    _labourCostController.dispose();
    _travelCostController.dispose();
    _discountController.dispose();
    _reasonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'revised_quotation_editor'.tr(context),
          style: const TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Before vs After Price Comparison Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('original_quote_label2'.tr(context),
                          style: const TextStyle(
                              fontSize: 11, color: Color(0xFF64748B))),
                      const SizedBox(height: 4),
                      const Text(
                        '₹ 1,298',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF94A3B8),
                          decoration: TextDecoration.lineThrough,
                        ),
                      ),
                    ],
                  ),
                    const Icon(Icons.arrow_forward_rounded,
                        color: Color(0xFF2563EB), size: 24),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('revised_quote_label'.tr(context),
                            style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF2563EB))),
                        const SizedBox(height: 4),
                        Text(
                          '₹ ${_revisedTotal.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF10B981),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Text(
                'adjust_line_items'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 14),

              _buildCostInputRow(
                label: 'spare_parts_materials'.tr(context),
                controller: _materialCostController,
              ),
              const SizedBox(height: 12),
              _buildCostInputRow(
                label: 'labour_repair_charges'.tr(context),
                controller: _labourCostController,
              ),
              const SizedBox(height: 12),
              _buildCostInputRow(
                label: 'travel_convenience_fee'.tr(context),
                controller: _travelCostController,
              ),
              const SizedBox(height: 12),
              _buildCostInputRow(
                label: 'special_discount_coupon'.tr(context),
                controller: _discountController,
                isDiscount: true,
              ),

              const SizedBox(height: 20),

              // Reason for Revision Field
              Text(
                'reason_for_revision'.tr(context),
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF334155),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _reasonController,
                maxLines: 2,
                decoration: InputDecoration(
                  hintText: 'enter_reason_price_update'.tr(context),
                  hintStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding: const EdgeInsets.all(14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // Submit Revised Quotation Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                        context, '/worker/inspection/repair-confirmation');
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
                      const Icon(Icons.send_rounded, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'submit_revised_quotation'.tr(context),
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 20),
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
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF2563EB)),
              ),
            ),
            onChanged: (_) => setState(() {}),
          ),
        ),
      ],
    );
  }
}
