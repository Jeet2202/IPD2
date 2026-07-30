import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget {{
  const CustomAppBar({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('C u s t o m A p p B a r')),
      body: const Center(child: Text('C u s t o m A p p B a r')),
    );
  }}
}}
