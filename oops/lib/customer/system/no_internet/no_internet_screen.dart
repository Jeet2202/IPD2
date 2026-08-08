// File:
// lib/customer/system/no_internet/no_internet_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class NoInternetScreen extends StatelessWidget {
  const NoInternetScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Spacer(),

              // ── Offline Illustration Placeholder ────────────────────
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: Color(0xFFEFF6FF),
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.wifi_off_rounded, color: Color(0xFF2563EB), size: 56),
              ),

              SizedBox(height: 28),

              Text('no_internet_connection'.tr(context),
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
              ),

              SizedBox(height: 8),

              Text('we_couldn'.tr(context)t connect to Ally servers. Please check your cellular data or Wi-Fi network and try again.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
              ),

              SizedBox(height: 32),

              // ── Troubleshooting Checklist Card ───────────────────────
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _TipItem(text: 'Check if Wi-Fi or Mobile Data is turned on'),
                    SizedBox(height: 8),
                    _TipItem(text: 'Ensure Airplane mode is disabled'),
                    SizedBox(height: 8),
                    _TipItem(text: 'Try restarting the Ally app'),
                  ],
                ),
              ),

              Spacer(),

              // ── Action Buttons ──────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: () {},
                  icon: Icon(Icons.refresh_rounded, size: 20),
                  label: Text('retry_connection'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ),

              SizedBox(height: 12),

              SizedBox(
                width: double.infinity,
                height: 50,
                child: TextButton(
                  onPressed: () {},
                  child: Text('open_network_settings'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF64748B))),
                ),
              ),

              SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }
}

class _TipItem extends StatelessWidget {
  final String text;

  const _TipItem({required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(Icons.check_circle_outline_rounded, color: Color(0xFF16A34A), size: 18),
        SizedBox(width: 10),
        Expanded(
          child: Text(text, style: TextStyle(fontSize: 12, color: Color(0xFF475569), fontWeight: FontWeight.w500)),
        ),
      ],
    );
  }
}
