// File: lib/customer/settings/settings_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../l10n/app_translations.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _profileData;

  bool _pushNotifications = true;
  bool _emailNotifications = true;
  bool _smsNotifications = true;

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
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final res = await AuthService.instance.fetchCustomerProfile();
      if (mounted) {
        setState(() {
          _profileData = res;
          final notifs = res['notification_preferences'] as Map<String, dynamic>?;
          if (notifs != null) {
            _pushNotifications = notifs['push'] as bool? ?? true;
            _emailNotifications = notifs['email'] as bool? ?? true;
            _smsNotifications = notifs['sms'] as bool? ?? true;
          }
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _updateNotificationPreferences() async {
    try {
      await AuthService.instance.updateCustomerProfile({
        'notification_preferences': {
          'push': _pushNotifications,
          'email': _emailNotifications,
          'sms': _smsNotifications,
        },
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('preferences_updated'.tr(context)), backgroundColor: Color(0xFF16A34A)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update preferences: $e'), backgroundColor: Colors.red),
        );
      }
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
            title: Text('change_password'.tr(context), style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
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
                    SizedBox(height: 14),
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
                    SizedBox(height: 14),
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
                child: Text('cancel'.tr(context), style: TextStyle(color: Color(0xFF64748B))),
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
                                content: Text('password_changed_successfully_please_log'.tr(context)),
                                backgroundColor: Color(0xFF16A34A),
                              ),
                            );
                            Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerLogin, (r) => false);
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
                    ? SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : Text('update_password'.tr(context)),
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
        title: Text('logout_all_devices'.tr(context), style: TextStyle(fontWeight: FontWeight.w800)),
        content: Text('are_you_sure_you_want_3'.tr(context)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('cancel'.tr(context), style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await AuthService.instance.logoutAll();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('logged_out_from_all_devices'.tr(context)), backgroundColor: Color(0xFF16A34A)),
                );
                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerLogin, (r) => false);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: Text('logout_all'.tr(context)),
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
            title: Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444)),
                SizedBox(width: 8),
                Text('delete_account'.tr(context), style: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
              ],
            ),
            content: Form(
              key: _deleteFormKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('this_action_is_permanent_and'.tr(context),
                    style: TextStyle(fontSize: 13, color: Color(0xFF475569)),
                  ),
                  SizedBox(height: 16),
                  Text('enter_your_password_to_confirm'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                  SizedBox(height: 8),
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
                child: Text('cancel'.tr(context), style: TextStyle(color: Color(0xFF64748B))),
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
                              const SnackBar(content: Text('account_permanently_deleted'.tr(context)), backgroundColor: Color(0xFF16A34A)),
                            );
                            Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerLogin, (r) => false);
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
                    ? SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : Text('permanently_delete'.tr(context)),
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
    final fullName = (data?['full_name'] as String?) ?? 'Customer';
    final email = (data?['email'] as String?) ?? '';
    final phone = (data?['phone'] as String?) ?? '';
    final photoUrl = data?['profile_photo_url'] as String?;
    final completion = (data?['profile_completion_percentage'] as num?)?.toInt() ?? 0;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('settings_account'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: _isLoading
            ? Center(child: CircularProgressIndicator())
            : SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── ACCOUNT SECTION ─────────────────────────────────────
              Text('account_information'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
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
                              ? Icon(Icons.person_rounded, size: 32, color: Color(0xFF2563EB))
                              : null,
                        ),
                        SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(fullName, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                              SizedBox(height: 2),
                              Text(email, style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                              Text(phone, style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                            ],
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 14),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Profile Completion: $completion%', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
                        TextButton(
                          onPressed: () => Navigator.pushNamed(context, AppRoutes.customerProfile),
                          child: Text('view_full_profile'.tr(context)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── SECURITY SECTION ────────────────────────────────────
              Text('security_sessions'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

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
                      subtitle: 'Update your login password',
                      onTap: _showChangePasswordDialog,
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.devices_rounded,
                      title: 'Logout All Devices',
                      subtitle: 'Revoke active sessions across all devices',
                      onTap: _showLogoutAllDialog,
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.logout_rounded,
                      title: 'Logout Current Session',
                      subtitle: 'Sign out from this device',
                      isRed: true,
                      onTap: () async {
                        await AuthService.instance.logout();
                        if (mounted) {
                          Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerLogin, (r) => false);
                        }
                      },
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── PREFERENCES SECTION ──────────────────────────────────
              Text('app_preferences'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    SwitchListTile(
                      title: Text('push_notifications'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      value: _pushNotifications,
                      activeThumbColor: const Color(0xFF2563EB),
                      onChanged: (val) {
                        setState(() => _pushNotifications = val);
                        _updateNotificationPreferences();
                      },
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SwitchListTile(
                      title: Text('email_alerts'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      value: _emailNotifications,
                      activeThumbColor: const Color(0xFF2563EB),
                      onChanged: (val) {
                        setState(() => _emailNotifications = val);
                        _updateNotificationPreferences();
                      },
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SwitchListTile(
                      title: Text('sms_updates'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      value: _smsNotifications,
                      activeThumbColor: const Color(0xFF2563EB),
                      onChanged: (val) {
                        setState(() => _smsNotifications = val);
                        _updateNotificationPreferences();
                      },
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── SUPPORT & LEGAL SECTION ─────────────────────────────
              Text('support_legal'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF94A3B8))),
              SizedBox(height: 10),

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
                      title: 'Help & Support Center',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.helpSupport),
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.policy_rounded,
                      title: 'Privacy Policy',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.privacyPolicy),
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.description_outlined,
                      title: 'Terms & Conditions',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.termsConditions),
                    ),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    _SettingTile(
                      icon: Icons.info_outline_rounded,
                      title: 'About Ally',
                      subtitle: 'Version 1.0.0 (Build 2026.08)',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.aboutUs),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // ── DANGER ZONE ──────────────────────────────────────────
              Text('danger_zone'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFEF4444))),
              SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFFCA5A5)),
                ),
                child: _SettingTile(
                  icon: Icons.delete_forever_rounded,
                  title: 'Delete Account',
                  subtitle: 'Permanently remove your account & all data',
                  isRed: true,
                  onTap: _showDeleteAccountDialog,
                ),
              ),

              SizedBox(height: 32),
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
        subtitle: subtitle != null ? Text(subtitle!, style: TextStyle(fontSize: 12, color: Color(0xFF64748B))) : null,
        trailing: Icon(Icons.chevron_right_rounded, color: Color(0xFF94A3B8)),
        onTap: onTap,
      ),
    );
  }
}
