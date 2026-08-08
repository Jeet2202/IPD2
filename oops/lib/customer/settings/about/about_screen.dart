import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('a_b_o_u_t'.tr(context))),
      body: Center(child: Text('a_b_o_u_t'.tr(context))),
    );
  }
}
