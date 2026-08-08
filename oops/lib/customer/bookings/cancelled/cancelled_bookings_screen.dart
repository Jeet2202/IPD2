import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class CancelledBookingsScreen extends StatelessWidget {
  const CancelledBookingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('c_a_n_c_e'.tr(context))),
      body: Center(child: Text('c_a_n_c_e'.tr(context))),
    );
  }
}
