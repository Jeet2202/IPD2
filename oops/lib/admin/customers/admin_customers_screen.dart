import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminCustomersScreen extends StatelessWidget {
  const AdminCustomersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_customers_screen'.tr(context))),
      body: const Center(child: Text('admin_customers_screen'.tr(context))),
    );
  }
}

