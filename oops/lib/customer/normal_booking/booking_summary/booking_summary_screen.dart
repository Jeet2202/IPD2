// File:
// lib/customer/normal_booking/booking_summary/booking_summary_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class BookingSummaryScreen extends StatefulWidget {
  const BookingSummaryScreen({super.key});

  @override
  State<BookingSummaryScreen> createState() => _BookingSummaryScreenState();
}

class _BookingSummaryScreenState extends State<BookingSummaryScreen> {
  bool _agreedToTerms = true;

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
        title: const Text(
          'Booking Summary',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Service Details Summary Card ───────────────────────
                _buildSummaryCard(
                  title: 'Service Selected',
                  icon: Icons.electrical_services_rounded,
                  content: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Switchboard & Wiring Repair',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(height: 4),
                      const Text('Tasks: Wiring fix, Switch replacement', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('Certified Electrician Assigned', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Date & Time Card ──────────────────────────────────
                _buildSummaryCard(
                  title: 'Date & Time Slot',
                  icon: Icons.calendar_month_rounded,
                  onChangeTap: () {},
                  content: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Thursday, 31 July 2026',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      SizedBox(height: 4),
                      Text('10:30 AM - 11:30 AM Slot', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Address Card ──────────────────────────────────────
                _buildSummaryCard(
                  title: 'Service Address',
                  icon: Icons.location_on_rounded,
                  onChangeTap: () {},
                  content: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Home (Default)',
                        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Flat 402, Royal Palms Heights, Sector 6, HSR Layout, Bengaluru - 560102',
                        style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Notes & Uploads Card ──────────────────────────────
                _buildSummaryCard(
                  title: 'Instructions & Photos',
                  icon: Icons.note_alt_rounded,
                  content: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Notes: "Living room switchboard sparking when AC is turned on."',
                        style: TextStyle(fontSize: 13, color: Color(0xFF475569), fontStyle: FontStyle.italic),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Container(
                            width: 50,
                            height: 50,
                            margin: const EdgeInsets.only(right: 8),
                            decoration: BoxDecoration(
                              color: const Color(0xFFE0F2FE),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(Icons.image_rounded, color: Color(0xFF0EA5E9), size: 24),
                          ),
                          Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              color: const Color(0xFFE0F2FE),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(Icons.image_rounded, color: Color(0xFF0EA5E9), size: 24),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Final Payment Breakdown Card ──────────────────────
                _buildSummaryCard(
                  title: 'Payment Details',
                  icon: Icons.receipt_long_rounded,
                  content: Column(
                    children: [
                      _buildRow('Subtotal', '₹477'),
                      const SizedBox(height: 6),
                      _buildRow('Discount Coupon (KAAMSETU50)', '-₹100', isGreen: true),
                      const SizedBox(height: 8),
                      const Divider(color: Color(0xFFF1F5F9), height: 1),
                      const SizedBox(height: 8),
                      _buildRow('Total Estimated Pay', '₹377', isBold: true),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // ── Terms Checkbox ────────────────────────────────────
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 22,
                      height: 22,
                      child: Checkbox(
                        value: _agreedToTerms,
                        activeColor: const Color(0xFF2563EB),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5)),
                        onChanged: (val) => setState(() => _agreedToTerms = val ?? false),
                      ),
                    ),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Text(
                        'I agree to KaamSetu\'s Terms of Service and Cancellation Policy.',
                        style: TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.4),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 110),
              ],
            ),
          ),

          // ── Bottom Sticky Bar ───────────────────────────────────────
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
              child: Row(
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Total Payable', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                      SizedBox(height: 2),
                      Text(
                        '₹377',
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF2563EB)),
                      ),
                    ],
                  ),
                  const SizedBox(width: 20),
                  Expanded(
                    child: SizedBox(
                      height: 52,
                      child: ElevatedButton(
                        onPressed: _agreedToTerms
                            ? () => Navigator.pushNamed(context, AppRoutes.bookingPayment)
                            : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        ),
                        child: const Text(
                          'Confirm & Book',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard({
    required String title,
    required IconData icon,
    required Widget content,
    VoidCallback? onChangeTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Row(
                  children: [
                    Icon(icon, size: 18, color: const Color(0xFF2563EB)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
              if (onChangeTap != null) ...[
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: onChangeTap,
                  child: const Text('Change', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                ),
              ],
            ],
          ),
          const SizedBox(height: 12),
          content,
        ],
      ),
    );
  }

  Widget _buildRow(String label, String value, {bool isGreen = false, bool isBold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: isBold ? 14 : 13,
              fontWeight: isBold ? FontWeight.w800 : FontWeight.w500,
              color: isGreen ? const Color(0xFF16A34A) : const Color(0xFF475569),
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: isBold ? 16 : 13,
            fontWeight: isBold || isGreen ? FontWeight.w800 : FontWeight.w600,
            color: isBold ? const Color(0xFF2563EB) : (isGreen ? const Color(0xFF16A34A) : const Color(0xFF0F172A)),
          ),
        ),
      ],
    );
  }
}
