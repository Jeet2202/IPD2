// File:
// lib/customer/settings/privacy_security/privacy_security_screen.dart

import 'package:flutter/material.dart';

class PrivacySecurityScreen extends StatefulWidget {
  const PrivacySecurityScreen({super.key});

  @override
  State<PrivacySecurityScreen> createState() => _PrivacySecurityScreenState();
}

class _PrivacySecurityScreenState extends State<PrivacySecurityScreen> {
  bool _biometricEnabled = true;
  bool _twoFactorEnabled = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Privacy & Security',
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
              // ── Security Health Score ─────────────────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(color: Color(0xFF16A34A), shape: BoxShape.circle),
                      child: const Icon(Icons.shield_rounded, color: Colors.white, size: 24),
                    ),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Security Health: 95%', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF14532D))),
                          SizedBox(height: 2),
                          Text('Your account is highly secure with 2FA enabled.', style: TextStyle(fontSize: 12, color: Color(0xFF15803D))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Security Toggles ─────────────────────────────────────
              const Text('ACCOUNT PROTECTION', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.fingerprint_rounded, color: Color(0xFF2563EB), size: 22),
                      title: const Text('Biometric Login', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      subtitle: const Text('Unlock app using Face ID or Fingerprint', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                      trailing: Switch(
                        value: _biometricEnabled,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _biometricEnabled = val),
                      ),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    ListTile(
                      leading: const Icon(Icons.phonelink_lock_rounded, color: Color(0xFF2563EB), size: 22),
                      title: const Text('Two-Factor Authentication (2FA)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      subtitle: const Text('OTP required for login on new devices', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                      trailing: Switch(
                        value: _twoFactorEnabled,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _twoFactorEnabled = val),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Active Sessions ──────────────────────────────────────
              const Text('ACTIVE LOGGED-IN DEVICES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.phone_iphone_rounded, color: Color(0xFF2563EB), size: 28),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('iPhone 15 Pro (This Device)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('Bengaluru, India • Active Now', style: TextStyle(fontSize: 11, color: Color(0xFF16A34A), fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ),
                    TextButton(
                      onPressed: () {},
                      child: const Text('Revoke', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Data & Privacy Control ───────────────────────────────
              const Text('DATA & PRIVACY CONTROL', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.download_rounded, color: Color(0xFF2563EB), size: 22),
                      title: const Text('Download My Data', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      subtitle: const Text('Request a copy of your personal data archive', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                      onTap: () {},
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    ListTile(
                      leading: const Icon(Icons.cleaning_services_rounded, color: Color(0xFF2563EB), size: 22),
                      title: const Text('Clear Search & Browsing History', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      onTap: () {},
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // ── Delete Account Section ───────────────────────────────
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFFCA5A5)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.delete_forever_rounded, color: Color(0xFFEF4444), size: 28),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Delete Account Permanently', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF991B1B))),
                          SizedBox(height: 2),
                          Text('Irreversibly delete your profile, booking history & wallet.', style: TextStyle(fontSize: 11, color: Color(0xFF7F1D1D))),
                        ],
                      ),
                    ),
                    TextButton(
                      onPressed: () {},
                      child: const Text('Delete', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Color(0xFFEF4444))),
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
}
