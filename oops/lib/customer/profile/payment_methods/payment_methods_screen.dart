// File:
// lib/customer/profile/payment_methods/payment_methods_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class PaymentMethodsScreen extends StatefulWidget {
  const PaymentMethodsScreen({super.key});

  @override
  State<PaymentMethodsScreen> createState() => _PaymentMethodsScreenState();
}

class _PaymentMethodsScreenState extends State<PaymentMethodsScreen> {
  String _preferredMethod = 'KaamSetu Wallet';

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
          'Payment Methods',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── KaamSetu Wallet Banner ───────────────────────────────
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
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.25), blurRadius: 16, offset: const Offset(0, 6)),
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('KAAMSETU PAY WALLET', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFFDBEAFE))),
                        SizedBox(height: 4),
                        Text('₹1,450.00', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: Colors.white)),
                        SizedBox(height: 2),
                        Text('Instant 1-Click Checkout', style: TextStyle(fontSize: 11, color: Color(0xFFE0F2FE))),
                      ],
                    ),
                    ElevatedButton(
                      onPressed: () => Navigator.pushNamed(context, AppRoutes.customerWallet),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFF2563EB),
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: const Text('+ Top Up', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // ── Saved UPI ───────────────────────────────────────────
              const Text('Saved UPI Handles', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              const SizedBox(height: 12),

              _PaymentTile(
                icon: Icons.account_balance_rounded,
                title: 'Google Pay',
                subtitle: 'rahul.sharma@okaxis',
                isSelected: _preferredMethod == 'gpay',
                onTap: () => setState(() => _preferredMethod = 'gpay'),
              ),
              const SizedBox(height: 10),
              _PaymentTile(
                icon: Icons.mobile_friendly_rounded,
                title: 'PhonePe',
                subtitle: '9876543210@ybl',
                isSelected: _preferredMethod == 'phonepe',
                onTap: () => setState(() => _preferredMethod = 'phonepe'),
              ),

              const SizedBox(height: 24),

              // ── Saved Cards ─────────────────────────────────────────
              const Text('Saved Cards', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              const SizedBox(height: 12),

              _PaymentTile(
                icon: Icons.credit_card_rounded,
                title: 'HDFC Regalia Credit Card',
                subtitle: '•••• •••• •••• 4920 • Exp 08/28',
                isSelected: _preferredMethod == 'hdfc',
                onTap: () => setState(() => _preferredMethod = 'hdfc'),
              ),

              const SizedBox(height: 24),

              // ── Add New Option ──────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Add Payment Method dialog opened. Enter UPI/Card details.')),
                    );
                  },
                  icon: const Icon(Icons.add_rounded, size: 20),
                  label: const Text('Add New Card or UPI ID', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF2563EB),
                    side: const BorderSide(color: Color(0xFF2563EB)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _PaymentTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final bool isSelected;
  final VoidCallback onTap;

  const _PaymentTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0), width: isSelected ? 2 : 1),
        ),
        child: Row(
          children: [
            Icon(icon, color: const Color(0xFF2563EB), size: 24),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                  const SizedBox(height: 2),
                  Text(subtitle, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                ],
              ),
            ),
            Icon(
              isSelected ? Icons.radio_button_checked_rounded : Icons.radio_button_off_rounded,
              color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFCBD5E1),
            ),
          ],
        ),
      ),
    );
  }
}
