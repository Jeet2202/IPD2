import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminQuotationsScreen extends StatelessWidget {
  const AdminQuotationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_quotations_screen'.tr(context))),
      body: Center(child: Text('admin_quotations_screen'.tr(context))),
    );
  }
}

