import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class LanguageScreen extends StatelessWidget {
  const LanguageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('l_a_n_g_u'.tr(context))),
      body: Center(child: Text('l_a_n_g_u'.tr(context))),
    );
  }
}
