// File: lib/worker/settings/settings_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../utils/validators.dart';

class WorkerSettingsScreen extends StatefulWidget {
  const WorkerSettingsScreen({super.key});

  @override
  State<WorkerSettingsScreen> createState() => _WorkerSettingsScreenState();
}

class _WorkerSettingsScreenState extends State<WorkerSettingsScreen> {
  bool _darkMode = false;
  bool _autoAccept = true;
  bool _emergencyJobs = true;
  bool _inspectionRequests = true;
  bool _biometricLogin = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Application Settings',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Job Dispatch Preferences Card
              _buildSectionHeader('Job Dispatch Preferences'),
              const SizedBox(height: 10),

              _buildSwitchTile(
                title: 'Auto-Accept Instant Jobs',
                subtitle: 'Automatically accept jobs within 5km radius',
                value: _autoAccept,
                onChanged: (v) => setState(() => _autoAccept = v),
              ),
              const SizedBox(height: 8),
              _buildSwitchTile(
                title: 'Emergency / Urgent Job Dispatch',
                subtitle: 'Receive high priority emergency job alerts',
                value: _emergencyJobs,
                onChanged: (v) => setState(() => _emergencyJobs = v),
              ),
              const SizedBox(height: 8),
              _buildSwitchTile(
                title: 'Pre-Repair Inspection Requests',
                subtitle: 'Receive diagnostic inspection assignments',
                value: _inspectionRequests,
                onChanged: (v) => setState(() => _inspectionRequests = v),
              ),

              const SizedBox(height: 24),

              // Security & Biometrics
              _buildSectionHeader('Security & Biometrics'),
              const SizedBox(height: 10),

              _buildSwitchTile(
                title: 'Biometric / Fingerprint Unlock',
                subtitle: 'Require TouchID / FaceID to open partner app',
                value: _biometricLogin,
                onChanged: (v) => setState(() => _biometricLogin = v),
              ),
              const SizedBox(height: 8),
              _buildSettingTile(
                title: 'Change Password',
                subtitle: 'Update your partner account password',
                icon: Icons.lock_outline_rounded,
                onTap: () => _showChangePasswordDialog(context),
              ),

              const SizedBox(height: 24),

              // App General Settings
              _buildSectionHeader('App Preferences & Info'),
              const SizedBox(height: 10),

              _buildSwitchTile(
                title: 'Dark Theme Mode',
                subtitle: 'Switch application color palette',
                value: _darkMode,
                onChanged: (v) => setState(() => _darkMode = v),
              ),

              const SizedBox(height: 12),

              _buildSettingTile(
                title: 'App Language',
                subtitle: 'English (India)',
                icon: Icons.language_rounded,
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('App Language: English (India) selected.'),
                    ),
                  );
                },
              ),
              const SizedBox(height: 8),
              _buildSettingTile(
                title: 'Terms of Partner Service',
                subtitle: 'Legal policies for KaamSetu partners',
                icon: Icons.description_outlined,
                onTap: () => Navigator.pushNamed(context, '/worker/legal/terms'),
              ),
              const SizedBox(height: 8),
              _buildSettingTile(
                title: 'App Version',
                subtitle: 'v1.0.0 Partner Stable (Build 108)',
                icon: Icons.info_outline_rounded,
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('App is up to date (v1.0.0 Build 108)'),
                    ),
                  );
                },
              ),

              const SizedBox(height: 32),

              // Logout Button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                        title: const Text('Confirm Logout', style: TextStyle(fontWeight: FontWeight.w800)),
                        content: const Text('Are you sure you want to logout from your KaamSetu Partner account?'),
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
                                AppRoutes.workerAuth,
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
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Text(
                    'Log Out',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 15,
        fontWeight: FontWeight.w800,
        color: Color(0xFF0F172A),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            activeColor: const Color(0xFF2563EB),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildSettingTile({
    required String title,
    required String subtitle,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
      ),
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
        leading: Icon(icon, color: const Color(0xFF64748B), size: 20),
        title: Text(
          title,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: Color(0xFF0F172A),
          ),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(
            fontSize: 11,
            color: Color(0xFF64748B),
          ),
        ),
        trailing: const Icon(Icons.chevron_right_rounded,
            color: Color(0xFF94A3B8), size: 18),
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
                  const Text('Change Partner Password', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
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
                                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerAuth, (r) => false);
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
