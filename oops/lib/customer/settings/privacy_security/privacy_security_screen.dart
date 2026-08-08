// File:
// lib/customer/settings/privacy_security/privacy_security_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

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
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('privacy_security'.tr(context),
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
              // ── Security Health Score ─────────────────────────────────
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(10),
                      decoration: BoxDecoration(color: Color(0xFF16A34A), shape: BoxShape.circle),
                      child: Icon(Icons.shield_rounded, color: Colors.white, size: 24),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('security_health_95'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF14532D))),
                          SizedBox(height: 2),
                          Text('your_account_is_highly_secure'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF15803D))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Security Toggles ─────────────────────────────────────
              Text('account_protection'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    ListTile(
                      leading: Icon(Icons.fingerprint_rounded, color: Color(0xFF2563EB), size: 22),
                      title: Text('biometric_login'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      subtitle: Text('unlock_app_using_face_id'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                      trailing: Switch(
                        value: _biometricEnabled,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _biometricEnabled = val),
                      ),
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    ListTile(
                      leading: Icon(Icons.phonelink_lock_rounded, color: Color(0xFF2563EB), size: 22),
                      title: Text('twofactor_authentication_2fa'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      subtitle: Text('otp_required_for_login_on'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                      trailing: Switch(
                        value: _twoFactorEnabled,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _twoFactorEnabled = val),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Active Sessions ──────────────────────────────────────
              Text('active_loggedin_devices'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.phone_iphone_rounded, color: Color(0xFF2563EB), size: 28),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('iphone_15_pro_this_device'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('bengaluru_india_active_now'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF16A34A), fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ),
                    TextButton(
                      onPressed: () {},
                      child: Text('revoke'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── Data & Privacy Control ───────────────────────────────
              Text('data_privacy_control'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    ListTile(
                      leading: Icon(Icons.download_rounded, color: Color(0xFF2563EB), size: 22),
                      title: Text('download_my_data'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      subtitle: Text('request_a_copy_of_your'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                      onTap: () {},
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    ListTile(
                      leading: Icon(Icons.cleaning_services_rounded, color: Color(0xFF2563EB), size: 22),
                      title: Text('clear_search_browsing_history'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      onTap: () {},
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Delete Account Section ───────────────────────────────
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFFCA5A5)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.delete_forever_rounded, color: Color(0xFFEF4444), size: 28),
                    SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('delete_account_permanently'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF991B1B))),
                          SizedBox(height: 2),
                          Text('irreversibly_delete_your_profile_booking'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFF7F1D1D))),
                        ],
                      ),
                    ),
                    TextButton(
                      onPressed: () {},
                      child: Text('delete'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Color(0xFFEF4444))),
                    ),
                  ],
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
