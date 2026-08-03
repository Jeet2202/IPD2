// File: lib/widgets/review_display_card.dart

import 'package:flutter/material.dart';
import '../models/review_model.dart';

class ReviewDisplayCard extends StatelessWidget {
  final ReviewModel review;
  final String titleText;

  const ReviewDisplayCard({
    super.key,
    required this.review,
    this.titleText = 'Customer Rating & Review',
  });

  Widget _buildStarRow(double rating, {double size = 18}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (index) {
        final starVal = index + 1;
        IconData icon;
        Color color;
        if (rating >= starVal) {
          icon = Icons.star_rounded;
          color = Colors.amber.shade700;
        } else if (rating >= starVal - 0.5) {
          icon = Icons.star_half_rounded;
          color = Colors.amber.shade700;
        } else {
          icon = Icons.star_outline_rounded;
          color = Colors.amber.shade200;
        }
        return Icon(icon, color: color, size: size);
      }),
    );
  }

  Widget _buildMetricChip(String label, double val) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFBEB),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFFDE68A)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '$label: ',
            style: const TextStyle(fontSize: 11, color: Color(0xFF78350F), fontWeight: FontWeight.w600),
          ),
          Text(
            val.toStringAsFixed(1),
            style: const TextStyle(fontSize: 11, color: Color(0xFF92400E), fontWeight: FontWeight.w900),
          ),
          const SizedBox(width: 2),
          const Icon(Icons.star_rounded, size: 12, color: Colors.amber),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFFCD34D), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF3C7),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(Icons.stars_rounded, color: Colors.amber.shade800, size: 22),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    titleText,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.amber.shade300),
                ),
                child: Row(
                  children: [
                    Text(
                      review.overallRating.toStringAsFixed(1),
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w900,
                        color: Colors.amber.shade900,
                      ),
                    ),
                    const SizedBox(width: 3),
                    Icon(Icons.star_rounded, size: 16, color: Colors.amber.shade700),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Overall Stars
          Row(
            children: [
              _buildStarRow(review.overallRating, size: 22),
              const SizedBox(width: 10),
              if (review.wouldRecommend)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: const Color(0xFFA7F3D0)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.thumb_up_rounded, size: 12, color: Color(0xFF059669)),
                      SizedBox(width: 4),
                      Text(
                        'Recommended',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 14),

          // Rating Breakdown Chips
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              _buildMetricChip('Punctuality', review.punctualityRating),
              _buildMetricChip('Quality', review.qualityRating),
              _buildMetricChip('Professionalism', review.professionalismRating),
              _buildMetricChip('Communication', review.communicationRating),
            ],
          ),

          // Review Title & Comment
          if (review.reviewTitle != null && review.reviewTitle!.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              review.reviewTitle!,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
          ],

          if (review.reviewComment != null && review.reviewComment!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              '"${review.reviewComment!}"',
              style: const TextStyle(
                fontSize: 13,
                fontStyle: FontStyle.italic,
                color: Color(0xFF334155),
                height: 1.4,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
