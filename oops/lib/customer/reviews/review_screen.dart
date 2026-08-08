// File:
// lib/customer/reviews/review_screen.dart

import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class ReviewScreen extends StatefulWidget {
  const ReviewScreen({super.key});

  @override
  State<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends State<ReviewScreen> {
  int _selectedRating = 5;
  bool _wouldRecommend = true;
  final TextEditingController _commentController = TextEditingController();

  final List<String> _feedbackChips = [
    'Professional',
    'On Time',
    'Clean Work',
    'Highly Skilled',
    'Affordable',
    'Friendly Behavior',
  ];

  final Set<String> _selectedChips = {'Professional', 'On Time', 'Clean Work'};

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('rate_review'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // ── Worker Header Card ──────────────────────────────────
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
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                      child: Icon(Icons.person_rounded, size: 36, color: Color(0xFF2563EB)),
                    ),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('ramesh_kumar'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('senior_electrician_switchboard_repair'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Interactive Star Rating Bar ──────────────────────────
              Text('how_was_your_overall_experience'.tr(context),
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
              SizedBox(height: 14),

              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(5, (index) {
                  final starValue = index + 1;
                  return GestureDetector(
                    onTap: () => setState(() => _selectedRating = starValue),
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 6.0),
                      child: Icon(
                        Icons.star_rounded,
                        size: 42,
                        color: starValue <= _selectedRating ? const Color(0xFFFBBF24) : const Color(0xFFE2E8F0),
                      ),
                    ),
                  );
                }),
              ),

              SizedBox(height: 8),
              Text(
                _getRatingLabel(_selectedRating),
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
              ),

              SizedBox(height: 28),

              // ── Quick Feedback Chips ──────────────────────────────────
              Align(
                alignment: Alignment.centerLeft,
                child: Text('what_did_you_like_the'.tr(context),
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
              ),
              SizedBox(height: 12),

              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: _feedbackChips.map((chip) {
                  final isSelected = _selectedChips.contains(chip);
                  return FilterChip(
                    label: Text(chip),
                    selected: isSelected,
                    labelStyle: TextStyle(
                      fontSize: 12,
                      fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                      color: isSelected ? Colors.white : const Color(0xFF334155),
                    ),                    selectedColor: const Color(0xFF2563EB),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                      side: BorderSide(color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFCBD5E1)),
                    ),
                    onSelected: (selected) {
                      setState(() {
                        if (selected) {
                          _selectedChips.add(chip);
                        } else {
                          _selectedChips.remove(chip);
                        }
                      });
                    },
                  );
                }).toList(),
              ),

              SizedBox(height: 28),

              // ── Review Text Field ────────────────────────────────────
              Align(
                alignment: Alignment.centerLeft,
                child: Text('write_your_detailed_review'.tr(context),
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                ),
              ),
              SizedBox(height: 8),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFFCBD5E1)),
                ),
                child: TextField(
                  controller: _commentController,
                  maxLines: 4,
                  style: TextStyle(fontSize: 14, color: Color(0xFF0F172A)),
                  decoration: const InputDecoration(
                    hintText: 'Share feedback about Ramesh\'s work quality, behavior...',
                    hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.all(14),
                  ),
                ),
              ),

              SizedBox(height: 24),

              // ── Would Recommend Toggle ───────────────────────────────
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('would_you_recommend_ally'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                    Row(
                      children: [
                        ChoiceChip(
                          label: Text('yes'.tr(context)),
                          selected: _wouldRecommend,
                          selectedColor: const Color(0xFFDCFCE7),
                          labelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: _wouldRecommend ? const Color(0xFF16A34A) : const Color(0xFF64748B)),
                          onSelected: (_) => setState(() => _wouldRecommend = true),
                        ),
                        SizedBox(width: 8),
                        ChoiceChip(
                          label: Text('no'.tr(context)),
                          selected: !_wouldRecommend,
                          selectedColor: const Color(0xFFFEF2F2),
                          labelStyle: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: !_wouldRecommend ? const Color(0xFFEF4444) : const Color(0xFF64748B)),
                          onSelected: (_) => setState(() => _wouldRecommend = false),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 32),

              // ── Action Buttons ────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('submit_review'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                ),
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  String _getRatingLabel(int rating) {
    switch (rating) {
      case 5:
        return 'Excellent! 🌟🌟🌟🌟🌟';
      case 4:
        return 'Very Good! 👍';
      case 3:
        return 'Average 😐';
      case 2:
        return 'Poor 👎';
      default:
        return 'Very Bad 😡';
    }
  }
}
