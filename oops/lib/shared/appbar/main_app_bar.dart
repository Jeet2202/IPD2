import 'package:flutter/material.dart';

class MainAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Widget? leading;
  final bool centerTitle;

  const MainAppBar({
    super.key,
    required this.title,
    this.actions,
    this.leading,
    this.centerTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    final canPop = Navigator.canPop(context);
    final theme = Theme.of(context);

    return AppBar(
      title: Text(
        title,
        style: theme.appBarTheme.titleTextStyle,
      ),
      centerTitle: centerTitle,
      backgroundColor: theme.appBarTheme.backgroundColor,
      elevation: 0,
      scrolledUnderElevation: 0,
      leading: leading ??
          (canPop
              ? IconButton(
                  icon: Icon(
                    Icons.arrow_back_rounded,
                    color: theme.appBarTheme.iconTheme?.color,
                  ),
                  onPressed: () => Navigator.pop(context),
                )
              : null),
      actions: actions,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
