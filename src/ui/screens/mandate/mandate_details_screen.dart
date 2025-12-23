import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// Mandate details screen showing mandate terms and legal acknowledgment
class MandateDetailsScreen extends StatefulWidget {
  final String? mandateId;
  
  const MandateDetailsScreen({Key? key, this.mandateId}) : super(key: key);
  
  @override
  State<MandateDetailsScreen> createState() => _MandateDetailsScreenState();
}

class _MandateDetailsScreenState extends State<MandateDetailsScreen> {
  Map<String, dynamic>? _mandateData;
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadMandateData();
  }
  
  Future<void> _loadMandateData() async {
    // In a real app, this would fetch mandate data from API
    // For now, use default data structure
    if (mounted) {
      setState(() {
        _mandateData = {
          'issued_by': 'Judge John Doe',
          'meeting_type': 'In-Person',
          'meeting_length': 60,
          'meeting_frequency': 'Weekly',
          'mandate_duration': 12,
        };
        _isLoading = false;
      });
    }
  }
  
  Future<void> _handleAccept() async {
    // TODO: Call API to accept mandate
    // For now, navigate to dashboard
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Mandate accepted successfully'),
        backgroundColor: AppColors.success,
      ),
    );
    context.go('/dashboard');
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppColors.background,
        drawer: const VCNavigationDrawer(),
        appBar: VCAppBar(
          title: 'Mandate Details',
        ),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Mandate Details',
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Mandate Issued By Section
            Text(
              'Mandate Issued By:',
              style: AppTextStyles.h5,
            ),
            const SizedBox(height: 8),
            Text(
              _mandateData?['issued_by'] ?? 'Judge',
              style: AppTextStyles.body1,
            ),
            const SizedBox(height: 32),
            
            // Mandate Terms Section
            Text(
              'Mandate Terms',
              style: AppTextStyles.h5,
            ),
            const SizedBox(height: 16),
            
            // Meeting Type
            VCCard(
              child: Row(
                children: [
                  Icon(
                    Icons.groups,
                    color: AppColors.primary,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Meeting Type',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _mandateData?['meeting_type'] ?? 'In-Person',
                          style: AppTextStyles.h6,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // Meeting Length
            VCCard(
              child: Row(
                children: [
                  Icon(
                    Icons.timer,
                    color: AppColors.primary,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Meeting Length',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_mandateData?['meeting_length'] ?? 60} minutes',
                          style: AppTextStyles.h6,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // Meeting Frequency
            VCCard(
              child: Row(
                children: [
                  Icon(
                    Icons.calendar_today,
                    color: AppColors.primary,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Meeting Frequency',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _mandateData?['meeting_frequency'] ?? 'Weekly',
                          style: AppTextStyles.h6,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // Mandate Duration
            VCCard(
              child: Row(
                children: [
                  Icon(
                    Icons.calendar_month,
                    color: AppColors.primary,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Mandate Duration',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_mandateData?['mandate_duration'] ?? 12} Months',
                          style: AppTextStyles.h6,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Legal Acknowledgment Section
            Text(
              'Legal Acknowledgment',
              style: AppTextStyles.h5,
            ),
            const SizedBox(height: 16),
            Text(
              'By creating an account and proceeding, I acknowledge and agree to comply with the terms and conditions of this mandate as outlined above. I understand that Verified Compliance serves as a reporting and verification platform and that all mandates are issued by independent third parties or authorized entities.',
              style: AppTextStyles.body2.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 32),
            
            // Accept & Continue Button
            VCButton(
              text: 'Accept & Continue',
              onPressed: _handleAccept,
              width: double.infinity,
            ),
          ],
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}
