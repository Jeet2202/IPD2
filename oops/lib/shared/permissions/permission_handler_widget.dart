import 'package:flutter/material.dart';
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
    final colorScheme = Theme.of(context).colorScheme;
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(AppDimensions.lg),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: theme.dividerColor),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 48, color: colorScheme.primary),
          const SizedBox(height: AppDimensions.md),
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: AppDimensions.xs),
          Text(
            description,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13,
              color: colorScheme.onSurfaceVariant,
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
