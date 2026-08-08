// File: lib/worker/profile/profile_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../services/auth_service.dart';
import '../../services/api_service.dart';
import '../../l10n/app_translations.dart';
import '../../widgets/language_selector_widget.dart';
import '../widgets/worker_bottom_navigation_bar.dart';
import 'service_area/service_area_screen.dart';

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
          _errorMessage = 'failed_load_profile_retry'.tr(context);
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
        return 'available_jobs'.tr(context);
      case 'on_job':
        return 'currently_on_job'.tr(context);
      case 'busy':
        return 'busy'.tr(context);
      case 'unavailable':
      default:
        return 'unavailable'.tr(context);
    }
  }

  String _getCompletionText(int percentage) {
    if (percentage >= 100) return 'profile_complete'.tr(context);
    if (percentage >= 70) return 'almost_complete'.tr(context);
    if (percentage >= 31) return 'keep_going'.tr(context);
    return 'getting_started'.tr(context);
  }

  List<String> _getSuggestions(Map<String, dynamic> data) {
    final suggestions = <String>[];
    if (data['profile_photo_url'] == null) suggestions.add('add_partner_photo_10'.tr(context));
    final bio = data['bio'] as String?;
    if (bio == null || bio.trim().length < 20) suggestions.add('write_detailed_bio_15'.tr(context));
    final skills = data['skills'] as List?;
    if (skills == null || skills.isEmpty) suggestions.add('add_skills_services_20'.tr(context));
    final exp = (data['experience_years'] as num?)?.toDouble() ?? 0.0;
    if (exp <= 0) suggestions.add('add_years_experience_10'.tr(context));
    final langs = data['languages'] as List?;
    if (langs == null || langs.isEmpty) suggestions.add('add_spoken_languages_10'.tr(context));
    final rate = (data['hourly_rate'] as num?)?.toDouble() ?? 0.0;
    if (rate <= 0) suggestions.add('set_hourly_rate_5'.tr(context));
    return suggestions;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        automaticallyImplyLeading: false,
        title: Text(
          'profile'.tr(context),
          style: const TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
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
                radius: 36,                backgroundImage: (photoUrl != null && photoUrl.isNotEmpty) ? NetworkImage(photoUrl) : null,
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
              _WorkerHeroStat(title: 'rating'.tr(context), value: rating > 0 ? rating.toStringAsFixed(1) : 'New', icon: Icons.star_rounded),
              _WorkerHeroStat(title: 'experience'.tr(context), value: '${expYears.toStringAsFixed(expYears.truncateToDouble() == expYears ? 0 : 1)} yrs', icon: Icons.work_history_rounded),
              _WorkerHeroStat(title: 'hourly_rate'.tr(context), value: hourlyRate != null && hourlyRate > 0 ? '₹${hourlyRate.toInt()}/hr' : 'flexible_rate'.tr(context), icon: Icons.payments_rounded),
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

    if (isCompleted || percentage >= 100) {
      return const SizedBox.shrink();
    }

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
              percentage >= 100
                  ? const SizedBox(
                      width: 50,
                      height: 50,
                      child: Icon(Icons.check_circle_rounded, color: Color(0xFF10B981), size: 50),
                    )
                  : Stack(
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
                      isCompleted ? 'profile_fully_verified'.tr(context) : 'complete_profile_rank_higher'.tr(context),
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
            Text(
              'suggestions_boost_ranking'.tr(context),
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
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
          Text('${radius.toInt()} ${'km_radius'.tr(context)}', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
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
          Text('offered_services_skills'.tr(context), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 12),
          skills.isNotEmpty
              ? Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: skills.map((s) => Chip(
                    label: Text(AppTranslations.getLocalizedName(context, s), style: const TextStyle(fontSize: 12, color: Color(0xFF1E40AF))),
                    backgroundColor: const Color(0xFFEFF6FF),
                    side: const BorderSide(color: Color(0xFFBFDBFE)),
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                  )).toList(),
                )
              : Text('no_skills_added'.tr(context), style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
          if (langs.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text('spoken_languages'.tr(context), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
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
    final bio = (data['bio'] as String?) ?? 'no_professional_bio'.tr(context);

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
          Text('professional_bio'.tr(context), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
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
            icon: Icons.language_rounded,
            title: 'select_language'.tr(context),
            subtitle: 'change_language'.tr(context),
            onTap: () => LanguageSelectorWidget.show(context),
          ),
          _MenuItem(
            icon: Icons.edit_note_rounded,
            title: 'edit_profile'.tr(context),
            onTap: () async {
              await Navigator.pushNamed(context, AppRoutes.workerEditProfile);
              _loadProfile();
            },
          ),
          _MenuItem(
            icon: Icons.location_on_rounded,
            title: 'service_area_location'.tr(context),
            subtitle: 'set_location_radius'.tr(context),
            onTap: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const WorkerServiceAreaScreen()),
              );
              _loadProfile(); // Refresh profile to show updated radius
            },
          ),
          _MenuItem(
            icon: Icons.lock_reset_rounded,
            title: 'change_password'.tr(context),
            onTap: () => Navigator.pushNamed(context, '/worker/settings'),
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
            Text('failed_load_profile'.tr(context), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
            const SizedBox(height: 8),
            Text(_errorMessage ?? 'network_error'.tr(context), textAlign: TextAlign.center, style: const TextStyle(fontSize: 13, color: Color(0xFF64748B))),
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
                Navigator.pushNamedAndRemoveUntil(context, AppRoutes.workerLogin, (route) => false);
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
  final String? subtitle;
  final VoidCallback onTap;
  final bool isRed;

  const _MenuItem({required this.icon, required this.title, required this.onTap, this.subtitle, this.isRed = false});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF475569)),
      title: Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF0F172A))),
      subtitle: subtitle != null ? Text(subtitle!, style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8))) : null,
      trailing: const Icon(Icons.chevron_right_rounded, color: Color(0xFF94A3B8)),
      onTap: onTap,
    );
  }
}
