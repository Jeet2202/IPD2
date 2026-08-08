import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class LogoutScreen extends StatelessWidget {
  const LogoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('l_o_g_o_u'.tr(context))),
      body: Center(child: Text('l_o_g_o_u'.tr(context))),
    );
  }
}
