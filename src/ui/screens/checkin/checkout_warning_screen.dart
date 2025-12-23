import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';

/// Warning screen when user tries to leave without checking out
class CheckoutWarningScreen extends StatefulWidget {
  final String? sessionId;
  
  const CheckoutWarningScreen({Key? key, this.sessionId}) : super(key: key);
  
  @override
  State<CheckoutWarningScreen> createState() => _CheckoutWarningScreenState();
}

class _CheckoutWarningScreenState extends State<CheckoutWarningScreen> {
  bool _isProcessing = false;
  
  Future<void> _handleCheckOut() async {
    setState(() => _isProcessing = true);
    
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    
    try {
      String? sessionId = widget.sessionId;
      
      // If no session ID provided, try to get active session
      if (sessionId == null) {
        await sessionProvider.loadActiveSession();
        final activeSession = sessionProvider.activeSession;
        if (activeSession != null && activeSession.isCheckedIn && !activeSession.isCheckedOut) {
          sessionId = activeSession.id;
        }
      }
      
      if (sessionId == null) {
        throw Exception('No active session found');
      }
      
      final success = await sessionProvider.checkOut(
        sessionId: sessionId,
        notes: 'Checked out via app',
      );
      
      if (mounted) {
        setState(() => _isProcessing = false);
        
        if (success) {
          context.go('/dashboard');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(sessionProvider.errorMessage ?? 'Check-out failed'),
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
  
  Future<void> _handleLeaveAnyway() async {
    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Leave Without Checking Out?'),
        content: Text(
          'Your session will be marked as non-compliant. Are you sure you want to leave?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(
              foregroundColor: AppColors.error,
            ),
            child: Text('Leave Anyway'),
          ),
        ],
      ),
    );
    
    if (confirmed == true && mounted) {
      context.go('/dashboard');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: VCAppBar(
        title: 'Check-Out Warning',
        showDrawer: false, // Modal screen
        showHomeButton: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Warning Icon
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: AppColors.error,
                    width: 4,
                  ),
                ),
                child: const Icon(
                  Icons.warning,
                  color: AppColors.error,
                  size: 64,
                ),
              ),
              const SizedBox(height: 32),
              
              // Warning Message
              Text(
                'Leaving Without Checking Out Will Result in Automatic Failure.',
                style: AppTextStyles.h4,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              
              // Explanation
              Text(
                'Your attendance must be verified through check-out before leaving this location. If you exit without checking out, your session will be automatically marked as non-compliant.',
                style: AppTextStyles.body1.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              
              // Check Out Button
              VCButton(
                text: 'Check Out',
                onPressed: _isProcessing ? null : _handleCheckOut,
                isLoading: _isProcessing,
                width: double.infinity,
              ),
              const SizedBox(height: 16),
              
              // Leave Anyway Button
              VCButton(
                text: 'Leave Anyway',
                type: VCButtonType.outlined,
                onPressed: _isProcessing ? null : _handleLeaveAnyway,
                width: double.infinity,
              ),
              
              const Spacer(),
              
              // Footer
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.fingerprint,
                    color: AppColors.textSecondary,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    Icons.location_on,
                    color: AppColors.textSecondary,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Monitored Session Integrity',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}
