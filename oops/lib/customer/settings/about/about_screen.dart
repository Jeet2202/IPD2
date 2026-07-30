import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('A b o u t S c r e e n')),
      body: const Center(child: Text('A b o u t S c r e e n')),
    );
  }
}
