// File: lib/customer/profile/profile_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../services/auth_service.dart';
import '../../services/api_service.dart';
import '../../l10n/app_translations.dart';
import '../../widgets/language_selector_widget.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  Map<String, dynamic>? _profileData;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final res = await AuthService.instance.fetchCustomerProfile();
      if (mounted) {
        setState(() {
          _profileData = res;
          _isLoading = false;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.message;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Failed to load profile details. Please try again.';
          _isLoading = false;
        });
      }
    }
  }

  String _getInitials(String name) {
    if (name.isEmpty) return 'CS';
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.substring(0, name.length >= 2 ? 2 : 1).toUpperCase();
  }

  String _getCompletionText(int percentage) {
    if (percentage >= 100) return 'Profile Complete';
    if (percentage >= 70) return 'Almost Complete';
    if (percentage >= 31) return 'Keep Going';
    return 'Getting Started';
  }

  List<String> _getSuggestions(Map<String, dynamic> data) {
    final suggestions = <String>[];
    if (data['profile_photo_url'] == null) suggestions.add('Add profile photo (+10%)');
    if (data['alternate_phone'] == null) suggestions.add('Add alternate phone number');
    if (data['gender'] == null) suggestions.add('Select gender (+10%)');
    if (data['date_of_birth'] == null) suggestions.add('Set date of birth (+10%)');
    final addresses = data['addresses'] as List?;
    if (addresses == null || addresses.isEmpty) suggestions.add('Add primary service address (+20%)');
    return suggestions;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            } else {
              Navigator.pushReplacementNamed(context, AppRoutes.customerHome);
            }
          },
        ),
        title: Text(
          'profile'.tr(context),
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Color(0xFF0F172A)),
            onPressed: () => Navigator.pushNamed(context, AppRoutes.customerSettings),
          ),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadProfile,
          color: const Color(0xFF2563EB),
          child: _isLoading
              ? _buildSkeletonLoader()
              : _errorMessage != null
                  ? _buildErrorView()
                  : SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // ── Hero Profile Header ───────────────────────────
                          _buildProfileHeaderCard(),

                          const SizedBox(height: 20),

                          // ── Profile Completion Card (Backend Powered) ─────
                          _buildCompletionCard(),

                          const SizedBox(height: 20),

                          // ── Detailed Personal Info Card ──────────────────
                          _buildPersonalInfoCard(),

                          const SizedBox(height: 24),

                          // ── Action Menu Items ────────────────────────────
                          _buildMenuCard(),

                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
        ),
      ),
    );
  }

  Widget _buildProfileHeaderCard() {
    final data = _profileData!;
    final fullName = (data['full_name'] as String?) ?? 'Customer';
    final email = (data['email'] as String?) ?? '';
    final phone = (data['phone'] as String?) ?? '';
    final photoUrl = data['profile_photo_url'] as String?;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 16, offset: const Offset(0, 4)),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 36,
            backgroundColor: const Color(0xFFDBEAFE),
            backgroundImage: (photoUrl != null && photoUrl.isNotEmpty) ? NetworkImage(photoUrl) : null,
            child: (photoUrl == null || photoUrl.isEmpty)
                ? Text(
                    _getInitials(fullName),
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF2563EB)),
                  )
                : null,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        fullName,
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Tooltip(
                      message: 'Verified Account',
                      child: Icon(Icons.verified_rounded, color: Color(0xFF2563EB), size: 18),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(phone, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF64748B))),
                const SizedBox(height: 2),
                Text(email, style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)), overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionCard() {
    final data = _profileData!;
    final percentage = (data['profile_completion_percentage'] as num?)?.toInt() ?? 0;
    final isCompleted = data['profile_completed'] as bool? ?? false;
    final suggestions = _getSuggestions(data);

    if (isCompleted || percentage >= 100) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isCompleted
              ? [const Color(0xFF10B981), const Color(0xFF059669)]
              : [const Color(0xFF2563EB), const Color(0xFF1D4ED8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: (isCompleted ? const Color(0xFF10B981) : const Color(0xFF2563EB)).withValues(alpha: 0.25),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              percentage >= 100
                  ? const SizedBox(
                      width: 54,
                      height: 54,
                      child: Icon(Icons.check_circle_rounded, color: Colors.white, size: 54),
                    )
                  : Stack(
                      alignment: Alignment.center,
                      children: [
                        SizedBox(
                          width: 54,
                          height: 54,
                          child: CircularProgressIndicator(
                            value: percentage / 100.0,
                            strokeWidth: 6,
                            backgroundColor: Colors.white24,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          '$percentage%',
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: Colors.white),
                        ),
                      ],
                    ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getCompletionText(percentage),
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      isCompleted ? 'Your profile meets all booking requirements!' : 'Complete your profile for faster booking checkout.',
                      style: const TextStyle(fontSize: 12, color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (suggestions.isNotEmpty && !isCompleted) ...[
            const SizedBox(height: 16),
            const Divider(color: Colors.white24, height: 1),
            const SizedBox(height: 12),
            const Text(
              'Suggestions to reach 100%:',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 6),
            ...suggestions.map(
              (s) => Padding(
                padding: const EdgeInsets.only(bottom: 4.0),
                child: Row(
                  children: [
                    const Icon(Icons.add_circle_outline_rounded, color: Colors.white70, size: 14),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(s, style: const TextStyle(fontSize: 11, color: Color(0xE6FFFFFF))),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPersonalInfoCard() {
    final data = _profileData!;
    final gender = (data['gender'] as String?)?.toUpperCase() ?? 'Not Set';
    final lang = (data['preferred_language'] as String?)?.toUpperCase() ?? 'HI';
    final dob = data['date_of_birth'] as String? ?? 'Not Set';
    final altPhone = data['alternate_phone'] as String? ?? 'Not Set';
    final addresses = data['addresses'] as List?;
    String defaultAddr = 'No saved addresses';
    if (addresses != null && addresses.isNotEmpty) {
      final first = addresses.first as Map<String, dynamic>;
      defaultAddr = '${first['address_line1'] ?? ''}, ${first['city'] ?? ''}'.trim();
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('customer_profile'.tr(context), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 16),
          _InfoRow(icon: Icons.phone_android_rounded, label: 'alternate_phone'.tr(context), value: altPhone),
          const SizedBox(height: 12),
          _InfoRow(icon: Icons.cake_rounded, label: 'date_of_birth'.tr(context), value: dob),
          const SizedBox(height: 12),
          _InfoRow(icon: Icons.person_outline_rounded, label: 'gender'.tr(context), value: gender),
          const SizedBox(height: 12),
          _InfoRow(icon: Icons.language_rounded, label: 'language'.tr(context), value: lang),
          const SizedBox(height: 12),
          _InfoRow(icon: Icons.location_on_outlined, label: 'service_address'.tr(context), value: defaultAddr),
        ],
      ),
    );
  }

  Widget _buildMenuCard() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        children: [
          _MenuItem(
            icon: Icons.language_rounded,
            title: 'select_language'.tr(context),
            onTap: () => LanguageSelectorWidget.show(context),
          ),
          _MenuItem(
            icon: Icons.person_outline_rounded,
            title: 'edit_profile'.tr(context),
            onTap: () async {
              await Navigator.pushNamed(context, AppRoutes.editProfile);
              _loadProfile();
            },
          ),
          _MenuItem(
            icon: Icons.receipt_long_rounded,
            title: 'my_bookings'.tr(context),
            onTap: () => Navigator.pushNamed(context, AppRoutes.myBookings),
          ),
          _MenuItem(
            icon: Icons.location_on_outlined,
            title: 'saved_addresses'.tr(context),
            onTap: () async {
              await Navigator.pushNamed(context, AppRoutes.savedAddresses);
              _loadProfile();
            },
          ),
          _MenuItem(
            icon: Icons.lock_reset_rounded,
            title: 'change_password'.tr(context),
            onTap: () => Navigator.pushNamed(context, AppRoutes.customerSettings),
          ),
          _MenuItem(
            icon: Icons.notifications_none_rounded,
            title: 'notifications'.tr(context),
            onTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
          ),
          _MenuItem(
            icon: Icons.help_outline_rounded,
            title: 'help_support'.tr(context),
            onTap: () => Navigator.pushNamed(context, AppRoutes.helpSupport),
          ),
          _MenuItem(
            icon: Icons.logout_rounded,
            title: 'logout'.tr(context),
            isRed: true,
            onTap: _showLogoutDialog,
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletonLoader() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: [
          Container(
            height: 100,
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24)),
          ),
          const SizedBox(height: 20),
          Container(
            height: 120,
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24)),
          ),
          const SizedBox(height: 20),
          Container(
            height: 200,
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(24)),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.cloud_off_rounded, size: 64, color: Color(0xFF94A3B8)),
            const SizedBox(height: 16),
            const Text('Failed to load profile', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
            const SizedBox(height: 8),
            Text(_errorMessage ?? 'Network error', textAlign: TextAlign.center, style: const TextStyle(fontSize: 13, color: Color(0xFF64748B))),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadProfile,
              icon: const Icon(Icons.refresh_rounded),
              label: Text('retry'.tr(context)),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text('confirm_logout'.tr(context), style: const TextStyle(fontWeight: FontWeight.w800)),
        content: Text('confirm_logout'.tr(context)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('cancel'.tr(context), style: const TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await AuthService.instance.logout();
              if (mounted) {
                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.customerLogin, (route) => false);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: Text('yes_logout'.tr(context), style: const TextStyle(fontWeight: FontWeight.w800)),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: const Color(0xFF2563EB)),
        const SizedBox(width: 12),
        Text(label, style: const TextStyle(fontSize: 13, color: Color(0xFF64748B))),
        const Spacer(),
        Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
      ],
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final bool isRed;

  const _MenuItem({
    required this.icon,
    required this.title,
    required this.onTap,
    this.isRed = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF475569)),
      title: Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF0F172A))),
      trailing: const Icon(Icons.chevron_right_rounded, color: Color(0xFF94A3B8)),
      onTap: onTap,
    );
  }
}
