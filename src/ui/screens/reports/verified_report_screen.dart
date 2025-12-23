import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/core/models/session.dart';
import '../../../../frontend/lib/core/services/api_service.dart';
import '../../../../frontend/lib/core/models/contact.dart';

/// Verified report screen showing detailed attendance report
class VerifiedReportScreen extends StatefulWidget {
  final String? sessionId;
  
  const VerifiedReportScreen({Key? key, this.sessionId}) : super(key: key);
  
  @override
  State<VerifiedReportScreen> createState() => _VerifiedReportScreenState();
}

class _VerifiedReportScreenState extends State<VerifiedReportScreen> {
  Session? _session;
  Contact? _user;
  Map<String, dynamic>? _sessionDetails;
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadSessionData();
  }
  
  Future<void> _loadSessionData() async {
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    final apiService = Provider.of<ApiService>(context, listen: false);
    
    try {
      String? sessionId = widget.sessionId;
      
      // If no session ID, try to get active session
      if (sessionId == null) {
        await sessionProvider.loadActiveSession();
        final activeSession = sessionProvider.activeSession;
        if (activeSession != null) {
          sessionId = activeSession.id;
        }
      }
      
      if (sessionId != null) {
        // Load session details
        final session = await sessionProvider.getSessionDetails(sessionId);
        final details = await sessionProvider.getSessionDetailsFull(sessionId);
        final user = await apiService.getCurrentUser();
        
        if (mounted) {
          setState(() {
            _session = session;
            _sessionDetails = details;
            _user = user;
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() => _isLoading = false);
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading session: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
  
  String _formatDuration(Duration? duration) {
    if (duration == null) return 'N/A';
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    return '${hours}h ${minutes}m';
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppColors.background,
        drawer: const VCNavigationDrawer(),
        appBar: VCAppBar(
          title: 'Verified Report',
        ),
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }
    
    if (_session == null) {
      return Scaffold(
        backgroundColor: AppColors.background,
        drawer: const VCNavigationDrawer(),
        appBar: VCAppBar(
          title: 'Verified Report',
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: AppColors.error,
              ),
              const SizedBox(height: 16),
              Text(
                'Session not found',
                style: AppTextStyles.h5,
              ),
              const SizedBox(height: 8),
              VCButton(
                text: 'Go to Dashboard',
                onPressed: () => context.go('/dashboard'),
              ),
            ],
          ),
        ),
      );
    }
    
    final checkInTime = _session!.checkInTime;
    final checkOutTime = _session!.checkOutTime;
    final duration = _session!.duration ?? 
        (checkInTime != null && checkOutTime != null 
            ? checkOutTime.difference(checkInTime)
            : null);
    
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Verified Report',
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // TODO: Show options menu
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // User Information Card
            VCCard(
              child: Row(
                children: [
                  // Profile Picture
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppColors.surfaceVariant,
                    ),
                    child: Icon(
                      Icons.person,
                      color: AppColors.textSecondary,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _user?.fullName ?? 'User',
                          style: AppTextStyles.h5,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'GPS: ${_session!.destLat.toStringAsFixed(4)}° ${_session!.destLat >= 0 ? 'N' : 'S'}, ${_session!.destLng.toStringAsFixed(4)}° ${_session!.destLng >= 0 ? 'E' : 'W'}',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Attendance Details Card
            VCCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildDetailRow(
                    label: 'Time checked in',
                    value: checkInTime != null
                        ? DateFormat('hh:mm a, d MMM yyyy').format(checkInTime)
                        : 'Not checked in',
                  ),
                  const Divider(height: 32),
                  _buildDetailRow(
                    label: 'Time checked out',
                    value: checkOutTime != null
                        ? DateFormat('hh:mm a, d MMM yyyy').format(checkOutTime)
                        : 'Not checked out',
                  ),
                  const Divider(height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Biometrics verified at check in',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      VCStatusBadge(
                        label: checkInTime != null ? 'Verified' : 'Pending',
                        type: checkInTime != null ? VCStatusType.verified : VCStatusType.pending,
                      ),
                    ],
                  ),
                  const Divider(height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Biometrics verified at check out',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      VCStatusBadge(
                        label: checkOutTime != null ? 'Verified' : 'Pending',
                        type: checkOutTime != null ? VCStatusType.verified : VCStatusType.pending,
                      ),
                    ],
                  ),
                  const Divider(height: 32),
                  _buildDetailRow(
                    label: 'Total attendance time',
                    value: _formatDuration(duration),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Action Buttons
            VCButton(
              text: 'Report Dashboard',
              onPressed: () {
                context.go('/dashboard');
              },
              width: double.infinity,
            ),
            const SizedBox(height: 12),
            VCButton(
              text: 'Generate Report',
              type: VCButtonType.outlined,
              onPressed: () {
                // TODO: Generate PDF report
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Report generation coming soon'),
                  ),
                );
              },
              width: double.infinity,
            ),
          ],
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
  
  Widget _buildDetailRow({
    required String label,
    required String value,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.body2.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: AppTextStyles.body1.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
