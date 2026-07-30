import 'package:flutter/material.dart';

class MainAppBar extends StatelessWidget {{
  const MainAppBar({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('M a i n A p p B a r')),
      body: const Center(child: Text('M a i n A p p B a r')),
    );
  }}
}}
