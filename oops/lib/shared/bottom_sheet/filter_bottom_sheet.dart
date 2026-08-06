import 'package:flutter/material.dart';
import '../../app/theme/app_dimensions.dart';

class FilterBottomSheet extends StatelessWidget {
  final String title;
  final Widget child;
  final VoidCallback? onApply;
  final VoidCallback? onReset;
  final String applyText;
  final String resetText;

  const FilterBottomSheet({
    super.key,
    this.title = 'Filter Options',
    required this.child,
    this.onApply,
    this.onReset,
    this.applyText = 'Apply Filters',
    this.resetText = 'Reset',
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      padding: EdgeInsets.only(
        top: 12,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
        left: 20,
        right: 20,
      ),
      decoration: BoxDecoration(
        color: theme.bottomSheetTheme.backgroundColor ?? colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(AppDimensions.radiusXl)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: theme.dividerColor,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: colorScheme.onSurface,
                ),
              ),
              if (onReset != null)
                TextButton(
                  onPressed: onReset,
                  child: Text(
                    resetText,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: colorScheme.primary,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Divider(height: 1, color: theme.dividerColor),
          const SizedBox(height: 16),

          // Main Filter Content
          Flexible(child: SingleChildScrollView(child: child)),

          if (onApply != null) ...[
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: AppDimensions.buttonHeight,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  onApply!();
                },
                child: Text(
                  applyText,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
