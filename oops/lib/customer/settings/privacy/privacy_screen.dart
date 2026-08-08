import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('p_r_i_v_a'.tr(context))),
      body: Center(child: Text('p_r_i_v_a'.tr(context))),
    );
  }
}
