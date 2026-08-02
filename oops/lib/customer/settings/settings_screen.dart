// File:
// lib/customer/settings/settings_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../utils/validators.dart';

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
                      subtitle: 'Update your account password',
                      onTap: () => _showChangePasswordDialog(context),
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
                    _SettingTile(
                      icon: Icons.info_outline_rounded,
                      title: 'App Version',
                      subtitle: 'v2.4.0 (Build 9021)',
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('KaamSetu Customer App is up to date (v2.4.0)')),
                        );
                      },
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.description_outlined,
                      title: 'Terms of Service',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.termsConditions),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.privacy_tip_outlined,
                      title: 'Privacy Policy',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.privacyPolicy),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 28),

              // ── Logout & Delete ──────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                        title: const Text('Confirm Logout', style: TextStyle(fontWeight: FontWeight.w800)),
                        content: const Text('Are you sure you want to logout from your KaamSetu account?'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(ctx),
                            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
                          ),
                          ElevatedButton(
                            onPressed: () {
                              Navigator.pop(ctx);
                              Navigator.pushNamedAndRemoveUntil(
                                context,
                                AppRoutes.customerLogin,
                                (route) => false,
                              );
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFEF4444),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            child: const Text('Logout', style: TextStyle(fontWeight: FontWeight.w800)),
                          ),
                        ],
                      ),
                    );
                  },
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

  void _showChangePasswordDialog(BuildContext context) {
    final formKey = GlobalKey<FormState>();
    final currentCtr = TextEditingController();
    final newCtr = TextEditingController();
    final confirmCtr = TextEditingController();
    bool loading = false;
    bool obscureCurrent = true;
    bool obscureNew = true;
    bool obscureConfirm = true;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) {
          return Padding(
            padding: EdgeInsets.only(
              left: 24,
              right: 24,
              top: 24,
              bottom: MediaQuery.of(context).viewInsets.bottom + 24,
            ),
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E8F0),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text('Change Password', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                  const SizedBox(height: 6),
                  const Text('Enter your current password and set a new password.', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                  const SizedBox(height: 20),

                  TextFormField(
                    controller: currentCtr,
                    obscureText: obscureCurrent,
                    decoration: InputDecoration(
                      labelText: 'Current Password',
                      suffixIcon: IconButton(
                        icon: Icon(obscureCurrent ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                        onPressed: () => setModalState(() => obscureCurrent = !obscureCurrent),
                      ),
                    ),
                    validator: (v) => (v == null || v.isEmpty) ? 'Current password is required' : null,
                  ),
                  const SizedBox(height: 14),

                  TextFormField(
                    controller: newCtr,
                    obscureText: obscureNew,
                    decoration: InputDecoration(
                      labelText: 'New Password',
                      suffixIcon: IconButton(
                        icon: Icon(obscureNew ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                        onPressed: () => setModalState(() => obscureNew = !obscureNew),
                      ),
                    ),
                    validator: Validators.password,
                  ),
                  const SizedBox(height: 14),

                  TextFormField(
                    controller: confirmCtr,
                    obscureText: obscureConfirm,
                    decoration: InputDecoration(
                      labelText: 'Confirm New Password',
                      suffixIcon: IconButton(
                        icon: Icon(obscureConfirm ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                        onPressed: () => setModalState(() => obscureConfirm = !obscureConfirm),
                      ),
                    ),
                    validator: (v) => Validators.confirmPassword(v, newCtr.text),
                  ),
                  const SizedBox(height: 24),

                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      onPressed: loading
                          ? null
                          : () async {
                              if (!formKey.currentState!.validate()) return;
                              setModalState(() => loading = true);
                              try {
                                await AuthService.instance.changePassword(
                                  currentPassword: currentCtr.text,
                                  newPassword: newCtr.text,
                                );
                                if (!context.mounted) return;
                                Navigator.pop(ctx);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Password changed successfully. Please log in again.'),
                                    backgroundColor: Color(0xFF2563EB),
                                  ),
                                );
                                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerLogin, (r) => false);
                              } catch (e) {
                                if (!context.mounted) return;
                                final msg = e is ApiException ? e.message : 'Change password failed: $e';
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text(msg), backgroundColor: Colors.red),
                                );
                              } finally {
                                setModalState(() => loading = false);
                              }
                            },
                      child: loading
                          ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Text('Update Password', style: TextStyle(fontWeight: FontWeight.w700)),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
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
