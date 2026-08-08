import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class InspectionTrackingScreen extends StatelessWidget {
  const InspectionTrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('i_n_s_p_e_2'.tr(context))),
      body: Center(child: Text('i_n_s_p_e_2'.tr(context))),
    );
  }
}
