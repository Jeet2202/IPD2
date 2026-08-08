import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminNotificationsScreen extends StatelessWidget {
  const AdminNotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_notifications_screen'.tr(context))),
      body: const Center(child: Text('admin_notifications_screen'.tr(context))),
    );
  }
}

