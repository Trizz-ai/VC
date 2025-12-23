import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../../../../frontend/lib/features/auth/providers/auth_provider.dart';

/// Navigation drawer with menu items
class VCNavigationDrawer extends StatelessWidget {
  const VCNavigationDrawer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppColors.surface,
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              color: AppColors.primary,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Text(
                  'Verified Compliance',
                  style: AppTextStyles.h4.copyWith(
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Consumer<AuthProvider>(
                  builder: (context, authProvider, _) {
                    final user = authProvider.user;
                    if (user != null) {
                      return Text(
                        user.email ?? 'User',
                        style: AppTextStyles.body2.copyWith(
                          color: Colors.white70,
                        ),
                      );
                    }
                    return const SizedBox.shrink();
                  },
                ),
              ],
            ),
          ),
          _buildDrawerItem(
            context,
            icon: Icons.home,
            title: 'Dashboard',
            route: '/dashboard',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.groups,
            title: 'Find Meetings',
            route: '/meetings/finder',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.description,
            title: 'Personal Logs',
            route: '/logs/personal',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.verified,
            title: 'Compliance Journey',
            route: '/compliance',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.check_circle,
            title: 'Verified Compliance',
            route: '/verified-compliance',
          ),
          const Divider(),
          _buildDrawerItem(
            context,
            icon: Icons.smart_toy,
            title: 'AI Assistant',
            route: '/ai-assistant',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.gavel,
            title: 'AI Legal Assistant',
            route: '/ai-legal-assistant',
          ),
          const Divider(),
          _buildDrawerItem(
            context,
            icon: Icons.subscriptions,
            title: 'Subscription',
            route: '/subscription',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.person,
            title: 'Profile',
            route: '/profile',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.settings,
            title: 'Settings',
            route: '/settings',
          ),
          _buildDrawerItem(
            context,
            icon: Icons.help_outline,
            title: 'Help',
            route: '/help',
          ),
          const Divider(),
          _buildDrawerItem(
            context,
            icon: Icons.logout,
            title: 'Logout',
            route: null,
            onTap: () async {
              final authProvider = context.read<AuthProvider>();
              await authProvider.logout();
              if (context.mounted) {
                context.go('/login');
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    String? route,
    VoidCallback? onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: AppColors.textPrimary),
      title: Text(
        title,
        style: AppTextStyles.body1,
      ),
      onTap: onTap ??
          () {
            Navigator.pop(context);
            if (route != null) {
              context.go(route);
            }
          },
    );
  }
}

