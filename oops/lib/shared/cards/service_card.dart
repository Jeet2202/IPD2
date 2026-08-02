import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../widgets/app_card.dart';

class ServiceCard extends StatelessWidget {
  final String title;
  final String category;
  final String price;
  final String rating;
  final String? imageUrl;
  final String? duration;
  final String? shortDescription;
  final bool isFeatured;
  final IconData icon;
  final Color iconColor;
  final VoidCallback? onTap;
  final VoidCallback? onAdd;

  const ServiceCard({
    super.key,
    this.title = 'Deep House Cleaning',
    this.category = 'Cleaning',
    this.price = '₹1,499',
    this.rating = '4.8 (1.2k)',
    this.imageUrl,
    this.duration,
    this.shortDescription,
    this.isFeatured = false,
    this.icon = Icons.cleaning_services_rounded,
    this.iconColor = AppColors.primary,
    this.onTap,
    this.onAdd,
  });

  @override
  Widget build(BuildContext context) {
    return AppCard(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppDimensions.md),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          border: Border.all(color: AppColors.divider),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                  child: imageUrl != null && imageUrl!.isNotEmpty
                      ? Image.network(
                          imageUrl!,
                          width: 64,
                          height: 64,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => Container(
                            width: 64,
                            height: 64,
                            color: iconColor.withValues(alpha: 0.1),
                            child: Icon(icon, color: iconColor, size: 28),
                          ),
                        )
                      : Container(
                          width: 64,
                          height: 64,
                          color: iconColor.withValues(alpha: 0.1),
                          child: Icon(icon, color: iconColor, size: 28),
                        ),
                ),
                if (isFeatured)
                  Positioned(
                    top: 0,
                    left: 0,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF59E0B),
                        borderRadius: BorderRadius.only(
                          topLeft: Radius.circular(AppDimensions.radiusMd),
                          bottomRight: Radius.circular(AppDimensions.radiusSm),
                        ),
                      ),
                      child: const Text(
                        '★',
                        style: TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(width: AppDimensions.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          category.toUpperCase(),
                          style: const TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            color: AppColors.primary,
                            letterSpacing: 0.5,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (isFeatured) ...[
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEF3C7),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text(
                            'FEATURED',
                            style: TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFFD97706),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (shortDescription != null && shortDescription!.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Text(
                      shortDescription!,
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.star_rounded, color: AppColors.starRating, size: 14),
                      const SizedBox(width: 4),
                      Text(
                        rating,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      if (duration != null && duration!.isNotEmpty) ...[
                        const SizedBox(width: 8),
                        Text(
                          '• $duration',
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                      const Spacer(),
                      Text(
                        price,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                          color: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            if (onAdd != null) ...[
              const SizedBox(width: 10),
              ElevatedButton(
                onPressed: onAdd,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  minimumSize: const Size(64, 36),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
                  ),
                ),
                child: const Text('Add', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
