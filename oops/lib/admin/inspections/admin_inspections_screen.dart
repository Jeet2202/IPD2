import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminInspectionsScreen extends StatelessWidget {
  const AdminInspectionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_inspections_screen'.tr(context))),
      body: Center(child: Text('admin_inspections_screen'.tr(context))),
    );
  }
}

