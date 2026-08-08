import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class FaqScreen extends StatelessWidget {
  const FaqScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('f_a_q_s_c'.tr(context))),
      body: Center(child: Text('f_a_q_s_c'.tr(context))),
    );
  }
}
