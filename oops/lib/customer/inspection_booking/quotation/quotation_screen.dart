import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class QuotationScreen extends StatelessWidget {
  const QuotationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('q_u_o_t_a'.tr(context))),
      body: Center(child: Text('q_u_o_t_a'.tr(context))),
    );
  }
}
