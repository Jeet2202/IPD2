import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class HelpCenterScreen extends StatelessWidget {
  const HelpCenterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('h_e_l_p_c'.tr(context))),
      body: Center(child: Text('h_e_l_p_c'.tr(context))),
    );
  }
}
