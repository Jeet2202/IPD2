// File: lib/worker/widgets/worker_bottom_navigation_bar.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';

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
        Navigator.pushReplacementNamed(context, AppRoutes.workerWork);
        break;
      case 3:
        Navigator.pushReplacementNamed(context, AppRoutes.workerEarnings);
        break;
      case 4:
        Navigator.pushReplacementNamed(context, AppRoutes.workerProfile);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      selectedItemColor: AppColors.primary,
      unselectedItemColor: AppColors.slate400,
      type: BottomNavigationBarType.fixed,
      backgroundColor: AppColors.surface,
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
          icon: Icon(Icons.work_rounded),
          label: 'Work',
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
