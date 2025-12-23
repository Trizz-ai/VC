import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import 'home_button.dart';

/// Consistent AppBar with home button and navigation
class VCAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool showHomeButton;
  final bool showDrawer;
  final bool showBackButton;
  final bool showSettingsButton;
  final VoidCallback? onDrawerPressed;

  const VCAppBar({
    Key? key,
    required this.title,
    this.actions,
    this.showHomeButton = true,
    this.showDrawer = true,
    this.showBackButton = true,
    this.showSettingsButton = true,
    this.onDrawerPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final List<Widget> appBarActions = [];

    // Add settings button (always first in actions, top right)
    if (showSettingsButton) {
      appBarActions.add(
        IconButton(
          icon: const Icon(Icons.settings),
          tooltip: 'Settings',
          color: AppColors.textPrimary,
          onPressed: () {
            context.go('/settings');
          },
        ),
      );
    }

    // Add custom actions after settings button
    if (actions != null) {
      appBarActions.addAll(actions!);
    }

    // Build leading widget with back, home, and optionally drawer
    Widget? leadingWidget;
    int buttonCount = 0;
    if (showDrawer) buttonCount++;
    if (showBackButton) buttonCount++;
    if (showHomeButton) buttonCount++;
    
    final double leadingWidth = buttonCount * 48.0; // 48px per button
    
    if (showDrawer) {
      // Show drawer button, back button, and home button
      leadingWidget = SizedBox(
        width: leadingWidth,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Drawer button - use Builder to ensure correct Scaffold context
            Builder(
              builder: (builderContext) {
                return IconButton(
                  icon: const Icon(Icons.menu),
                  padding: const EdgeInsets.all(12),
                  constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                  onPressed: onDrawerPressed ?? () {
                    // Use the Builder's context to find the Scaffold
                    final scaffoldState = Scaffold.maybeOf(builderContext);
                    if (scaffoldState != null && scaffoldState.hasDrawer) {
                      scaffoldState.openDrawer();
                    } else {
                      // Fallback: try Scaffold.of with error handling
                      try {
                        final scaffold = Scaffold.of(builderContext);
                        if (scaffold.hasDrawer) {
                          scaffold.openDrawer();
                        }
                      } catch (e) {
                        debugPrint('Error opening drawer: $e');
                      }
                    }
                  },
                );
              },
            ),
            // Back button
            if (showBackButton)
              IconButton(
                icon: const Icon(Icons.arrow_back),
                padding: const EdgeInsets.all(12),
                constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                onPressed: () {
                  if (Navigator.of(context).canPop()) {
                    context.pop();
                  } else {
                    context.go('/dashboard');
                  }
                },
              ),
            // Home button
            if (showHomeButton)
              IconButton(
                icon: const Icon(Icons.home, size: 24),
                tooltip: 'Go to Dashboard',
                padding: const EdgeInsets.all(12),
                constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                color: AppColors.textPrimary,
                onPressed: () {
                  context.go('/dashboard');
                },
              ),
          ],
        ),
      );
    } else {
      // Show back and home buttons only
      leadingWidget = SizedBox(
        width: leadingWidth,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Back button
            if (showBackButton)
              IconButton(
                icon: const Icon(Icons.arrow_back),
                padding: const EdgeInsets.all(12),
                constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                onPressed: () {
                  if (Navigator.of(context).canPop()) {
                    context.pop();
                  } else {
                    context.go('/dashboard');
                  }
                },
              ),
            // Home button
            if (showHomeButton)
              IconButton(
                icon: const Icon(Icons.home, size: 24),
                tooltip: 'Go to Dashboard',
                padding: const EdgeInsets.all(12),
                constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                color: AppColors.textPrimary,
                onPressed: () {
                  context.go('/dashboard');
                },
              ),
          ],
        ),
      );
    }

    return AppBar(
      backgroundColor: AppColors.surface,
      elevation: 0,
      automaticallyImplyLeading: false, // We handle leading manually
      leading: leadingWidget,
      leadingWidth: leadingWidth,
      title: Text(
        title,
        style: AppTextStyles.h6,
      ),
      actions: appBarActions,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

