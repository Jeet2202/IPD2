import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class CompletedBookingsScreen extends StatelessWidget {
  const CompletedBookingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('c_o_m_p_l'.tr(context))),
      body: Center(child: Text('c_o_m_p_l'.tr(context))),
    );
  }
}
