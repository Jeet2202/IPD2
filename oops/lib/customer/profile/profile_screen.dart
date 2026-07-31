// File:
// lib/customer/profile/profile_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
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
        title: const Text(
          'My Profile',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Color(0xFF0F172A)),
            onPressed: () => Navigator.pushNamed(context, AppRoutes.customerSettings),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              // ── Profile Card ──────────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 34,
                          backgroundColor: const Color(0xFFDBEAFE),
                          child: Text('RS', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: const Color(0xFF2563EB))),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  const Text('Rahul Sharma', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                                  const SizedBox(width: 6),
                                  const Icon(Icons.verified_rounded, color: Color(0xFF2563EB), size: 18),
                                ],
                              ),
                              const SizedBox(height: 2),
                              const Text('+91 98765 43210', style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                              const SizedBox(height: 2),
                              const Text('rahul.sharma@example.com', style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const Divider(color: Color(0xFFF1F5F9), height: 1),
                    const SizedBox(height: 16),

                    // Quick Stats
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _StatItem(title: 'Total Bookings', val: '24'),
                        _StatItem(title: 'Completed', val: '22'),
                        _StatItem(title: 'Saved', val: '₹3,450'),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Menu List ─────────────────────────────────────────────
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  children: [
                    _MenuItem(
                      icon: Icons.person_outline_rounded,
                      title: 'Edit Profile',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.editProfile),
                    ),
                    _MenuItem(
                      icon: Icons.location_on_outlined,
                      title: 'Saved Addresses',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.savedAddresses),
                    ),
                    _MenuItem(
                      icon: Icons.payment_rounded,
                      title: 'Payment Methods',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.paymentMethods),
                    ),
                    _MenuItem(
                      icon: Icons.account_balance_wallet_outlined,
                      title: 'KaamSetu Wallet & Cashbacks',
                      badge: '₹1,450',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.customerWallet),
                    ),
                    _MenuItem(
                      icon: Icons.card_giftcard_rounded,
                      title: 'Refer & Earn',
                      badge: 'Earn ₹200',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.referAndEarn),
                    ),
                    _MenuItem(
                      icon: Icons.notifications_none_rounded,
                      title: 'Notifications',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.notifications),
                    ),
                    _MenuItem(
                      icon: Icons.help_outline_rounded,
                      title: 'Help & Support',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.helpSupport),
                    ),
                    _MenuItem(
                      icon: Icons.lock_outline_rounded,
                      title: 'Privacy & Security',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.privacyPolicy),
                    ),
                    _MenuItem(
                      icon: Icons.info_outline_rounded,
                      title: 'About KaamSetu',
                      onTap: () => Navigator.pushNamed(context, AppRoutes.aboutUs),
                    ),
                    _MenuItem(
                      icon: Icons.logout_rounded,
                      title: 'Logout',
                      isRed: true,
                      onTap: () {
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
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: 3,
          onTap: (index) {
            if (index == 3) return;
            switch (index) {
              case 0:
                if (Navigator.canPop(context)) {
                  Navigator.pop(context);
                } else {
                  Navigator.pushReplacementNamed(context, AppRoutes.customerHome);
                }
                break;
              case 1:
                Navigator.pushReplacementNamed(context, AppRoutes.myBookings);
                break;
              case 2:
                Navigator.pushReplacementNamed(context, AppRoutes.helpSupport);
                break;
            }
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          selectedItemColor: const Color(0xFF2563EB),
          unselectedItemColor: const Color(0xFF94A3B8),
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
          unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w500, fontSize: 12),
          elevation: 0,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_rounded),
              label: 'Bookings',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.headset_mic_rounded),
              label: 'Support',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String title;
  final String val;

  const _StatItem({required this.title, required this.val});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(val, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
        const SizedBox(height: 2),
        Text(title, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
      ],
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? badge;
  final bool isRed;
  final VoidCallback onTap;

  const _MenuItem({
    required this.icon,
    required this.title,
    this.badge,
    this.isRed = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      leading: Icon(icon, color: isRed ? const Color(0xFFEF4444) : const Color(0xFF2563EB), size: 22),
      title: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          color: isRed ? const Color(0xFFEF4444) : const Color(0xFF0F172A),
        ),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (badge != null) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
              child: Text(badge!, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
            ),
            const SizedBox(width: 8),
          ],
          const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Color(0xFF94A3B8)),
        ],
      ),
    );
  }
}
