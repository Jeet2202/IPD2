import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class UpcomingBookingsScreen extends StatelessWidget {
  const UpcomingBookingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('u_p_c_o_m'.tr(context))),
      body: Center(child: Text('u_p_c_o_m'.tr(context))),
    );
  }
}
