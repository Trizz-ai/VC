import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/vc_button.dart';
import '../../widgets/vc_card.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/core/services/location_service.dart';

/// Main dashboard screen with session timer and GPS tracking
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);
  
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    // Load active session on mount
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<SessionProvider>(context, listen: false).loadActiveSession();
    });
  }
  
  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final hours = twoDigits(duration.inHours);
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$hours:$minutes:$seconds';
  }
  
  Duration _calculateSessionDuration(Session? session) {
    if (session == null || session.checkInTime == null) {
      return Duration.zero;
    }
    
    final checkInTime = session.checkInTime!;
    final now = DateTime.now();
    return now.difference(checkInTime);
  }
  
  @override
  Widget build(BuildContext context) {
    final locationService = Provider.of<LocationService>(context, listen: false);
    
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () {
            // TODO: Open drawer
          },
        ),
        title: const Text('Verified Compliance'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final authProvider = Provider.of<AuthProvider>(context, listen: false);
              await authProvider.logout();
              if (mounted) {
                context.go('/login');
              }
            },
          ),
        ],
      ),
      body: Consumer<SessionProvider>(
        builder: (context, sessionProvider, _) {
          final activeSession = sessionProvider.activeSession;
          final sessionDuration = _calculateSessionDuration(activeSession);
          final currentLocation = locationService.currentPosition;
          
          String gpsLocation = 'Getting location...';
          if (currentLocation != null) {
            gpsLocation = '${currentLocation.latitude.toStringAsFixed(4)}° N, ${currentLocation.longitude.toStringAsFixed(4)}° W';
          }
          
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Session Duration Section
                Text(
                  'Session Duration',
                  style: AppTextStyles.h4,
                ),
                const SizedBox(height: 24),
                
                // Timer Circle
                Center(
                  child: Container(
                    width: 200,
                    height: 200,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: AppColors.primary,
                        width: 4,
                      ),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            _formatDuration(sessionDuration),
                            style: AppTextStyles.timer,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Session Time',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                
                // GPS Location
                Center(
                  child: Text(
                    'GPS: $gpsLocation',
                    style: AppTextStyles.body1.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                
                // Timestamp
                Center(
                  child: Text(
                    'Timestamp: ${DateFormat('yyyy-MM-dd HH:mm:ss').format(DateTime.now())}',
                    style: AppTextStyles.body2.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                
                // Error Message
                if (sessionProvider.errorMessage != null)
                  VCCard(
                    color: AppColors.error.withOpacity(0.1),
                    child: Row(
                      children: [
                        Icon(Icons.error, color: AppColors.error),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            sessionProvider.errorMessage!,
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.error,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                
                // Check Out Button (only if session is active)
                if (activeSession != null && activeSession.checkInTime != null)
                  VCButton(
                    text: 'Check Out',
                    icon: Icons.face,
                    onPressed: sessionProvider.isLoading
                        ? null
                        : () async {
                            final success = await sessionProvider.checkOut(
                              sessionId: activeSession.id,
                            );
                            if (success && mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Checked out successfully'),
                                  backgroundColor: AppColors.success,
                                ),
                              );
                            } else if (mounted && sessionProvider.errorMessage != null) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(sessionProvider.errorMessage!),
                                  backgroundColor: AppColors.error,
                                ),
                              );
                            }
                          },
                    isLoading: sessionProvider.isLoading,
                    width: double.infinity,
                  )
                else
                  VCButton(
                    text: 'Check In',
                    icon: Icons.login,
                    onPressed: () {
                      context.go('/meetings/finder');
                    },
                    width: double.infinity,
                  ),
                const SizedBox(height: 16),
                
                // Instructions
                Center(
                  child: Column(
                    children: [
                      Text(
                        activeSession != null && activeSession.checkInTime != null
                            ? 'Facial verification required to check out.'
                            : 'Select a meeting to check in.',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      if (activeSession != null && activeSession.checkInTime != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          'Failure to check out will result in your attendance being marked as incomplete.',
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.error,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
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
        onTap: (index) {
          switch (index) {
            case 0:
              context.go('/dashboard');
              break;
            case 1:
              context.go('/meetings');
              break;
            case 2:
              context.go('/logs/personal');
              break;
            case 3:
              context.go('/profile/edit');
              break;
          }
        },
      ),
    );
  }
}

