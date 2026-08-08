import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class CategoriesScreen extends StatelessWidget {
  const CategoriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('c_a_t_e_g'.tr(context))),
      body: Center(child: Text('c_a_t_e_g'.tr(context))),
    );
  }
}
