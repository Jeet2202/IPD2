// File: lib/worker/dashboard/dashboard_screen.dart

import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';
import '../../widgets/language_selector_widget.dart';

class WorkerDashboardScreen extends StatefulWidget {
  const WorkerDashboardScreen({super.key});

  @override
  State<WorkerDashboardScreen> createState() => _WorkerDashboardScreenState();
}

class _WorkerDashboardScreenState extends State<WorkerDashboardScreen> {
  bool _isOnline = true;
  int _currentNavIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        automaticallyImplyLeading: false,
        title: Row(
          children: [
            Stack(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: const Color(0xFF2563EB).withOpacity(0.3),
                      width: 2,
                    ),
                  ),
                  child: const Center(
                    child: Icon(Icons.person_rounded,
                        color: Color(0xFF2563EB), size: 26),
                  ),
                ),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    width: 13,
                    height: 13,
                    decoration: BoxDecoration(
                      color: _isOnline
                          ? const Color(0xFF10B981)
                          : const Color(0xFF94A3B8),
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${'hello_worker'.tr(context)}, Ramesh',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          'electrician_pro'.tr(context),
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF2563EB),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          // Online Toggle Switch Header Button
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _isOnline ? const Color(0xFFD1FAE5) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Text(
                  _isOnline ? 'online'.tr(context) : 'offline'.tr(context),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: _isOnline
                        ? const Color(0xFF10B981)
                        : const Color(0xFF64748B),
                  ),
                ),
                const SizedBox(width: 4),
                Switch(
                  value: _isOnline,
                  activeColor: const Color(0xFF10B981),
                  inactiveThumbColor: const Color(0xFF64748B),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  onChanged: (val) {
                    setState(() {
                      _isOnline = val;
                    });
                  },
                ),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Today's Stats Cards Row
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      title: 'todays_earnings'.tr(context),
                      value: '₹ 2,450',
                      subtext: 'tips_subtext'.tr(context),
                      icon: Icons.account_balance_wallet_rounded,
                      color: const Color(0xFF2563EB),
                      bgGradient: const LinearGradient(
                        colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)],
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildStatCard(
                      title: 'jobs_completed'.tr(context),
                      value: 'jobs_value_count'.tr(context),
                      subtext: 'target_today'.tr(context),
                      icon: Icons.check_circle_rounded,
                      color: const Color(0xFF0EA5E9),
                      bgGradient: const LinearGradient(
                        colors: [Color(0xFF0EA5E9), Color(0xFF0284C7)],
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _buildMiniStatCard(
                      title: 'pending_requests'.tr(context),
                      value: 'new_requests_count'.tr(context),
                      icon: Icons.notifications_active_rounded,
                      iconColor: const Color(0xFFF59E0B),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMiniStatCard(
                      title: 'partner_rating'.tr(context),
                      value: '4.9 ★',
                      icon: Icons.star_rounded,
                      iconColor: const Color(0xFFF59E0B),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Quick Actions Grid
              Text(
                'quick_management'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 14),

              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 3,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 0.92,
                children: [
                  _buildQuickActionItem(
                    label: 'incoming_jobs'.tr(context),
                    icon: Icons.inbox_rounded,
                    badgeCount: 3,
                    color: const Color(0xFF2563EB),
                    onTap: () =>
                        Navigator.pushNamed(context, '/worker/jobs/incoming'),
                  ),
                  _buildQuickActionItem(
                    label: 'active_jobs'.tr(context),
                    icon: Icons.engineering_rounded,
                    badgeCount: 1,
                    color: const Color(0xFF0EA5E9),
                    onTap: () =>
                        Navigator.pushNamed(context, '/worker/jobs/active'),
                  ),
                  _buildQuickActionItem(
                    label: 'inspection_jobs'.tr(context),
                    icon: Icons.fact_check_rounded,
                    color: const Color(0xFF8B5CF6),
                    onTap: () =>
                        Navigator.pushNamed(context, '/worker/inspection/request'),
                  ),
                  _buildQuickActionItem(
                    label: 'earnings'.tr(context),
                    icon: Icons.payments_rounded,
                    color: const Color(0xFF10B981),
                    onTap: () =>
                        Navigator.pushReplacementNamed(context, '/worker/earnings/dashboard'),
                  ),
                  _buildQuickActionItem(
                    label: 'availability'.tr(context),
                    icon: Icons.calendar_month_rounded,
                    color: const Color(0xFFF59E0B),
                    onTap: () =>
                        Navigator.pushNamed(context, '/worker/profile/availability'),
                  ),
                  _buildQuickActionItem(
                    label: 'my_wallet'.tr(context),
                    icon: Icons.account_balance_wallet_rounded,
                    color: const Color(0xFFEC4899),
                    onTap: () =>
                        Navigator.pushNamed(context, '/worker/profile/bank-details'),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Weekly Earnings Chart Placeholder Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 16,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'weekly_performance'.tr(context),
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'weekly_total_text'.tr(context),
                              style: const TextStyle(
                                fontSize: 12,
                                color: Color(0xFF64748B),
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'vs_last_week'.tr(context),
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    // Dummy Bar Chart Representation
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        _buildChartBar('mon'.tr(context), 0.5),
                        _buildChartBar('tue'.tr(context), 0.75),
                        _buildChartBar('wed'.tr(context), 0.4),
                        _buildChartBar('thu'.tr(context), 0.9),
                        _buildChartBar('fri'.tr(context), 0.65),
                        _buildChartBar('sat'.tr(context), 0.95, isHigh: true),
                        _buildChartBar('sun'.tr(context), 0.8),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Recent Activity Feed
              Text(
                'recent_activity'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 12),

              _buildActivityTile(
                title: 'ac_maintenance_completed'.tr(context),
                customer: 'Anita Sharma • Saket',
                amount: '₹ 850',
                time: '1 hour ago',
                icon: Icons.check_circle_rounded,
                iconColor: const Color(0xFF10B981),
              ),
              const SizedBox(height: 10),
              _buildActivityTile(
                title: 'payout_transferred'.tr(context),
                customer: 'SBI A/C ending ...4321',
                amount: '₹ 3,200',
                time: 'Yesterday',
                icon: Icons.account_balance_rounded,
                iconColor: const Color(0xFF2563EB),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: const Color(0xFF2563EB),
        unselectedItemColor: const Color(0xFF94A3B8),
        type: BottomNavigationBarType.fixed,
        elevation: 12,
        onTap: (index) {
          if (index == 0) return;
          if (index == 1) {
            Navigator.pushNamed(context, '/worker/marketplace');
          } else if (index == 2) {
            Navigator.pushReplacementNamed(context, '/worker/jobs/incoming');
          } else if (index == 3) {
            Navigator.pushReplacementNamed(context, '/worker/earnings/dashboard');
          } else if (index == 4) {
            Navigator.pushReplacementNamed(context, '/worker/profile');
          }
        },
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.dashboard_rounded),
            label: 'home'.tr(context),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.storefront_rounded),
            label: 'marketplace'.tr(context),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.work_history_rounded),
            label: 'work'.tr(context),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.account_balance_wallet_rounded),
            label: 'earnings'.tr(context),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person_rounded),
            label: 'profile'.tr(context),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtext,
    required IconData icon,
    required Color color,
    required Gradient bgGradient,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: bgGradient,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.25),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.white.withOpacity(0.85),
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 4),
              Icon(icon, color: Colors.white.withOpacity(0.9), size: 20),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: Colors.white,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subtext,
            style: TextStyle(
              fontSize: 11,
              color: Colors.white.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMiniStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color iconColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF64748B),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionItem({
    required String label,
    required IconData icon,
    required Color color,
    int badgeCount = 0,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.03),
              blurRadius: 10,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: color, size: 22),
                ),
                const SizedBox(height: 6),
                Text(
                  label,
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF334155),
                  ),
                ),
              ],
            ),
            if (badgeCount > 0)
              Positioned(
                top: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 6, vertical: 2),
                  decoration: const BoxDecoration(
                    color: Color(0xFFEF4444),
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '$badgeCount',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildChartBar(String day, double heightFactor,
      {bool isHigh = false}) {
    return Column(
      children: [
        Container(
          height: 90 * heightFactor,
          width: 14,
          decoration: BoxDecoration(
            color: isHigh ? const Color(0xFF2563EB) : const Color(0xFF93C5FD),
            borderRadius: BorderRadius.circular(6),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          day,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isHigh ? FontWeight.w700 : FontWeight.w500,
            color: isHigh ? const Color(0xFF2563EB) : const Color(0xFF64748B),
          ),
        ),
      ],
    );
  }

  Widget _buildActivityTile({
    required String title,
    required String customer,
    required String amount,
    required String time,
    required IconData icon,
    required Color iconColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(width: 12),
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
                  customer,
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF64748B),
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                amount,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF10B981),
                ),
              ),
              const SizedBox(height: 2),
              Text(
                time,
                style: const TextStyle(
                  fontSize: 10,
                  color: Color(0xFF94A3B8),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
