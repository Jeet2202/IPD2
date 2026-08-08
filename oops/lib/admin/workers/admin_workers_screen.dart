import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminWorkersScreen extends StatelessWidget {
  const AdminWorkersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_workers_screen'.tr(context))),
      body: Center(child: Text('admin_workers_screen'.tr(context))),
    );
  }
}

