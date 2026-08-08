import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class BookingDetailScreen extends StatelessWidget {
  const BookingDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('b_o_o_k_i'.tr(context))),
      body: Center(child: Text('b_o_o_k_i'.tr(context))),
    );
  }
}
