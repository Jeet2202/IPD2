import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class CustomerWalletScreen extends StatelessWidget {
  const CustomerWalletScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('c_u_s_t_o'.tr(context))),
      body: Center(child: Text('c_u_s_t_o'.tr(context))),
    );
  }
}
