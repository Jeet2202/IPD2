// File:
// lib/customer/offers/offers_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';

class OffersScreen extends StatefulWidget {
  const OffersScreen({super.key});

  @override
  State<OffersScreen> createState() => _OffersScreenState();
}

class _OffersScreenState extends State<OffersScreen> {
  String _selectedCategory = 'All Coupons';

  final List<String> _categories = ['All Coupons', 'Cashback', 'Festival Offers', 'Referral Offers'];

  final List<Map<String, dynamic>> _offers = [
    {
      'title': 'Flat ₹500 OFF on Electrical Repairs',
      'desc': 'Applicable on inspection & complete DB rewiring orders above ₹2,999.',
      'code': 'KAAM500',
      'valid': 'Valid till 15 Aug 2026',
      'tag': 'FESTIVAL SPECIAL',
      'color': const Color(0xFF2563EB),
    },
    {
      'title': '20% Instant Cashback via KaamSetu Pay',
      'desc': 'Pay via KaamSetu Pay wallet & get up to ₹250 instant cashback.',
      'code': 'WALLETSAVE',
      'valid': 'Valid till 31 Aug 2026',
      'tag': 'CASHBACK',
      'color': const Color(0xFF16A34A),
    },
    {
      'title': 'Free Diagnostic Inspection (₹99 Value)',
      'desc': 'Get 100% inspection fee waiver when you accept the repair quotation.',
      'code': 'FREEINSPECT',
      'valid': 'Valid till 10 Aug 2026',
      'tag': 'EXCLUSIVE',
      'color': const Color(0xFF0EA5E9),
    },
  ];

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
          'Offers & Coupons',
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
              // ── Search Coupon Input ──────────────────────────────────
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.confirmation_number_outlined, color: Color(0xFF2563EB)),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Enter coupon promo code...',
                          hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                          border: InputBorder.none,
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Promo code applied successfully! 🎉'), backgroundColor: Color(0xFF16A34A)),
                        );
                      },
                      child: const Text('APPLY', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ── Categories ──────────────────────────────────────────
              SizedBox(
                height: 38,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _categories.length,
                  itemBuilder: (context, index) {
                    final cat = _categories[index];
                    final isSelected = _selectedCategory == cat;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: ChoiceChip(
                        label: Text(cat),
                        selected: isSelected,
                        selectedColor: const Color(0xFF2563EB),
                        backgroundColor: Colors.white,
                        labelStyle: TextStyle(
                          fontSize: 12,
                          fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
                          color: isSelected ? Colors.white : const Color(0xFF475569),
                        ),
                        onSelected: (_) => setState(() => _selectedCategory = cat),
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 24),

              // ── Offer Cards ─────────────────────────────────────────
              Column(
                children: _offers.map((offer) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: (offer['color'] as Color).withOpacity(0.08),
                            borderRadius: const BorderRadius.only(topLeft: Radius.circular(24), topRight: Radius.circular(24)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(offer['tag'] as String, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: offer['color'] as Color)),
                              Text(offer['valid'] as String, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(18),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(offer['title'] as String, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                              const SizedBox(height: 4),
                              Text(offer['desc'] as String, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.3)),
                              const SizedBox(height: 16),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFF1F5F9),
                                      borderRadius: BorderRadius.circular(10),
                                      border: Border.all(color: const Color(0xFFCBD5E1), style: BorderStyle.solid),
                                    ),
                                    child: Text(offer['code'] as String, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w900, letterSpacing: 1, color: Color(0xFF0F172A))),
                                  ),
                                  ElevatedButton(
                                    onPressed: () {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('Promo "${offer['code']}" applied! Redirecting to booking...'), backgroundColor: const Color(0xFF2563EB)),
                                      );
                                      Navigator.pushNamed(context, AppRoutes.customerServices);
                                    },
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: const Color(0xFF2563EB),
                                      foregroundColor: Colors.white,
                                      elevation: 0,
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                    ),
                                    child: const Text('Apply Offer', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
