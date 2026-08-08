import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class AddressScreen extends StatelessWidget {
  const AddressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('a_d_d_r_e'.tr(context))),
      body: Center(child: Text('a_d_d_r_e'.tr(context))),
    );
  }
}
