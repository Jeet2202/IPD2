// File:
// lib/customer/settings/settings_screen.dart

import 'package:flutter/material.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _locationEnabled = true;
  bool _autoUpdates = true;
  bool _biometricEnabled = true;

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
          'Settings',
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
              // ── General Preferences ──────────────────────────────────
              const Text('GENERAL PREFERENCES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _SettingTile(
                      icon: Icons.language_rounded,
                      title: 'App Language',
                      subtitle: 'English (US)',
                      onTap: () {},
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingSwitchTile(
                      icon: Icons.notifications_none_rounded,
                      title: 'Push Notifications',
                      value: _notificationsEnabled,
                      onChanged: (val) => setState(() => _notificationsEnabled = val),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingSwitchTile(
                      icon: Icons.location_on_outlined,
                      title: 'GPS Location Access',
                      value: _locationEnabled,
                      onChanged: (val) => setState(() => _locationEnabled = val),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Booking Alerts ──────────────────────────────────────
              const Text('BOOKING ALERTS & UPDATES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _SettingSwitchTile(
                      icon: Icons.mark_chat_unread_outlined,
                      title: 'Real-time Service WhatsApp Updates',
                      value: _autoUpdates,
                      onChanged: (val) => setState(() => _autoUpdates = val),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Security Settings ───────────────────────────────────
              const Text('SECURITY & PRIVACY', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _SettingSwitchTile(
                      icon: Icons.fingerprint_rounded,
                      title: 'Biometric / Face ID Unlock',
                      value: _biometricEnabled,
                      onChanged: (val) => setState(() => _biometricEnabled = val),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.lock_outline_rounded,
                      title: 'Change Password',
                      subtitle: 'Last updated 3 months ago',
                      onTap: () {},
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── About Application ───────────────────────────────────
              const Text('ABOUT KAAMSETU', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _SettingTile(icon: Icons.info_outline_rounded, title: 'App Version', subtitle: 'v2.4.0 (Build 9021)', onTap: () {}),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(icon: Icons.description_outlined, title: 'Terms of Service', onTap: () {}),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(icon: Icons.privacy_tip_outlined, title: 'Privacy Policy', onTap: () {}),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // ── Logout & Delete ──────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.logout_rounded, color: Color(0xFFEF4444)),
                  label: const Text('Logout Account', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFFCA5A5)),
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

class _SettingTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback onTap;

  const _SettingTile({required this.icon, required this.title, this.subtitle, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      leading: Icon(icon, color: const Color(0xFF2563EB), size: 22),
      title: Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
      subtitle: subtitle != null ? Text(subtitle!, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))) : null,
      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Color(0xFF94A3B8)),
    );
  }
}

class _SettingSwitchTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SettingSwitchTile({required this.icon, required this.title, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: const Color(0xFF2563EB), size: 22),
      title: Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
      trailing: Switch(
        value: value,
        activeColor: const Color(0xFF2563EB),
        onChanged: onChanged,
      ),
    );
  }
}
