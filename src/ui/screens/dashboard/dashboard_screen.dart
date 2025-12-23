import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/features/auth/providers/auth_provider.dart';
import '../../../../frontend/lib/core/services/location_service.dart';

/// Main dashboard screen with session timer and GPS tracking
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);
  
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String? _gpsLocation;
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    // Load active session
    final sessionProvider = context.read<SessionProvider>();
    await sessionProvider.loadActiveSession();
    
    // Get current location
    final locationService = context.read<LocationService>();
    try {
      final position = await locationService.getCurrentPosition();
      if (position != null && mounted) {
        setState(() {
          _gpsLocation = '${position.latitude.toStringAsFixed(4)}° N, ${position.longitude.toStringAsFixed(4)}° W';
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _gpsLocation = 'Location unavailable';
        });
      }
    }
  }
  
  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final hours = twoDigits(duration.inHours);
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$hours:$minutes:$seconds';
  }
  
  Duration _calculateSessionDuration(Session? session) {
    if (session == null || !session.isCheckedIn || session.checkInTime == null) {
      return Duration.zero;
    }
    
    final checkInTime = session.checkInTime!;
    final now = DateTime.now();
    return now.difference(checkInTime);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Verified Compliance',
      ),
      body: Consumer<SessionProvider>(
        builder: (context, sessionProvider, _) {
          final activeSession = sessionProvider.activeSession;
          final sessionDuration = _calculateSessionDuration(activeSession);
          
          if (sessionProvider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }
          
          return RefreshIndicator(
            onRefresh: _loadData,
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              physics: const AlwaysScrollableScrollPhysics(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Welcome Message
                  Consumer<AuthProvider>(
                    builder: (context, authProvider, _) {
                      return Text(
                        'Welcome, ${authProvider.userName ?? "User"}',
                        style: AppTextStyles.h4,
                      );
                    },
                  ),
                  const SizedBox(height: 24),
                  
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
                              activeSession != null && activeSession.isCheckedIn
                                  ? _formatDuration(sessionDuration)
                                  : '00:00:00',
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
                      'GPS: ${_gpsLocation ?? "Loading..."}',
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
                  
                  // Session Info
                  if (activeSession != null) ...[
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Active Session',
                            style: AppTextStyles.h6,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Destination: ${activeSession.destName}',
                            style: AppTextStyles.body2,
                          ),
                          Text(
                            'Address: ${activeSession.destAddress}',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          if (activeSession.isCheckedIn) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Checked in: ${DateFormat('MMM d, y h:mm a').format(activeSession.checkInTime!)}',
                              style: AppTextStyles.caption.copyWith(
                                color: AppColors.success,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  
                  // Error Message
                  if (sessionProvider.errorMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.error.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.error),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.error_outline, color: AppColors.error, size: 20),
                          const SizedBox(width: 8),
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
                    const SizedBox(height: 16),
                  ],
                  
                  // Action Buttons
                  if (activeSession != null) ...[
                    if (!activeSession.isCheckedIn) ...[
                      VCButton(
                        text: 'Check In',
                        icon: Icons.login,
                        onPressed: () async {
                          final success = await sessionProvider.checkIn(
                            sessionId: activeSession.id,
                          );
                          if (success && mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Checked in successfully'),
                                backgroundColor: AppColors.success,
                              ),
                            );
                            await _loadData();
                          } else if (mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  sessionProvider.errorMessage ?? 'Check-in failed',
                                ),
                                backgroundColor: AppColors.error,
                              ),
                            );
                          }
                        },
                        width: double.infinity,
                      ),
                    ] else ...[
                      VCButton(
                        text: 'Check Out',
                        icon: Icons.logout,
                        onPressed: () {
                          context.go('/check-out-warning');
                        },
                        width: double.infinity,
                      ),
                    ],
                  ] else ...[
                    VCButton(
                      text: 'Find Meetings',
                      icon: Icons.search,
                      onPressed: () {
                        context.go('/meetings/finder');
                      },
                      width: double.infinity,
                    ),
                  ],
                  const SizedBox(height: 16),
                  
                  // Instructions
                  if (activeSession != null && activeSession.isCheckedIn)
                    Center(
                      child: Column(
                        children: [
                          Text(
                            'Facial verification required to check out.',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Failure to check out will result in your attendance being marked as incomplete.',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.error,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          );
        },
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}

