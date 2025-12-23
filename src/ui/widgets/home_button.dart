import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../theme/app_colors.dart';

/// A reusable home button widget for AppBar actions
class HomeButton extends StatelessWidget {
  const HomeButton({super.key});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.home, size: 24),
      tooltip: 'Go to Dashboard',
      color: AppColors.textPrimary,
      onPressed: () {
        context.go('/dashboard');
      },
    );
  }
}

