import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:geolocator/geolocator.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/core/services/location_service.dart';
import '../../../../frontend/lib/core/models/session.dart';

/// Main dashboard screen with session timer and GPS tracking - Connected to Backend
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);
  
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String? _gpsLocation;
  Position? _currentPosition;
  Map<String, dynamic>? _statistics;
  bool _isLoadingStats = false;
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    
    // Load active session
    await sessionProvider.loadActiveSession();
    
    // Load session history for statistics
    await sessionProvider.loadSessionHistory(limit: 100, offset: 0);
    
    // Load statistics
    _isLoadingStats = true;
    if (mounted) setState(() {});
    
    try {
      final stats = await sessionProvider.getStatistics(
        startDate: DateTime.now().subtract(const Duration(days: 365)),
        endDate: DateTime.now(),
      );
      if (mounted) {
        setState(() {
          _statistics = stats;
          _isLoadingStats = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingStats = false;
        });
      }
    }
    
    // Get current location
    try {
      final locationService = Provider.of<LocationService>(context, listen: false);
      final position = await locationService.getCurrentPosition();
      if (position != null && mounted) {
        setState(() {
          _currentPosition = position;
          _gpsLocation = '${position.latitude.toStringAsFixed(4)}° ${position.latitude >= 0 ? 'N' : 'S'}, ${position.longitude.toStringAsFixed(4)}° ${position.longitude >= 0 ? 'E' : 'W'}';
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
  
  Duration _getSessionDuration(SessionProvider sessionProvider) {
    final session = sessionProvider.activeSession;
    if (session == null) return Duration.zero;
    
    // Calculate duration from check-in time
    final checkInTime = session.checkInTime;
    if (checkInTime == null) return Duration.zero;
    
    return DateTime.now().difference(checkInTime);
  }
  
  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final hours = twoDigits(duration.inHours);
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$hours:$minutes:$seconds';
  }
  
  int _calculateTotalSessions(SessionProvider sessionProvider) {
    if (_statistics != null && _statistics!['total_sessions'] != null) {
      return _statistics!['total_sessions'] as int;
    }
    return sessionProvider.sessionHistory.length;
  }
  
  String _calculateTotalHours(SessionProvider sessionProvider) {
    if (_statistics != null && _statistics!['average_duration_minutes'] != null && _statistics!['completed_sessions'] != null) {
      final avgMinutes = _statistics!['average_duration_minutes'] as double;
      final completedSessions = _statistics!['completed_sessions'] as int;
      final totalMinutes = avgMinutes * completedSessions;
      final hours = (totalMinutes / 60).floor();
      final minutes = (totalMinutes % 60).floor();
      if (hours > 0) {
        return '${hours}h ${minutes}m';
      }
      return '${minutes}m';
    }
    
    // Calculate from session history
    final sessions = sessionProvider.sessionHistory.where((s) => s.isCheckedOut && s.duration != null).toList();
    final totalDuration = sessions.fold<Duration>(
      Duration.zero,
      (sum, session) => sum + (session.duration ?? Duration.zero),
    );
    final hours = totalDuration.inHours;
    final minutes = totalDuration.inMinutes.remainder(60);
    if (hours > 0) {
      return '${hours}h ${minutes}m';
    }
    return '${minutes}m';
  }
  
  String _calculateComplianceRate(SessionProvider sessionProvider) {
    if (_statistics != null && _statistics!['total_sessions'] != null && _statistics!['completed_sessions'] != null) {
      final total = _statistics!['total_sessions'] as int;
      final completed = _statistics!['completed_sessions'] as int;
      if (total == 0) return '0%';
      final rate = (completed / total * 100).round();
      return '$rate%';
    }
    
    // Calculate from session history
    final sessions = sessionProvider.sessionHistory;
    if (sessions.isEmpty) return '0%';
    final completed = sessions.where((s) => s.isCheckedOut).length;
    final rate = (completed / sessions.length * 100).round();
    return '$rate%';
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Verified Compliance',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: Consumer<SessionProvider>(
        builder: (context, sessionProvider, _) {
          final session = sessionProvider.activeSession;
          final duration = _getSessionDuration(sessionProvider);
          
          if (sessionProvider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }
          
          if (sessionProvider.errorMessage != null) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppColors.error.withOpacity(0.1),
                      ),
                      child: Icon(
                        Icons.error_outline,
                        size: 48,
                        color: AppColors.error,
                      ),
                    ),
                    const SizedBox(height: 24),
                    Text(
                      sessionProvider.errorMessage ?? 'Failed to load active session',
                      style: AppTextStyles.body1.copyWith(
                        color: AppColors.textPrimary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    VCButton(
                      text: 'Retry',
                      onPressed: _loadData,
                      width: 200,
                    ),
                  ],
                ),
              ),
            );
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
                        color: session != null ? AppColors.primary : AppColors.divider,
                        width: 4,
                      ),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            session != null ? _formatDuration(duration) : '00:00:00',
                            style: AppTextStyles.timer,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Session Time',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          if (session != null) ...[
                            const SizedBox(height: 8),
                            VCStatusBadge(
                              label: session.isCheckedIn ? 'Checked In' : 'Active',
                              type: VCStatusType.verified,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                
                // Session Info
                if (session != null) ...[
                  VCCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Session: ${session.destName ?? 'Unknown'}',
                          style: AppTextStyles.h6,
                        ),
                        if (session.destAddress != null) ...[
                          const SizedBox(height: 8),
                          Text(
                            session.destAddress!,
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                        if (session.checkInTime != null) ...[
                          const SizedBox(height: 8),
                          Text(
                            'Checked in: ${DateFormat('MMM dd, yyyy HH:mm').format(session.checkInTime!)}',
                            style: AppTextStyles.caption,
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                
                // GPS Location
                Center(
                  child: Text(
                    'GPS: ${_gpsLocation ?? 'Loading...'}',
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
                
                // Find Meetings Button
                VCButton(
                  text: 'Find Meetings',
                  icon: Icons.search,
                  onPressed: () {
                    context.go('/meetings/finder');
                  },
                  width: double.infinity,
                ),
                const SizedBox(height: 32),
                
                // Quick Actions Section
                Text(
                  'Quick Actions',
                  style: AppTextStyles.h4,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: VCCard(
                        onTap: () {
                          context.go('/meetings/finder');
                        },
                        child: Column(
                          children: [
                            Icon(
                              Icons.search,
                              color: AppColors.primary,
                              size: 32,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Find Meetings',
                              style: AppTextStyles.body2,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: VCCard(
                        onTap: () {
                          context.go('/logs/personal');
                        },
                        child: Column(
                          children: [
                            Icon(
                              Icons.history,
                              color: AppColors.primary,
                              size: 32,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'View Logs',
                              style: AppTextStyles.body2,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: VCCard(
                        onTap: () {
                          context.go('/compliance');
                        },
                        child: Column(
                          children: [
                            Icon(
                              Icons.verified,
                              color: AppColors.primary,
                              size: 32,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Compliance',
                              style: AppTextStyles.body2,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                
                // Your Statistics Section
                Text(
                  'Your Statistics',
                  style: AppTextStyles.h4,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: VCCard(
                        child: Column(
                          children: [
                            Text(
                              _isLoadingStats ? '...' : '${_calculateTotalSessions(sessionProvider)}',
                              style: AppTextStyles.h4.copyWith(
                                color: AppColors.primary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Total Sessions',
                              style: AppTextStyles.body2,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: VCCard(
                        child: Column(
                          children: [
                            Text(
                              _isLoadingStats ? '...' : _calculateTotalHours(sessionProvider),
                              style: AppTextStyles.h4.copyWith(
                                color: AppColors.success,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Total Hours',
                              style: AppTextStyles.body2,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: VCCard(
                        child: Column(
                          children: [
                            Text(
                              _isLoadingStats ? '...' : _calculateComplianceRate(sessionProvider),
                              style: AppTextStyles.h4.copyWith(
                                color: AppColors.success,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Compliance',
                              style: AppTextStyles.body2,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                
                // Action Buttons
                if (session != null && session.isCheckedIn) ...[
                  VCButton(
                    text: 'Check Out',
                    icon: Icons.logout,
                    onPressed: () {
                      context.go('/check-out-warning?sessionId=${session.id}');
                    },
                    width: double.infinity,
                  ),
                ] else if (session != null) ...[
                  VCButton(
                    text: 'Check In',
                    icon: Icons.login,
                    onPressed: () {
                      context.go('/check-in?sessionId=${session.id}');
                    },
                    width: double.infinity,
                  ),
                ],
                const SizedBox(height: 16),
                
                // Instructions
                if (session != null && session.isCheckedIn)
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
          );
        },
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}

