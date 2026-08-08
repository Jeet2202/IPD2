import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminPaymentsScreen extends StatelessWidget {
  const AdminPaymentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_payments_screen'.tr(context))),
      body: const Center(child: Text('admin_payments_screen'.tr(context))),
    );
  }
}

