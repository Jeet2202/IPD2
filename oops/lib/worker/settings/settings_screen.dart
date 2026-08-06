// File: lib/worker/settings/settings_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';

class WorkerSettingsScreen extends StatefulWidget {
  const WorkerSettingsScreen({super.key});

  @override
  State<WorkerSettingsScreen> createState() => _WorkerSettingsScreenState();
}

class _WorkerSettingsScreenState extends State<WorkerSettingsScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _profileData;

  bool _pushNotifications = true;
  bool _emailNotifications = true;

  final _changePwdFormKey = GlobalKey<FormState>();
  final _currentPwdController = TextEditingController();
  final _newPwdController = TextEditingController();
  final _confirmPwdController = TextEditingController();

  final _deleteFormKey = GlobalKey<FormState>();
  final _deletePasswordController = TextEditingController();

  bool _isActionLoading = false;

  @override
  void initState() {
    super.initState();
    _loadWorkerProfile();
  }

  Future<void> _loadWorkerProfile() async {
    try {
      final res = await AuthService.instance.fetchWorkerProfile();
      if (mounted) {
        setState(() {
          _profileData = res;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showChangePasswordDialog() {
    _currentPwdController.clear();
    _newPwdController.clear();
    _confirmPwdController.clear();

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            title: const Text('Change Password', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
            content: Form(
              key: _changePwdFormKey,
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextFormField(
                      controller: _currentPwdController,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: 'Current Password',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      validator: (v) => (v == null || v.isEmpty) ? 'Required' : null,
                    ),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _newPwdController,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: 'New Password',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      validator: (v) {
                        if (v == null || v.length < 8) return 'Min 8 characters required';
                        return null;
                      },
                    ),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _confirmPwdController,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: 'Confirm New Password',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      validator: (v) {
                        if (v != _newPwdController.text) return 'Passwords do not match';
                        return null;
                      },
                    ),
                  ],
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
              ),
              ElevatedButton(
                onPressed: _isActionLoading
                    ? null
                    : () async {
                        if (!_changePwdFormKey.currentState!.validate()) return;
                        setDialogState(() => _isActionLoading = true);
                        try {
                          await AuthService.instance.changePassword(
                            currentPassword: _currentPwdController.text,
                            newPassword: _newPwdController.text,
                          );
                          if (mounted) {
                            Navigator.pop(ctx);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Password changed successfully! Please log in again.'),
                                backgroundColor: Color(0xFF16A34A),
                              ),
                            );
                            Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerLogin, (r) => false);
                          }
                        } on ApiException catch (e) {
                          setDialogState(() => _isActionLoading = false);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(e.message), backgroundColor: Colors.red),
                          );
                        } catch (e) {
                          setDialogState(() => _isActionLoading = false);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Failed: $e'), backgroundColor: Colors.red),
                          );
                        }
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isActionLoading
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text('Update Password'),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showLogoutAllDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Logout All Devices', style: TextStyle(fontWeight: FontWeight.w800)),
        content: const Text('Are you sure you want to revoke all active sessions for your partner account?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await AuthService.instance.logoutAll();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Logged out from all devices.'), backgroundColor: Color(0xFF16A34A)),
                );
                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerLogin, (r) => false);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: const Text('Logout All'),
          ),
        ],
      ),
    );
  }

  void _showDeleteAccountDialog() {
    _deletePasswordController.clear();
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) {
          return AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            title: const Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444)),
                SizedBox(width: 8),
                Text('Delete Partner Account', style: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
              ],
            ),
            content: Form(
              key: _deleteFormKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Deleting your partner account will remove all your professional ratings, job history, profile photos, and verification records permanently.',
                    style: TextStyle(fontSize: 13, color: Color(0xFF475569)),
                  ),
                  const SizedBox(height: 16),
                  const Text('Enter your password to confirm:', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _deletePasswordController,
                    obscureText: true,
                    decoration: InputDecoration(
                      hintText: 'Current Password',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    validator: (v) => (v == null || v.isEmpty) ? 'Password is required' : null,
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
              ),
              ElevatedButton(
                onPressed: _isActionLoading
                    ? null
                    : () async {
                        if (!_deleteFormKey.currentState!.validate()) return;
                        setDialogState(() => _isActionLoading = true);
                        try {
                          await AuthService.instance.deleteAccount(_deletePasswordController.text);
                          if (mounted) {
                            Navigator.pop(ctx);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Partner account permanently deleted.'), backgroundColor: Color(0xFF16A34A)),
                            );
                            Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerLogin, (r) => false);
                          }
                        } on ApiException catch (e) {
                          setDialogState(() => _isActionLoading = false);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(e.message), backgroundColor: Colors.red),
                          );
                        } catch (e) {
                          setDialogState(() => _isActionLoading = false);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Account deletion failed: $e'), backgroundColor: Colors.red),
                          );
                        }
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFEF4444),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isActionLoading
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text('Permanently Delete'),
              ),
            ],
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _currentPwdController.dispose();
    _newPwdController.dispose();
    _confirmPwdController.dispose();
    _deletePasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final data = _profileData;
    final fullName = (data?['full_name'] as String?) ?? 'Partner';
    final email = (data?['email'] as String?) ?? '';
    final phone = (data?['phone'] as String?) ?? '';
    final photoUrl = data?['profile_photo_url'] as String?;
    final completion = (data?['profile_completion_percentage'] as num?)?.toInt() ?? 0;

    return Scaffold(      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Partner Settings',
          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── PARTNER ACCOUNT SECTION ─────────────────────────────
              const Text('PARTNER ACCOUNT', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 28,
                          backgroundColor: const Color(0xFFDBEAFE),
                          backgroundImage: (photoUrl != null && photoUrl.isNotEmpty) ? NetworkImage(photoUrl) : null,
                          child: (photoUrl == null || photoUrl.isEmpty)
                              ? const Icon(Icons.person_rounded, size: 32, color: Color(0xFF2563EB))
                              : null,
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(fullName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                              const SizedBox(height: 2),
                              Text(email, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                              Text(phone, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const Divider(color: Color(0xFFE2E8F0), height: 1),
                    const SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Profile Score: $completion%', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
                        TextButton(
                          onPressed: () => Navigator.pushNamed(context, AppRoutes.workerProfile),
                          child: const Text('View Partner Profile'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── SECURITY SECTION ────────────────────────────────────
              const Text('SECURITY & SESSIONS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
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
                      icon: Icons.lock_reset_rounded,
                      title: 'Change Password',
                      subtitle: 'Update account login password',
                      onTap: _showChangePasswordDialog,
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.devices_rounded,
                      title: 'Logout All Devices',
                      subtitle: 'Revoke active sessions across all devices',
                      onTap: _showLogoutAllDialog,
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.logout_rounded,
                      title: 'Logout Current Session',
                      subtitle: 'Sign out from this device',
                      isRed: true,
                      onTap: () async {
                        await AuthService.instance.logout();
                        if (mounted) {
                          Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerLogin, (r) => false);
                        }
                      },
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── PREFERENCES SECTION ──────────────────────────────────
              const Text('PARTNER PREFERENCES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    SwitchListTile(
                      title: const Text('Job Request Notifications', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      value: _pushNotifications,
                      activeThumbColor: const Color(0xFF2563EB),
                      onChanged: (val) => setState(() => _pushNotifications = val),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    SwitchListTile(
                      title: const Text('Email Alerts & Payout Slips', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      value: _emailNotifications,
                      activeThumbColor: const Color(0xFF2563EB),
                      onChanged: (val) => setState(() => _emailNotifications = val),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── SUPPORT & LEGAL SECTION ─────────────────────────────
              const Text('SUPPORT & LEGAL', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
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
                      icon: Icons.help_outline_rounded,
                      title: 'Partner Support Center',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.workerSupport),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.policy_rounded,
                      title: 'Privacy Policy',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.workerPrivacy),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.description_outlined,
                      title: 'Terms of Service',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.workerTerms),
                    ),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.info_outline_rounded,
                      title: 'About Ally Partner',
                      subtitle: 'Version 1.0.0 (Build 2026.08)',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.workerAbout),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── DANGER ZONE ──────────────────────────────────────────
              const Text('DANGER ZONE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFFCA5A5)),
                ),
                child: _SettingTile(
                  icon: Icons.delete_forever_rounded,
                  title: 'Delete Partner Account',
                  subtitle: 'Permanently delete partner account & ratings',
                  isRed: true,
                  onTap: _showDeleteAccountDialog,
                ),
              ),

              const SizedBox(height: 32),
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
  final bool isRed;

  const _SettingTile({
    required this.icon,
    required this.title,
    this.subtitle,
    required this.onTap,
    this.isRed = false,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: ListTile(
        leading: Icon(icon, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF2563EB)),
        title: Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF0F172A))),
        subtitle: subtitle != null ? Text(subtitle!, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))) : null,
        trailing: const Icon(Icons.chevron_right_rounded, color: Color(0xFF94A3B8)),
        onTap: onTap,
      ),
    );
  }
}
