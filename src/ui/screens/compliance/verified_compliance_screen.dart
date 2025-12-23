import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/core/services/location_service.dart';
import '../../../../frontend/lib/core/models/session.dart';
import 'package:geolocator/geolocator.dart';

/// Verified Compliance screen showing session duration and check-out
class VerifiedComplianceScreen extends StatefulWidget {
  const VerifiedComplianceScreen({Key? key}) : super(key: key);
  
  @override
  State<VerifiedComplianceScreen> createState() => _VerifiedComplianceScreenState();
}

class _VerifiedComplianceScreenState extends State<VerifiedComplianceScreen> {
  String? _gpsLocation;
  Position? _currentPosition;
  
  @override
  void initState() {
    super.initState();
    _loadData();
    _getCurrentLocation();
  }
  
  Future<void> _loadData() async {
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    await sessionProvider.loadActiveSession();
  }
  
  Future<void> _getCurrentLocation() async {
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
  
  Duration _calculateSessionDuration(Session? session) {
    if (session == null || session.checkInTime == null) {
      return Duration.zero;
    }
    final checkInTime = session.checkInTime!;
    final now = DateTime.now();
    return now.difference(checkInTime);
  }
  
  Future<void> _handleCheckOut() async {
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    final activeSession = sessionProvider.activeSession;
    
    if (activeSession == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('No active session'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }
    
    // Navigate to check-out warning first
    context.push('/check-out-warning?sessionId=${activeSession.id}');
  }
  
  @override
  Widget build(BuildContext context) {
    return Consumer<SessionProvider>(
      builder: (context, sessionProvider, _) {
        final activeSession = sessionProvider.activeSession;
        final sessionDuration = _calculateSessionDuration(activeSession);
        final hasActiveSession = activeSession != null && activeSession.checkInTime != null;
        
        return Scaffold(
          backgroundColor: AppColors.background,
          drawer: const VCNavigationDrawer(),
          appBar: VCAppBar(
            title: 'Verified Compliance',
          ),
          body: sessionProvider.isLoading
              ? Center(child: CircularProgressIndicator())
              : SingleChildScrollView(
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
                                  hasActiveSession
                                      ? '${sessionDuration.inMinutes} mins'
                                      : '0 mins',
                                  style: AppTextStyles.largeNumber.copyWith(
                                    fontSize: 36,
                                  ),
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
                      
                      // Check Out Button
                      VCButton(
                        text: hasActiveSession ? 'Check Out' : 'Check In',
                        icon: hasActiveSession ? Icons.face : Icons.login,
                        onPressed: hasActiveSession
                            ? _handleCheckOut
                            : () => context.push('/check-in'),
                        width: double.infinity,
                      ),
                      const SizedBox(height: 16),
                      
                      // Instructions
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
          bottomNavigationBar: const VCBottomNavBar(
            currentIndex: VCBottomNavBar.getIndexForRoute('/verified-compliance'),
          ),
        );
      },
    );
  }
}
