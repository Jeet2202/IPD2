import 'package:flutter/material.dart';

class EmptyStateWidget extends StatelessWidget {{
  const EmptyStateWidget({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('E m p t y S t a t e W i d g e t')),
      body: const Center(child: Text('E m p t y S t a t e W i d g e t')),
    );
  }}
}}
