import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class ActiveBookingsScreen extends StatelessWidget {
  const ActiveBookingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('a_c_t_i_v'.tr(context))),
      body: Center(child: Text('a_c_t_i_v'.tr(context))),
    );
  }
}
