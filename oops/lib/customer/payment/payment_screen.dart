// File:
// lib/customer/payment/payment_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../l10n/app_translations.dart';

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
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('payment_gateway'.tr(context),
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
                // ── Total Amount Card ─────────────────────────────────
                Container(
                  padding: EdgeInsets.all(20),
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
                          Text('amount_payable'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFFDBEAFE))),
                          SizedBox(height: 4),
                          Text(
                            '₹${finalPay.toStringAsFixed(0)}',
                            style: TextStyle(fontSize: 32, fontWeight: FontWeight.w900, color: Colors.white),
                          ),
                          SizedBox(height: 2),
                          Text('incl_of_all_taxes_gst'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF93C5FD))),
                        ],
                      ),
                      Container(
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(color: Colors.white.withOpacity(0.15), shape: BoxShape.circle),
                        child: Icon(Icons.shield_rounded, color: Colors.white, size: 36),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Ally Wallet Card ──────────────────────────────
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
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(14)),
                        child: Icon(Icons.account_balance_wallet_rounded, color: Color(0xFF2563EB), size: 22),
                      ),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('ally_wallet'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('available_balance_15000'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
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

                SizedBox(height: 28),

                // ── Payment Methods ────────────────────────────────────
                Text('select_payment_method'.tr(context),
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
                SizedBox(height: 14),

                // UPI Option
                _buildPaymentTile(
                  id: 'upi',
                  title: 'UPI (GPay / PhonePe / Paytm)',
                  subtitle: 'Instant payment via any UPI app',
                  icon: Icons.account_balance_rounded,
                  badge: 'Fastest',
                ),

                SizedBox(height: 12),

                // Cash Option
                _buildPaymentTile(
                  id: 'cash',
                  title: 'Cash / Pay After Service',
                  subtitle: 'Pay directly to Ramesh via Cash or UPI',
                  icon: Icons.payments_rounded,
                  badge: 'Recommended',
                ),

                SizedBox(height: 12),

                // Credit/Debit Card Option
                _buildPaymentTile(
                  id: 'card',
                  title: 'Credit / Debit Card',
                  subtitle: 'Visa, Mastercard, RuPay, Amex',
                  icon: Icons.credit_card_rounded,
                ),

                SizedBox(height: 12),

                // Net Banking Option
                _buildPaymentTile(
                  id: 'netbanking',
                  title: 'Net Banking',
                  subtitle: 'All major Indian banks supported',
                  icon: Icons.account_balance_outlined,
                ),

                SizedBox(height: 28),

                // ── Security Info Banner ──────────────────────────────
                Container(
                  padding: EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.lock_rounded, color: Color(0xFF64748B), size: 18),
                      SizedBox(width: 10),
                      Expanded(
                        child: Text('256bit_ssl_encrypted_100_safe'.tr(context),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Pay Button ───────────────────────────────────────
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
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.searchingWorker),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text(
                    'Pay ₹${finalPay.toStringAsFixed(0)} & Finish',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
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
        padding: EdgeInsets.all(16),
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
            SizedBox(width: 6),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      if (badge != null) ...[
                        SizedBox(width: 8),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(6)),
                          child: Text(badge, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                        ),
                      ],
                    ],
                  ),
                  SizedBox(height: 2),
                  Text(subtitle, style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
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
