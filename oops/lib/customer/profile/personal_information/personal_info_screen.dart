import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class PersonalInfoScreen extends StatelessWidget {
  const PersonalInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('p_e_r_s_o'.tr(context))),
      body: Center(child: Text('p_e_r_s_o'.tr(context))),
    );
  }
}
