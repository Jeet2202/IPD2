import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class ReviewScreen extends StatelessWidget {
  const ReviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('r_e_v_i_e'.tr(context))),
      body: Center(child: Text('r_e_v_i_e'.tr(context))),
    );
  }
}
