import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class PreferencesScreen extends StatelessWidget {
  const PreferencesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('p_r_e_f_e'.tr(context))),
      body: Center(child: Text('p_r_e_f_e'.tr(context))),
    );
  }
}
