import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class UploadImagesScreen extends StatelessWidget {
  const UploadImagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('u_p_l_o_a'.tr(context))),
      body: Center(child: Text('u_p_l_o_a'.tr(context))),
    );
  }
}
