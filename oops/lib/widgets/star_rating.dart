import 'package:flutter/material.dart';
import '../app/theme/app_colors.dart';
import '../app/theme/app_dimensions.dart';

class StarRating extends StatelessWidget {
  final double rating;
  final double size;
  final int maxStars;

  const StarRating({
    super.key,
    required this.rating,
    this.size = 18,
    this.maxStars = 5,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(maxStars, (i) {
        final filled = i < rating.floor();
        final half   = !filled && i < rating;
        return Icon(
          filled ? Icons.star : half ? Icons.star_half : Icons.star_border,
          color: AppColors.starRating,
          size: size,
        );
      }),
    );
  }
}
