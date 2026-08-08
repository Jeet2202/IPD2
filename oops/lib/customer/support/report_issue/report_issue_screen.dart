import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class ReportIssueScreen extends StatelessWidget {
  const ReportIssueScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('r_e_p_o_r'.tr(context))),
      body: Center(child: Text('r_e_p_o_r'.tr(context))),
    );
  }
}
