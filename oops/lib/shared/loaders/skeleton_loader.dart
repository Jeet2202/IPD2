import 'package:flutter/material.dart';
import '../../widgets/app_shimmer.dart';

class SkeletonLoader extends StatelessWidget {
  final int count;
  final double height;
  final double borderRadius;

  const SkeletonLoader({
    super.key,
    this.count = 3,
    this.height = 80,
    this.borderRadius = 12,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: count,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, __) => AppShimmer(
        width: double.infinity,
        height: height,
        borderRadius: borderRadius,
      ),
    );
  }
}
