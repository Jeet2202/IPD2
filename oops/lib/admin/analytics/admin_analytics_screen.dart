import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class AdminAnalyticsScreen extends StatelessWidget {
  const AdminAnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('admin_analytics_screen'.tr(context))),
      body: const Center(child: Text('admin_analytics_screen'.tr(context))),
    );
  }
}

