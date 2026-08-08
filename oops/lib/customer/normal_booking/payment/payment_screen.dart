import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class PaymentScreen extends StatelessWidget {
  const PaymentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('p_a_y_m_e'.tr(context))),
      body: Center(child: Text('p_a_y_m_e'.tr(context))),
    );
  }
}
