// File:
// lib/customer/offers/offers_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../l10n/app_translations.dart';

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
      'title': '20% Instant Cashback via Ally Pay',
      'desc': 'Pay via Ally Pay wallet & get up to ₹250 instant cashback.',
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
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('offers_coupons'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Search Coupon Input ──────────────────────────────────
              Container(
                padding: EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.confirmation_number_outlined, color: Color(0xFF2563EB)),
                    SizedBox(width: 12),
                    Expanded(
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
                          SnackBar(content: Text('promo_code_applied_successfully'.tr(context)), backgroundColor: Color(0xFF16A34A)),
                        );
                      },
                      child: Text('apply'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 20),

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
                      padding: EdgeInsets.only(right: 8.0),
                      child: ChoiceChip(
                        label: Text(cat),
                        selected: isSelected,
                        selectedColor: const Color(0xFF2563EB),                        labelStyle: TextStyle(
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

              SizedBox(height: 24),

              // ── Offer Cards ─────────────────────────────────────────
              Column(
                children: _offers.map((offer) {
                  return Container(
                    margin: EdgeInsets.only(bottom: 20),
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
                          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: (offer['color'] as Color).withOpacity(0.08),
                            borderRadius: const BorderRadius.only(topLeft: Radius.circular(24), topRight: Radius.circular(24)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(offer['tag'] as String, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: offer['color'] as Color)),
                              Text(offer['valid'] as String, style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                        Padding(
                          padding: EdgeInsets.all(18),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(offer['title'] as String, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                              SizedBox(height: 4),
                              Text(offer['desc'] as String, style: TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.3)),
                              SizedBox(height: 16),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Container(
                                    padding: EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFF1F5F9),
                                      borderRadius: BorderRadius.circular(10),
                                      border: Border.all(color: const Color(0xFFCBD5E1), style: BorderStyle.solid),
                                    ),
                                    child: Text(offer['code'] as String, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w900, letterSpacing: 1, color: Color(0xFF0F172A))),
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
                                    child: Text('apply_offer'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
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

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
