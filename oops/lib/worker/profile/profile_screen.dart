// File: lib/worker/profile/profile_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../services/auth_service.dart';
import '../../services/api_service.dart';
import '../widgets/worker_bottom_navigation_bar.dart';

class WorkerProfileScreen extends StatefulWidget {
  const WorkerProfileScreen({super.key});

  @override
  State<WorkerProfileScreen> createState() => _WorkerProfileScreenState();
}

class _WorkerProfileScreenState extends State<WorkerProfileScreen> {
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
      final res = await AuthService.instance.fetchWorkerProfile();
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
          _errorMessage = 'Failed to load partner profile. Please try again.';
          _isLoading = false;
        });
      }
    }
  }

  Color _getAvailabilityColor(String availability) {
    switch (availability.toLowerCase()) {
      case 'available':
        return const Color(0xFF10B981);
      case 'on_job':
      case 'busy':
        return const Color(0xFF2563EB);
      case 'unavailable':
      default:
        return const Color(0xFFEF4444);
    }
  }

  String _getAvailabilityLabel(String availability) {
    switch (availability.toLowerCase()) {
      case 'available':
        return 'Available for Jobs';
      case 'on_job':
        return 'Currently On Job';
      case 'busy':
        return 'Busy';
      case 'unavailable':
      default:
        return 'Unavailable';
    }
  }

  String _getCompletionText(int percentage) {
    if (percentage >= 100) return 'Profile Complete';
    if (percentage >= 70) return 'Almost Complete';
    if (percentage >= 31) return 'Keep Going';
    return 'Getting Started';
  }

  List<String> _getSuggestions(Map<String, dynamic> data) {
    final suggestions = <String>[];
    if (data['profile_photo_url'] == null) suggestions.add('Add partner photo (+10%)');
    final bio = data['bio'] as String?;
    if (bio == null || bio.trim().length < 20) suggestions.add('Write detailed professional bio (+15%)');
    final skills = data['skills'] as List?;
    if (skills == null || skills.isEmpty) suggestions.add('Add offered skills & services (+20%)');
    final exp = (data['experience_years'] as num?)?.toDouble() ?? 0.0;
    if (exp <= 0) suggestions.add('Add years of experience (+10%)');
    final langs = data['languages'] as List?;
    if (langs == null || langs.isEmpty) suggestions.add('Add spoken languages (+10%)');
    final rate = (data['hourly_rate'] as num?)?.toDouble() ?? 0.0;
    if (rate <= 0) suggestions.add('Set hourly service rate (+5%)');
    return suggestions;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
        title: const Text(
          'Partner Profile & Settings',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Color(0xFF0F172A)),
            onPressed: () => Navigator.pushNamed(context, '/worker/settings'),
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
                      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
                      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // ── Hero Profile Header Card ────────────────────
                          _buildHeroCard(),

                          const SizedBox(height: 20),

                          // ── Backend Profile Completion Progress Card ───
                          _buildCompletionCard(),

                          const SizedBox(height: 24),

                          // ── Availability Status Badge ──────────────────
                          _buildAvailabilityBadge(),

                          const SizedBox(height: 20),

                          // ── Skills & Experience Section ────────────────
                          _buildSkillsSection(),

                          const SizedBox(height: 20),

                          // ── Professional Bio Section ───────────────────
                          _buildBioSection(),

                          const SizedBox(height: 24),

                          // ── Settings Menu Items ───────────────────────
                          _buildMenuCard(),

                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
        ),
      ),
      bottomNavigationBar: const WorkerBottomNavigationBar(currentIndex: 4),
    );
  }

  Widget _buildHeroCard() {
    final data = _profileData!;
    final fullName = (data['full_name'] as String?) ?? 'Partner';
    final email = (data['email'] as String?) ?? '';
    final phone = (data['phone'] as String?) ?? '';
    final photoUrl = data['profile_photo_url'] as String?;
    final expYears = (data['experience_years'] as num?)?.toDouble() ?? 0.0;
    final hourlyRate = (data['hourly_rate'] as num?)?.toDouble();
    final rating = (data['rating'] as num?)?.toDouble() ?? 0.0;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF2563EB).withValues(alpha: 0.25),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 36,
                backgroundColor: Colors.white,
                backgroundImage: (photoUrl != null && photoUrl.isNotEmpty) ? NetworkImage(photoUrl) : null,
                child: (photoUrl == null || photoUrl.isEmpty)
                    ? const Icon(Icons.person_rounded, size: 42, color: Color(0xFF2563EB))
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
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w900,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 6),
                        const Icon(Icons.verified_rounded, color: Colors.white, size: 18),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(phone, style: const TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 2),
                    Text(email, style: const TextStyle(color: Colors.white70, fontSize: 12), overflow: TextOverflow.ellipsis),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Divider(color: Colors.white24, height: 1),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _WorkerHeroStat(title: 'Rating', value: rating > 0 ? rating.toStringAsFixed(1) : 'New', icon: Icons.star_rounded),
              _WorkerHeroStat(title: 'Experience', value: '${expYears.toStringAsFixed(expYears.truncateToDouble() == expYears ? 0 : 1)} yrs', icon: Icons.work_history_rounded),
              _WorkerHeroStat(title: 'Hourly Rate', value: hourlyRate != null && hourlyRate > 0 ? '₹${hourlyRate.toInt()}/hr' : 'Flexible', icon: Icons.payments_rounded),
            ],
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

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 50,
                    height: 50,
                    child: CircularProgressIndicator(
                      value: percentage / 100.0,
                      strokeWidth: 6,
                      backgroundColor: const Color(0xFFE2E8F0),
                      color: isCompleted ? const Color(0xFF10B981) : const Color(0xFF2563EB),
                    ),
                  ),
                  Text(
                    '$percentage%',
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
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
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      isCompleted ? 'Your profile is fully verified for customer matching.' : 'Complete partner profile to rank higher in customer searches.',
                      style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (suggestions.isNotEmpty && !isCompleted) ...[
            const SizedBox(height: 16),
            const Divider(color: Color(0xFFE2E8F0), height: 1),
            const SizedBox(height: 12),
            const Text(
              'Suggestions to boost ranking:',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 6),
            ...suggestions.map(
              (s) => Padding(
                padding: const EdgeInsets.only(bottom: 4.0),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle_outline_rounded, color: Color(0xFF2563EB), size: 14),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(s, style: const TextStyle(fontSize: 11, color: Color(0xFF334155), fontWeight: FontWeight.w500)),
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

  Widget _buildAvailabilityBadge() {
    final data = _profileData!;
    final availability = (data['availability'] as String?) ?? 'available';
    final radius = (data['working_radius_km'] as num?)?.toDouble() ?? 10.0;
    final color = _getAvailabilityColor(availability);
    final label = _getAvailabilityLabel(availability);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 10),
          Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: color)),
          const Spacer(),
          Icon(Icons.near_me_rounded, size: 14, color: color),
          const SizedBox(width: 4),
          Text('${radius.toInt()} km radius', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
        ],
      ),
    );
  }

  Widget _buildSkillsSection() {
    final data = _profileData!;
    final rawSkills = data['skills'] as List?;
    final skills = rawSkills?.map((s) => s.toString()).toList() ?? [];
    final rawLangs = data['languages'] as List?;
    final langs = rawLangs?.map((l) => l.toString().toUpperCase()).toList() ?? [];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Offered Services & Skills', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 12),
          skills.isNotEmpty
              ? Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: skills.map((s) => Chip(
                    label: Text(s, style: const TextStyle(fontSize: 12, color: Color(0xFF1E40AF))),
                    backgroundColor: const Color(0xFFEFF6FF),
                    side: const BorderSide(color: Color(0xFFBFDBFE)),
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                  )).toList(),
                )
              : const Text('No skills added yet', style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
          if (langs.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('Spoken Languages', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: langs.map((l) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(8)),
                child: Text(l, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF475569))),
              )).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBioSection() {
    final data = _profileData!;
    final bio = (data['bio'] as String?) ?? 'No professional bio provided yet.';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Professional Bio', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 8),
          Text(
            bio,
            style: const TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF475569)),
          ),
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
            icon: Icons.edit_note_rounded,
            title: 'Edit Partner Profile',
            onTap: () async {
              await Navigator.pushNamed(context, AppRoutes.workerEditProfile);
              _loadProfile();
            },
          ),
          _MenuItem(
            icon: Icons.lock_reset_rounded,
            title: 'Change Password',
            onTap: () => Navigator.pushNamed(context, '/worker/settings'),
          ),
          _MenuItem(
            icon: Icons.logout_rounded,
            title: 'Logout',
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
          Container(height: 160, decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(24))),
          const SizedBox(height: 20),
          Container(height: 100, decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(24))),
          const SizedBox(height: 20),
          Container(height: 140, decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(24))),
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
              label: const Text('Try Again'),
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
        title: const Text('Confirm Logout', style: TextStyle(fontWeight: FontWeight.w800)),
        content: const Text('Are you sure you want to logout from your KaamSetu Partner account?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await AuthService.instance.logout();
              if (mounted) {
                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerLogin, (route) => false);
              }
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
  }
}

class _WorkerHeroStat extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _WorkerHeroStat({required this.title, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: Colors.white70),
            const SizedBox(width: 4),
            Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Colors.white)),
          ],
        ),
        const SizedBox(height: 2),
        Text(title, style: const TextStyle(fontSize: 11, color: Colors.white70)),
      ],
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final bool isRed;

  const _MenuItem({required this.icon, required this.title, required this.onTap, this.isRed = false});

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
