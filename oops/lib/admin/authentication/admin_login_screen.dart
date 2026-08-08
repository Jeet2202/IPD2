import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminLoginScreen extends StatelessWidget {
  const AdminLoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_login_screen'.tr(context))),
      body: Center(child: Text('admin_login_screen'.tr(context))),
    );
  }
}

