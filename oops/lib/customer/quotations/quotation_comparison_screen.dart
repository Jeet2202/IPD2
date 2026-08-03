// File: lib/customer/quotations/quotation_comparison_screen.dart

import 'package:flutter/material.dart';
import '../../models/quotation_model.dart';

class QuotationComparisonScreen extends StatelessWidget {
  final String bookingNumber;
  final List<CustomerQuotationItem> quotations;

  const QuotationComparisonScreen({
    super.key,
    required this.bookingNumber,
    required this.quotations,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quotation Comparison',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            Text(
              'Booking Ref: $bookingNumber',
              style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline_rounded, color: Color(0xFF2563EB), size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Comparing ${quotations.length} professional quotations side-by-side.',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF1E40AF)),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                physics: const BouncingScrollPhysics(),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: quotations.map((item) => _buildComparisonColumn(context, item)).toList(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildComparisonColumn(BuildContext context, CustomerQuotationItem item) {
    final q = item.quotation;
    final w = item.worker;

    return Container(
      width: 280,
      margin: const EdgeInsets.only(right: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFCBD5E1)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Worker Profile Header
          Row(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundColor: const Color(0xFF2563EB),
                backgroundImage: w.profilePhotoUrl != null ? NetworkImage(w.profilePhotoUrl!) : null,
                child: w.profilePhotoUrl == null
                    ? Text(
                        w.fullName.isNotEmpty ? w.fullName[0].toUpperCase() : 'W',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                      )
                    : null,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      w.fullName,
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Row(
                      children: [
                        const Icon(Icons.star_rounded, size: 14, color: Color(0xFFEAB308)),
                        const SizedBox(width: 4),
                        Text(
                          '${w.rating.toStringAsFixed(1)} (${w.experienceYears.toStringAsFixed(0)} yrs)',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),
          const Divider(height: 1),
          const SizedBox(height: 14),

          // Total Price Card
          Container(
            padding: const EdgeInsets.all(12),
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: [
                const Text(
                  'TOTAL AMOUNT',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white70),
                ),
                const SizedBox(height: 2),
                Text(
                  '₹${q.totalAmount.toStringAsFixed(0)}',
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF38BDF8)),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // Pricing Breakdown List
          _buildRow('Labour Cost', '₹${q.labourCost.toStringAsFixed(0)}'),
          _buildRow('Material Cost', '₹${q.materialCost.toStringAsFixed(0)}'),
          _buildRow('Inspection Charge', '₹${q.inspectionCharge.toStringAsFixed(0)}'),
          _buildRow('Additional Charges', '₹${q.additionalCharges.toStringAsFixed(0)}'),
          _buildRow('Taxes', '₹${q.taxAmount.toStringAsFixed(0)}'),
          _buildRow('Discount', '- ₹${q.discountAmount.toStringAsFixed(0)}', isDiscount: true),

          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 12),

          // Schedule & Duration
          _buildRow('Duration', q.estimatedDuration),
          _buildRow('Earliest Start', q.workStartDate ?? 'Immediate'),
          _buildRow('Valid Until', q.validityDate),

          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 12),

          // Scope of Work
          const Text(
            'Scope of Work:',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
          ),
          const SizedBox(height: 4),
          Text(
            q.workDescription ?? 'Standard service procedures',
            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3),
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildRow(String label, String value, {bool isDiscount = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: isDiscount ? const Color(0xFF059669) : const Color(0xFF0F172A),
            ),
          ),
        ],
      ),
    );
  }
}
