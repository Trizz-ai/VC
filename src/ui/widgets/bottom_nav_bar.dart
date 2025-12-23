import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../theme/app_colors.dart';

/// Consistent bottom navigation bar used across all main screens
class VCBottomNavBar extends StatelessWidget {
  final int? currentIndex;
  final String? currentRoute;

  const VCBottomNavBar({
    Key? key,
    this.currentIndex,
    this.currentRoute,
  }) : super(key: key);

  int _getCurrentIndex(BuildContext context) {
    // Use provided index if available
    if (currentIndex != null) return currentIndex!;
    
    // Otherwise, detect from GoRouter
    final location = GoRouterState.of(context).matchedLocation;
    return getIndexForRoute(location);
  }

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: _getCurrentIndex(context),
      type: BottomNavigationBarType.fixed,
      backgroundColor: AppColors.surface,
      selectedItemColor: AppColors.primary,
      unselectedItemColor: AppColors.textSecondary,
      selectedFontSize: 12,
      unselectedFontSize: 12,
      onTap: (index) {
        debugPrint('Bottom nav bar tapped: index=$index');
        try {
          switch (index) {
            case 0:
              debugPrint('Navigating to /dashboard');
              context.go('/dashboard');
              break;
            case 1:
              debugPrint('Navigating to /meetings/finder');
              context.go('/meetings/finder');
              break;
            case 2:
              debugPrint('Navigating to /logs/personal');
              context.go('/logs/personal');
              break;
            case 3:
              debugPrint('Navigating to /profile');
              context.go('/profile');
              break;
          }
        } catch (e, stackTrace) {
          debugPrint('Navigation error: $e');
          debugPrint('Stack trace: $stackTrace');
        }
      },
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.groups),
          label: 'Meetings',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.description),
          label: 'Logs',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person),
          label: 'Profile',
        ),
      ],
    );
  }

  /// Get the current index based on route
  static int getIndexForRoute(String route) {
    if (route.startsWith('/dashboard')) return 0;
    if (route.startsWith('/meetings')) return 1;
    if (route.startsWith('/logs') || route.startsWith('/sessions')) return 2;
    if (route.startsWith('/profile')) return 3;
    return 0; // Default to home
  }
}

