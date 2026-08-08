import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class SecurityScreen extends StatelessWidget {
  const SecurityScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('s_e_c_u_r'.tr(context))),
      body: Center(child: Text('s_e_c_u_r'.tr(context))),
    );
  }
}
