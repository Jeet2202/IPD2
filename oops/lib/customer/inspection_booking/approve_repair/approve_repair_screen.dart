import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class ApproveRepairScreen extends StatelessWidget {
  const ApproveRepairScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('a_p_p_r_o'.tr(context))),
      body: Center(child: Text('a_p_p_r_o'.tr(context))),
    );
  }
}
