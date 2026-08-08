// File:
// lib/customer/about/about_screen.dart

import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('about_ally'.tr(context),
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
              // ── App Brand Header ─────────────────────────────────────
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 90,
                      height: 90,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)]),
                        borderRadius: BorderRadius.circular(28),
                        boxShadow: [
                          BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.3), blurRadius: 20, offset: const Offset(0, 8)),
                        ],
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(28),
                        child: Image.asset(
                          'assets/images/logos/ally_logo.png',
                          width: 90,
                          height: 90,
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    SizedBox(height: 14),
                    SizedBox(height: 2),
                    Text('bridging_skill_service_across_india'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B), fontWeight: FontWeight.w600)),
                    SizedBox(height: 6),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(10)),
                      child: Text('version_240_build_9021'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Mission Statement ────────────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.rocket_launch_rounded, color: Color(0xFF2563EB), size: 22),
                        SizedBox(width: 10),
                        Text('our_mission'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                      ],
                    ),
                    SizedBox(height: 8),
                    Text('ally_is_indias_premier'.tr(context),
                      style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.5),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Platform Statistics ──────────────────────────────────
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 1.3,
                children: [
                  _StatBox(val: '50,000+', title: 'Happy Customers'),
                  _StatBox(val: '10,000+', title: 'Verified Pros'),
                  _StatBox(val: '25+', title: 'Cities Served'),
                  _StatBox(val: '150,000+', title: 'Completed Jobs'),
                ],
              ),

              SizedBox(height: 28),

              // ── Rating & Sharing Buttons ─────────────────────────────
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {},
                      icon: Icon(Icons.star_rounded, size: 18),
                      label: Text('rate_on_play_store'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: Icon(Icons.share_rounded, size: 18),
                      label: Text('share_app'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                      style: OutlinedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 14),
                        side: BorderSide(color: Color(0xFFCBD5E1)),
                        foregroundColor: const Color(0xFF0F172A),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatBox extends StatelessWidget {
  final String val;
  final String title;

  const _StatBox({required this.val, required this.title});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(val, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
          SizedBox(height: 4),
          Text(title, style: TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
