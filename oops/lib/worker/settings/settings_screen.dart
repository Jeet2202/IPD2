// File: lib/worker/settings/settings_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';

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
}
