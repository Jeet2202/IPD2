import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../app/theme/app_colors.dart';
import '../app/theme/app_dimensions.dart';

enum AppButtonVariant { primary, secondary, outline, text, danger }

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool outlined;
  final AppButtonVariant variant;
  final Color? color;
  final double? width;
  final double? height;
  final IconData? icon;
  final bool enableHaptic;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.isLoading = false,
    this.outlined = false,
    this.variant = AppButtonVariant.primary,
    this.color,
    this.width,
    this.height,
    this.icon,
    this.enableHaptic = true,
  });

  void _handlePress() {
    if (isLoading || onPressed == null) return;
    if (enableHaptic) {
      HapticFeedback.lightImpact();
    }
    onPressed!();
  }

  @override
  Widget build(BuildContext context) {
    final bool isOutlined = outlined || variant == AppButtonVariant.outline;
    final bool isText = variant == AppButtonVariant.text;

    Color bg = color ?? AppColors.primary;
    Color fg = Colors.white;

    switch (variant) {
      case AppButtonVariant.primary:
        bg = color ?? AppColors.primary;
        fg = Colors.white;
        break;
      case AppButtonVariant.secondary:
        bg = color ?? AppColors.secondary;
        fg = Colors.white;
        break;
      case AppButtonVariant.outline:
        bg = color ?? AppColors.primary;
        fg = bg;
        break;
      case AppButtonVariant.text:
        bg = Colors.transparent;
        fg = color ?? AppColors.primary;
        break;
      case AppButtonVariant.danger:
        bg = color ?? AppColors.error;
        fg = Colors.white;
        break;
    }

    if (outlined) {
      fg = bg;
    }

    Widget child = isLoading
        ? SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: (isOutlined || isText) ? fg : Colors.white,
            ),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[Icon(icon, size: 20), const SizedBox(width: 8)],
              Flexible(
                child: Text(
                  label,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: (isOutlined || isText) ? fg : fg,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          );

    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
    );

    final double btnHeight = height ?? AppDimensions.buttonHeight;

    if (isText) {
      return SizedBox(
        width: width,
        height: btnHeight,
        child: TextButton(
          onPressed: (isLoading || onPressed == null) ? null : _handlePress,
          style: TextButton.styleFrom(
            foregroundColor: fg,
            shape: shape,
          ),
          child: child,
        ),
      );
    }

    return SizedBox(
      width: width ?? double.infinity,
      height: btnHeight,
      child: isOutlined
          ? OutlinedButton(
              onPressed: (isLoading || onPressed == null) ? null : _handlePress,
              style: OutlinedButton.styleFrom(
                foregroundColor: fg,
                side: BorderSide(color: bg, width: 1.5),
                shape: shape,
              ),
              child: child,
            )
          : ElevatedButton(
              onPressed: (isLoading || onPressed == null) ? null : _handlePress,
              style: ElevatedButton.styleFrom(
                backgroundColor: bg,
                foregroundColor: fg,
                shape: shape,
                elevation: 0,
              ),
              child: child,
            ),
    );
  }
}

