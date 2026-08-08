import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminCmsScreen extends StatelessWidget {
  const AdminCmsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_cms_screen'.tr(context))),
      body: const Center(child: Text('admin_cms_screen'.tr(context))),
    );
  }
}

