import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminServicesScreen extends StatelessWidget {
  const AdminServicesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_services_screen'.tr(context))),
      body: const Center(child: Text('admin_services_screen'.tr(context))),
    );
  }
}

