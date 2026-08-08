import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_dashboard_screen'.tr(context))),
      body: const Center(child: Text('admin_dashboard_screen'.tr(context))),
    );
  }
}

