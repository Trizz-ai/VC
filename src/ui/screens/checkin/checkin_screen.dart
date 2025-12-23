import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';

/// Check-in screen with facial recognition UI
class CheckInScreen extends StatefulWidget {
  final String? sessionId;
  final String? meetingId;
  
  const CheckInScreen({Key? key, this.sessionId, this.meetingId}) : super(key: key);
  
  @override
  State<CheckInScreen> createState() => _CheckInScreenState();
}

class _CheckInScreenState extends State<CheckInScreen> {
  bool _isProcessing = false;
  
  Future<void> _handleCheckIn() async {
    setState(() => _isProcessing = true);
    
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    
    try {
      String? sessionId = widget.sessionId;
      
      // If no session ID provided, try to get active session or create one
      if (sessionId == null) {
        await sessionProvider.loadActiveSession();
        final activeSession = sessionProvider.activeSession;
        
        if (activeSession != null && !activeSession.isCheckedIn) {
          sessionId = activeSession.id;
        } else if (widget.meetingId != null) {
          // Create new session for the meeting
          final success = await sessionProvider.createSession(
            meetingId: widget.meetingId!,
            notes: 'Session created via check-in',
          );
          if (success && sessionProvider.activeSession != null) {
            sessionId = sessionProvider.activeSession!.id;
          }
        }
      }
      
      if (sessionId == null) {
        throw Exception('Unable to create or find session');
      }
      
      final success = await sessionProvider.checkIn(
        sessionId: sessionId,
        notes: 'Checked in via app',
      );
      
      if (mounted) {
        setState(() => _isProcessing = false);
        
        if (success) {
          context.go('/dashboard');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(sessionProvider.errorMessage ?? 'Check-in failed'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isProcessing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: VCAppBar(
        title: 'Check-In',
        showDrawer: false, // Check-in is a modal flow
        showHomeButton: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 32),
              
              // Instructions
              Text(
                "Alright, let's get you checked in!",
                style: AppTextStyles.h3,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Just center your awesome face in the circle!',
                style: AppTextStyles.body1.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              
              // Facial Recognition Area
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Face illustration placeholder
                      Container(
                        width: 200,
                        height: 200,
                        decoration: BoxDecoration(
                          color: AppColors.surfaceVariant,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          Icons.face,
                          size: 100,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      
                      // Dashed circle guide
                      Container(
                        width: 220,
                        height: 220,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: AppColors.primary,
                            width: 2,
                            style: BorderStyle.solid,
                          ),
                        ),
                      ),
                      
                      // Direction arrows
                      Positioned(
                        top: 0,
                        child: Icon(
                          Icons.keyboard_arrow_up,
                          color: AppColors.primary,
                          size: 32,
                        ),
                      ),
                      Positioned(
                        bottom: 0,
                        child: Icon(
                          Icons.keyboard_arrow_down,
                          color: AppColors.primary,
                          size: 32,
                        ),
                      ),
                      Positioned(
                        left: 0,
                        child: Icon(
                          Icons.keyboard_arrow_left,
                          color: AppColors.primary,
                          size: 32,
                        ),
                      ),
                      Positioned(
                        right: 0,
                        child: Icon(
                          Icons.keyboard_arrow_right,
                          color: AppColors.primary,
                          size: 32,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 32),
              
              // Ready Button
              VCButton(
                text: 'Ready to Check In!',
                onPressed: _isProcessing ? null : _handleCheckIn,
                isLoading: _isProcessing,
                width: double.infinity,
              ),
              
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}

