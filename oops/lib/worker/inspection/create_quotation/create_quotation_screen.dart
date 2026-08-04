// File: lib/worker/inspection/create_quotation/create_quotation_screen.dart

import 'package:flutter/material.dart';

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
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Generate Official Quotation',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Quotation Header Card
              Container(
                padding: const EdgeInsets.all(18),
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
                        const Text(
                          'ESTIMATED QUOTATION',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                            letterSpacing: 0.8,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'Ally Verified',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    Text(
                      '₹ ${_grandTotal.toStringAsFixed(0)}',
                      style: const TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: -0.8,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Total Price Including GST & 90-Day Warranty',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.white.withOpacity(0.85),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Itemized Cost Breakdown Inputs
              const Text(
                'Itemized Cost Breakdown',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 14),

              _buildCostInputRow(
                label: 'Spare Parts & Materials',
                controller: _materialCostController,
              ),
              const SizedBox(height: 12),
              _buildCostInputRow(
                label: 'Labour & Repair Charges',
                controller: _labourCostController,
              ),
              const SizedBox(height: 12),
              _buildCostInputRow(
                label: 'Travel & Convenience Fee',
                controller: _travelCostController,
              ),
              const SizedBox(height: 12),
              _buildCostInputRow(
                label: 'Special Discount / Coupon',
                controller: _discountController,
                isDiscount: true,
              ),

              const SizedBox(height: 20),

              // Calculation Summary Box
              Container(
                padding: const EdgeInsets.all(16),
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
                        const Text('Subtotal',
                            style: TextStyle(
                                fontSize: 13, color: Color(0xFF64748B))),
                        Text('₹ ${_subtotal.toStringAsFixed(0)}',
                            style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A))),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Applicable GST (18%)',
                            style: TextStyle(
                                fontSize: 13, color: Color(0xFF64748B))),
                        Text('₹ ${_gstTax.toStringAsFixed(0)}',
                            style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A))),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Divider(color: Color(0xFFE2E8F0)),
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Final Customer Price',
                            style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0F172A))),
                        Text('₹ ${_grandTotal.toStringAsFixed(0)}',
                            style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w900,
                                color: Color(0xFF10B981))),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Market Rate Comparison Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                      color: const Color(0xFF2563EB).withOpacity(0.2)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.compare_arrows_rounded,
                        color: Color(0xFF2563EB), size: 22),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Fair Price Indicator: This estimate matches Ally benchmark for AC Water Leak Repair (₹1,100 – ₹1,400)',
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

              const SizedBox(height: 20),

              // Additional Terms & Warranty Notes
              const Text(
                'Warranty & Terms Note for Customer',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF334155),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _customerNotesController,
                maxLines: 2,
                decoration: InputDecoration(
                  hintText: 'Add warranty period or terms...',
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
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.send_rounded, size: 20),
                      SizedBox(width: 8),
                      Text(
                        'Submit Quotation to Customer',
                        style: TextStyle(
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
              prefixStyle: TextStyle(
                color: isDiscount
                    ? const Color(0xFF10B981)
                    : const Color(0xFF0F172A),
                fontWeight: FontWeight.w700,
              ),
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
