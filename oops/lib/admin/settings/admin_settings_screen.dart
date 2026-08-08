import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminSettingsScreen extends StatelessWidget {
  const AdminSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_settings_screen'.tr(context))),
      body: const Center(child: Text('admin_settings_screen'.tr(context))),
    );
  }
}

