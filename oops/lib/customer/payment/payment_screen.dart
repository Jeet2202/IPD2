// File:
// lib/customer/payment/payment_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';

class PaymentScreen extends StatefulWidget {
  const PaymentScreen({super.key});

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  String _selectedMethod = 'upi';
  bool _useWallet = false;

  @override
  Widget build(BuildContext context) {
    const double totalPayable = 377.0;
    const double walletBalance = 150.0;
    final double finalPay = _useWallet ? (totalPayable - walletBalance) : totalPayable;

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
          'Payment Gateway',
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
                // ── Total Amount Card ─────────────────────────────────
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF1E40AF), Color(0xFF2563EB)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Amount Payable', style: TextStyle(fontSize: 12, color: Color(0xFFDBEAFE))),
                          const SizedBox(height: 4),
                          Text(
                            '₹${finalPay.toStringAsFixed(0)}',
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900, color: Colors.white),
                          ),
                          const SizedBox(height: 2),
                          const Text('Incl. of all taxes & GST', style: TextStyle(fontSize: 11, color: Color(0xFF93C5FD))),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: Colors.white.withOpacity(0.15), shape: BoxShape.circle),
                        child: const Icon(Icons.shield_rounded, color: Colors.white, size: 36),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // ── KaamSetu Wallet Card ──────────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(14)),
                        child: const Icon(Icons.account_balance_wallet_rounded, color: Color(0xFF2563EB), size: 22),
                      ),
                      const SizedBox(width: 14),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('KaamSetu Wallet', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('Available Balance: ₹150.00', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                      Switch(
                        value: _useWallet,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _useWallet = val),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                // ── Payment Methods ────────────────────────────────────
                const Text(
                  'Select Payment Method',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                const SizedBox(height: 14),

                // UPI Option
                _buildPaymentTile(
                  id: 'upi',
                  title: 'UPI (GPay / PhonePe / Paytm)',
                  subtitle: 'Instant payment via any UPI app',
                  icon: Icons.account_balance_rounded,
                  badge: 'Fastest',
                ),

                const SizedBox(height: 12),

                // Cash Option
                _buildPaymentTile(
                  id: 'cash',
                  title: 'Cash / Pay After Service',
                  subtitle: 'Pay directly to Ramesh via Cash or UPI',
                  icon: Icons.payments_rounded,
                  badge: 'Recommended',
                ),

                const SizedBox(height: 12),

                // Credit/Debit Card Option
                _buildPaymentTile(
                  id: 'card',
                  title: 'Credit / Debit Card',
                  subtitle: 'Visa, Mastercard, RuPay, Amex',
                  icon: Icons.credit_card_rounded,
                ),

                const SizedBox(height: 12),

                // Net Banking Option
                _buildPaymentTile(
                  id: 'netbanking',
                  title: 'Net Banking',
                  subtitle: 'All major Indian banks supported',
                  icon: Icons.account_balance_outlined,
                ),

                const SizedBox(height: 28),

                // ── Security Info Banner ──────────────────────────────
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.lock_rounded, color: Color(0xFF64748B), size: 18),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          '256-Bit SSL Encrypted & 100% Safe Payments',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Pay Button ───────────────────────────────────────
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
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.searchingWorker),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text(
                    'Pay ₹${finalPay.toStringAsFixed(0)} & Finish',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentTile({
    required String id,
    required String title,
    required String subtitle,
    required IconData icon,
    String? badge,
  }) {
    final isSelected = _selectedMethod == id;
    return GestureDetector(
      onTap: () => setState(() => _selectedMethod = id),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Radio<String>(
              value: id,
              groupValue: _selectedMethod,
              activeColor: const Color(0xFF2563EB),
              onChanged: (val) => setState(() => _selectedMethod = val!),
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      if (badge != null) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(6)),
                          child: Text(badge, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(subtitle, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                ],
              ),
            ),
            Icon(icon, color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF94A3B8), size: 22),
          ],
        ),
      ),
    );
  }
}
