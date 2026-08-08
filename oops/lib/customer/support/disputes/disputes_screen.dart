import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class DisputesScreen extends StatelessWidget {
  const DisputesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('d_i_s_p_u'.tr(context))),
      body: Center(child: Text('d_i_s_p_u'.tr(context))),
    );
  }
}
