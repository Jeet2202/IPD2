import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class ProfessionalAssignedScreen extends StatelessWidget {
  const ProfessionalAssignedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('p_r_o_f_e'.tr(context))),
      body: Center(child: Text('p_r_o_f_e'.tr(context))),
    );
  }
}
