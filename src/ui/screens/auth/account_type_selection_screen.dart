import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/vc_button.dart';
import '../../widgets/vc_card.dart';

/// Account type selection screen
class AccountTypeSelectionScreen extends StatefulWidget {
  const AccountTypeSelectionScreen({Key? key}) : super(key: key);
  
  @override
  State<AccountTypeSelectionScreen> createState() => _AccountTypeSelectionScreenState();
}

class _AccountTypeSelectionScreenState extends State<AccountTypeSelectionScreen> {
  AccountType? _selectedType;
  
  void _handleContinue() {
    if (_selectedType == null) return;
    
    switch (_selectedType!) {
      case AccountType.personal:
      case AccountType.verified:
        // Navigate to dashboard for personal/verified accounts
        context.go('/dashboard');
        break;
      case AccountType.mandated:
        // Navigate to enrollment for mandated accounts
        context.go('/enrollment');
        break;
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: const Text('Account Type'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Choose your account type',
                style: AppTextStyles.h2,
              ),
              const SizedBox(height: 32),
              
              // Personal Account
              VCCard(
                onTap: () {
                  setState(() => _selectedType = AccountType.personal);
                },
                color: _selectedType == AccountType.personal
                    ? AppColors.primary.withOpacity(0.1)
                    : AppColors.surface,
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Personal',
                            style: AppTextStyles.h6,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'For individual use, manage your personal compliance reports.',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 16,
                      color: AppColors.iconSecondary,
                    ),
                  ],
                ),
              ),
              
              // Verified Account
              VCCard(
                onTap: () {
                  setState(() => _selectedType = AccountType.verified);
                },
                color: _selectedType == AccountType.verified
                    ? AppColors.primary.withOpacity(0.1)
                    : AppColors.surface,
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Verified',
                            style: AppTextStyles.h6,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Individuals wanting to show verified compliance.',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 16,
                      color: AppColors.iconSecondary,
                    ),
                  ],
                ),
              ),
              
              // Mandated Account
              VCCard(
                onTap: () {
                  setState(() => _selectedType = AccountType.mandated);
                },
                color: _selectedType == AccountType.mandated
                    ? AppColors.primary.withOpacity(0.1)
                    : AppColors.surface,
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Mandated',
                            style: AppTextStyles.h6,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'For court-mandated compliance, facial recognition applies.',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 16,
                      color: AppColors.iconSecondary,
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              // Learn More Link
              Center(
                child: TextButton(
                  onPressed: () {
                    // TODO: Show account types info
                  },
                  child: Text(
                    'Not sure? Learn about account types',
                    style: AppTextStyles.body2.copyWith(
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ),
              
              const SizedBox(height: 32),
              
              // Continue Button
              VCButton(
                text: 'Continue',
                onPressed: _selectedType != null ? _handleContinue : null,
                width: double.infinity,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

enum AccountType {
  personal,
  verified,
  mandated,
}

