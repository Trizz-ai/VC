import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// Subscription activation screen for Verified Reports
class SubscriptionScreen extends StatefulWidget {
  const SubscriptionScreen({Key? key}) : super(key: key);
  
  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  SubscriptionType _selectedType = SubscriptionType.monthly;
  final _promoCodeController = TextEditingController();
  bool _agreedToTerms = false;
  bool _isProcessing = false;
  
  @override
  void dispose() {
    _promoCodeController.dispose();
    super.dispose();
  }
  
  Future<void> _handlePayment() async {
    if (!_agreedToTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please agree to the terms and conditions'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }
    
    setState(() => _isProcessing = true);
    
    try {
      // TODO: Integrate with payment processing (Stripe)
      // For now, simulate payment processing
      await Future.delayed(const Duration(seconds: 2));
      
      // TODO: Call API to activate subscription
      // await apiService.activateSubscription(
      //   type: _selectedType,
      //   promoCode: _promoCodeController.text.trim().isEmpty 
      //       ? null 
      //       : _promoCodeController.text.trim(),
      // );
      
      if (mounted) {
        setState(() => _isProcessing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Subscription activated successfully!'),
            backgroundColor: AppColors.success,
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isProcessing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Payment failed: ${e.toString()}'),
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
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Activate Verified Reports',
        showDrawer: false, // Modal screen, use back button
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Court-admissible reports with verified time, location, and identity.',
              style: AppTextStyles.body1.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 32),
            
            // Monthly Subscription Option
            VCCard(
              onTap: () {
                setState(() => _selectedType = SubscriptionType.monthly);
              },
              color: _selectedType == SubscriptionType.monthly
                  ? AppColors.primary.withOpacity(0.1)
                  : AppColors.surface,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Verified Reports - Monthly',
                        style: AppTextStyles.h6,
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          'Cancel anytime',
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '\$20.00/month',
                    style: AppTextStyles.h4.copyWith(
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildFeatureItem('Unlimited verified reports'),
                  _buildFeatureItem('GPS/time + facial recognition'),
                  _buildFeatureItem('Fraud-proof QR code'),
                  _buildFeatureItem('Save to wallet; share with courts/attorneys'),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Single Report Option
            VCCard(
              onTap: () {
                setState(() => _selectedType = SubscriptionType.single);
              },
              color: _selectedType == SubscriptionType.single
                  ? AppColors.primary.withOpacity(0.1)
                  : AppColors.surface,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Single Report',
                    style: AppTextStyles.h6,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '\$10.00/per report',
                    style: AppTextStyles.h4.copyWith(
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildFeatureItem('One verified attendance report'),
                  _buildFeatureItem('Location & time verification'),
                  _buildFeatureItem('Shareable compliance report'),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Promo Code Section
            Text(
              'Promo or discount code',
              style: AppTextStyles.body2,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: VCTextField(
                    hint: 'Enter code',
                    controller: _promoCodeController,
                  ),
                ),
                const SizedBox(width: 12),
                VCButton(
                  text: 'Apply',
                  onPressed: () {
                    // TODO: Validate promo code
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Promo code validation coming soon'),
                      ),
                    );
                  },
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Payment Method Section
            Text(
              'Payment Method',
              style: AppTextStyles.body2,
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppColors.divider,
                  style: BorderStyle.solid,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.credit_card,
                    color: AppColors.iconSecondary,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Enter Payment Details',
                    style: AppTextStyles.body2.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Terms Checkbox
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Checkbox(
                  value: _agreedToTerms,
                  onChanged: (value) {
                    setState(() => _agreedToTerms = value ?? false);
                  },
                  activeColor: AppColors.primary,
                ),
                Expanded(
                  child: Text.rich(
                    TextSpan(
                      text: 'By proceeding, I authorize Verified Compliance to charge \$${_selectedType == SubscriptionType.monthly ? "20.00" : "10.00"} ${_selectedType == SubscriptionType.monthly ? "monthly" : ""} for ${_selectedType == SubscriptionType.monthly ? "Verified Reports" : "this report"}. I agree to the ',
                      style: AppTextStyles.body2,
                      children: [
                        TextSpan(
                          text: 'Terms of Use',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.primary,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                        const TextSpan(text: ' and '),
                        TextSpan(
                          text: 'Privacy Policy',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.primary,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                        const TextSpan(text: ', and acknowledge that access may be suspended if payment fails.'),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 32),
            
            // Pay & Activate Button
            VCButton(
              text: _selectedType == SubscriptionType.monthly
                  ? 'Pay & Activate Verified Reports'
                  : 'Pay & Generate Report',
              onPressed: _isProcessing ? null : _handlePayment,
              isLoading: _isProcessing,
              width: double.infinity,
            ),
            
            const SizedBox(height: 16),
            
            // Security Footer
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.lock,
                  size: 16,
                  color: AppColors.textSecondary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Payments securely processed by Stripe.',
                  style: AppTextStyles.caption,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(
                'You can cancel your subscription at any time from your account settings.',
                style: AppTextStyles.caption,
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildFeatureItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(
            Icons.check_circle,
            color: AppColors.success,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: AppTextStyles.body2,
            ),
          ),
        ],
      ),
    );
  }
}

enum SubscriptionType {
  monthly,
  single,
}
