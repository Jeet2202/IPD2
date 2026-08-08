import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class NotificationSettingsScreen extends StatelessWidget {
  const NotificationSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('n_o_t_i_f'.tr(context))),
      body: Center(child: Text('n_o_t_i_f'.tr(context))),
    );
  }
}
