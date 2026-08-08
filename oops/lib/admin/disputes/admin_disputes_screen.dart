import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminDisputesScreen extends StatelessWidget {
  const AdminDisputesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_disputes_screen'.tr(context))),
      body: const Center(child: Text('admin_disputes_screen'.tr(context))),
    );
  }
}

