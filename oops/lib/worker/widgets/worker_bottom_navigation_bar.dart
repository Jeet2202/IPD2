// File: lib/worker/widgets/worker_bottom_navigation_bar.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';

class WorkerBottomNavigationBar extends StatelessWidget {
  final int currentIndex;

  const WorkerBottomNavigationBar({
    super.key,
    required this.currentIndex,
  });

  void _onTabTapped(BuildContext context, int index) {
    if (index == currentIndex) return;

    switch (index) {
      case 0:
        Navigator.pushReplacementNamed(context, AppRoutes.workerDashboard);
        break;
      case 1:
        Navigator.pushReplacementNamed(context, AppRoutes.workerMarketplace);
        break;
      case 2:
        Navigator.pushReplacementNamed(context, AppRoutes.workerEarnings);
        break;
      case 3:
        Navigator.pushReplacementNamed(context, AppRoutes.workerProfile);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      selectedItemColor: const Color(0xFF2563EB),
      unselectedItemColor: const Color(0xFF94A3B8),
      type: BottomNavigationBarType.fixed,
      backgroundColor: Colors.white,
      elevation: 12,
      onTap: (index) => _onTabTapped(context, index),
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.dashboard_rounded),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.storefront_rounded),
          label: 'Marketplace',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.account_balance_wallet_rounded),
          label: 'Earnings',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person_rounded),
          label: 'Profile',
        ),
      ],
    );
  }
}
