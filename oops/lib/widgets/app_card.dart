// File: lib/widgets/app_card.dart

import 'package:flutter/material.dart';
import '../app/theme/app_colors.dart';
import '../app/theme/app_dimensions.dart';

enum AppCardVariant { defaultSurface, outlined, elevated, highlighted }

class AppCard extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Color? color;
  final Color? borderColor;
  final double? borderRadius;
  final AppCardVariant variant;

  const AppCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding,
    this.margin,
    this.color,
    this.borderColor,
    this.borderRadius,
    this.variant = AppCardVariant.defaultSurface,
  });

  @override
  Widget build(BuildContext context) {
    Color bg = color ?? AppColors.surface;
    Color border = borderColor ?? AppColors.cardBorder;
    List<BoxShadow>? shadows;

    switch (variant) {
      case AppCardVariant.defaultSurface:
        shadows = [
          BoxShadow(
            color: AppColors.cardShadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ];
        break;
      case AppCardVariant.outlined:
        shadows = null;
        break;
      case AppCardVariant.elevated:
        shadows = [
          BoxShadow(
            color: AppColors.cardShadow,
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ];
        break;
      case AppCardVariant.highlighted:
        bg = AppColors.primarySurface;
        border = AppColors.primary.withValues(alpha: 0.3);
        shadows = null;
        break;
    }

    final radius = BorderRadius.circular(borderRadius ?? AppDimensions.radiusLg);

    final cardContent = Container(
      margin: margin ?? EdgeInsets.zero,
      padding: padding ?? const EdgeInsets.all(AppDimensions.md),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: radius,
        border: Border.all(color: border, width: 1),
        boxShadow: shadows,
      ),
      child: child,
    );

    if (onTap != null) {
      return Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: radius,
          child: cardContent,
        ),
      );
    }

    return cardContent;
  }
}
