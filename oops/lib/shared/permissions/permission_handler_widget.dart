import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../widgets/app_button.dart';

class PermissionHandlerWidget extends StatelessWidget {
  final String title;
  final String description;
  final IconData icon;
  final VoidCallback onRequestPermission;

  const PermissionHandlerWidget({
    super.key,
    this.title = 'Permission Required',
    this.description = 'Please grant permission to access this feature.',
    this.icon = Icons.security_rounded,
    required this.onRequestPermission,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: AppColors.primary),
          const SizedBox(height: AppDimensions.md),
          Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: AppDimensions.xs),
          Text(
            description,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 13,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppDimensions.md),
          AppButton(
            label: 'Allow Permission',
            onPressed: onRequestPermission,
          ),
        ],
      ),
    );
  }
}
