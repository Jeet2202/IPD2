import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminCategoriesScreen extends StatelessWidget {
  const AdminCategoriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_categories_screen'.tr(context))),
      body: Center(child: Text('admin_categories_screen'.tr(context))),
    );
  }
}

