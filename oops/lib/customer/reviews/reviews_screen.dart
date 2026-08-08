import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class ReviewsScreen extends StatelessWidget {
  const ReviewsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('r_e_v_i_e_2'.tr(context))),
      body: Center(child: Text('r_e_v_i_e_2'.tr(context))),
    );
  }
}
