import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/routes/app_routes.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool showBackButton;
  final VoidCallback? onBackPressed;
  final PreferredSizeWidget? bottom;
  final Color? backgroundColor;

  const CustomAppBar({
    super.key,
    required this.title,
    this.actions,
    this.showBackButton = true,
    this.onBackPressed,
    this.bottom,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: AppColors.textPrimary,
        ),
      ),
      centerTitle: true,
      backgroundColor: backgroundColor ?? Colors.white,
      elevation: 0,
      scrolledUnderElevation: 0,
      leading: showBackButton
          ? IconButton(
              icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20, color: AppColors.textPrimary),
              onPressed: onBackPressed ?? () {
                if (Navigator.canPop(context)) {
                  Navigator.pop(context);
                } else {
                  Navigator.pushReplacementNamed(context, AppRoutes.roleSelection);
                }
              },
            )
          : null,
      actions: actions,
      bottom: bottom,
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(kToolbarHeight + (bottom?.preferredSize.height ?? 0));
}

