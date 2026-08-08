// File:
// lib/customer/refer_earn/refer_earn_screen.dart

import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class ReferEarnScreen extends StatelessWidget {
  const ReferEarnScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('refer_earn'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            children: [
              // ── Hero Banner ──────────────────────────────────────────
              Container(
                padding: EdgeInsets.all(22),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.28), blurRadius: 16, offset: const Offset(0, 6)),
                  ],
                ),
                child: Column(
                  children: [
                    Icon(Icons.card_giftcard_rounded, color: Colors.white, size: 48),
                    SizedBox(height: 12),
                    Text('earn_200_for_every_friend'.tr(context),
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Colors.white),
                    ),
                    SizedBox(height: 6),
                    Text('share_your_code_with_friends'.tr(context),
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 12, color: Color(0xFFE0F2FE), height: 1.4),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Referral Code Box ────────────────────────────────────
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('your_referral_code'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
                        SizedBox(height: 4),
                        Text('kaamrahul99'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF0F172A), letterSpacing: 1)),
                      ],
                    ),
                    ElevatedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Referral code "KAAM-RAHUL99" copied to clipboard!'),
                            backgroundColor: Color(0xFF2563EB),
                          ),
                        );
                      },
                      icon: Icon(Icons.copy_rounded, size: 16),
                      label: Text('copy_code'.tr(context)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFEFF6FF),
                        foregroundColor: const Color(0xFF2563EB),
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Earnings Summary ──────────────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _RefStat(title: 'Total Earned', val: '₹600'),
                    _RefStat(title: 'Successful Refers', val: '3 Friends'),
                    _RefStat(title: 'Pending', val: '1 Friend'),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── How It Works ─────────────────────────────────────────
              Align(
                alignment: Alignment.centerLeft,
                child: Text('how_it_works'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              ),
              SizedBox(height: 14),

              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _StepRow(num: '1', title: 'Invite Your Friends', desc: 'Share your code or direct invite link.'),
                    SizedBox(height: 16),
                    _StepRow(num: '2', title: 'Friend Books a Service', desc: 'They get ₹100 instant discount on 1st booking.'),
                    SizedBox(height: 16),
                    _StepRow(num: '3', title: 'Get ₹200 Wallet Cash', desc: 'Credited directly to your wallet after completion.'),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Share Button ────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('sharing_ally_invite_link'.tr(context)),
                        backgroundColor: Color(0xFF16A34A),
                      ),
                    );
                  },
                  icon: Icon(Icons.share_rounded, size: 20),
                  label: Text('invite_friends_now'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF16A34A),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _RefStat extends StatelessWidget {
  final String title;
  final String val;

  const _RefStat({required this.title, required this.val});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(val, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
        SizedBox(height: 2),
        Text(title, style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
      ],
    );
  }
}

class _StepRow extends StatelessWidget {
  final String num;
  final String title;
  final String desc;

  const _StepRow({required this.num, required this.title, required this.desc});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: const Color(0xFFDBEAFE),
          child: Text(num, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
        ),
        SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              SizedBox(height: 2),
              Text(desc, style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
            ],
          ),
        ),
      ],
    );
  }
}
