// File:
// lib/customer/services/service_faq_screen.dart

import 'package:flutter/material.dart';

class ServiceFaqScreen extends StatefulWidget {
  const ServiceFaqScreen({super.key});

  @override
  State<ServiceFaqScreen> createState() => _ServiceFaqScreenState();
}

class _ServiceFaqScreenState extends State<ServiceFaqScreen> {
  final TextEditingController _faqSearchController = TextEditingController();
  String _selectedCategory = 'All';

  final List<String> _categories = [
    'All',
    'General',
    'Pricing & Payment',
    'Booking & Cancellation',
    'Warranty & Safety',
  ];

  final List<Map<String, String>> _faqs = [
    {
      'category': 'General',
      'question': 'How are Ally service professionals verified?',
      'answer': 'All professionals undergo background checks, government ID verification, and practical skills test before joining Ally.',
    },
    {
      'category': 'Pricing & Payment',
      'question': 'What if the final bill exceeds the estimated price?',
      'answer': 'Our professionals strictly follow standardized rate cards. Any extra spare parts required will be quoted and approved by you beforehand.',
    },
    {
      'category': 'Warranty & Safety',
      'question': 'Is there any service warranty provided?',
      'answer': 'Yes! We offer a 30-day service guarantee. If the same issue recurs within 30 days, we will fix it completely free of charge.',
    },
    {
      'category': 'Booking & Cancellation',
      'question': 'Can I reschedule or cancel my booking?',
      'answer': 'You can reschedule or cancel your booking for free up to 2 hours before the scheduled time slot.',
    },
    {
      'category': 'Pricing & Payment',
      'question': 'What payment modes are supported?',
      'answer': 'We support UPI (GPay, PhonePe, Paytm), Credit/Debit Cards, Net Banking, and Cash on Delivery.',
    },
    {
      'category': 'General',
      'question': 'What is an Inspection Booking?',
      'answer': 'If you are unsure of the exact issue, book an Inspection. A pro will visit, diagnose the problem, and provide a full estimate before starting repair.',
    },
  ];

  @override
  void dispose() {
    _faqSearchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filteredFaqs = _faqs.where((faq) {
      final matchesCat = _selectedCategory == 'All' || faq['category'] == _selectedCategory;
      final matchesQuery = faq['question']!.toLowerCase().contains(_faqSearchController.text.toLowerCase()) ||
          faq['answer']!.toLowerCase().contains(_faqSearchController.text.toLowerCase());
      return matchesCat && matchesQuery;
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Frequently Asked Questions',
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
              // ── FAQ Search Bar ──────────────────────────────────────────
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4)),
                  ],
                ),
                child: TextField(
                  controller: _faqSearchController,
                  onChanged: (_) => setState(() {}),
                  style: const TextStyle(fontSize: 14, color: Color(0xFF0F172A)),
                  decoration: const InputDecoration(
                    hintText: 'Search questions or keywords...',
                    hintStyle: TextStyle(fontSize: 14, color: Color(0xFF94A3B8)),
                    prefixIcon: Icon(Icons.search_rounded, color: Color(0xFF2563EB), size: 20),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // ── Category Filter Chips ────────────────────────────────
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                physics: const BouncingScrollPhysics(),
                child: Row(
                  children: _categories.map((cat) {
                    final isSelected = cat == _selectedCategory;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: FilterChip(
                        label: Text(cat),
                        selected: isSelected,
                        labelStyle: TextStyle(
                          fontSize: 13,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                          color: isSelected ? Colors.white : const Color(0xFF475569),
                        ),                        selectedColor: const Color(0xFF2563EB),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                          side: BorderSide(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0)),
                        ),
                        onSelected: (_) => setState(() => _selectedCategory = cat),
                      ),
                    );
                  }).toList(),
                ),
              ),

              const SizedBox(height: 24),

              // ── Expandable FAQ Cards List ────────────────────────────
              if (filteredFaqs.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32.0),
                    child: Text(
                      'No matching questions found.',
                      style: TextStyle(fontSize: 14, color: Color(0xFF64748B)),
                    ),
                  ),
                )
              else
                ...filteredFaqs.map((faq) => _buildFaqCard(faq)),

              const SizedBox(height: 28),

              // ── Still Need Help Card ─────────────────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFEFF6FF), Color(0xFFDBEAFE)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.headset_mic_rounded, size: 42, color: Color(0xFF2563EB)),
                    const SizedBox(height: 12),
                    const Text(
                      'Still Have Questions?',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Our customer support team is available 24/7 to assist you.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 13, color: Color(0xFF475569), height: 1.4),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.chat_bubble_outline_rounded, size: 18),
                        label: const Text('Contact Support', style: TextStyle(fontWeight: FontWeight.w700)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFaqCard(Map<String, String> faq) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 8, offset: const Offset(0, 3)),
        ],
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          iconColor: const Color(0xFF2563EB),
          collapsedIconColor: const Color(0xFF64748B),
          tilePadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
          title: Text(
            faq['question']!,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
          ),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(18, 0, 18, 18),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  faq['answer']!,
                  style: const TextStyle(fontSize: 14, color: Color(0xFF475569), height: 1.5),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
