import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class DocumentsScreen extends StatelessWidget {
  const DocumentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('d_o_c_u_m'.tr(context))),
      body: Center(child: Text('d_o_c_u_m'.tr(context))),
    );
  }
}
