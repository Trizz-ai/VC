import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/payment_service.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// Subscription Screen - Connected to Backend
class SubscriptionScreenConnected extends StatefulWidget {
  const SubscriptionScreenConnected({Key? key}) : super(key: key);
  
  @override
  State<SubscriptionScreenConnected> createState() => _SubscriptionScreenConnectedState();
}

class _SubscriptionScreenConnectedState extends State<SubscriptionScreenConnected> {
  List<Map<String, dynamic>> _plans = [];
  String? _selectedPlanId;
  bool _isLoading = true;
  bool _isProcessing = false;
  
  @override
  void initState() {
    super.initState();
    _loadPlans();
  }
  
  Future<void> _loadPlans() async {
    setState(() => _isLoading = true);
    
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final paymentService = PaymentService(apiService);
      
      final result = await paymentService.getSubscriptionPlans();
      
      if (mounted) {
        setState(() {
          _isLoading = false;
          if (result['success'] == true || result['plans'] != null) {
            _plans = List<Map<String, dynamic>>.from(result['plans'] ?? []);
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        _showError('Failed to load plans: ${e.toString()}');
      }
    }
  }
  
  Future<void> _subscribe(String planId) async {
    setState(() {
      _selectedPlanId = planId;
      _isProcessing = true;
    });
    
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final paymentService = PaymentService(apiService);
      
      // In production, you would:
      // 1. Show payment method selection dialog
      // 2. Process payment with Stripe/payment gateway
      // 3. Get payment method ID
      // For now, use mock payment method ID
      
      final mockPaymentMethodId = 'pm_${DateTime.now().millisecondsSinceEpoch}';
      
      final result = await paymentService.createSubscription(
        planId,
        mockPaymentMethodId,
        metadata: {
          'source': 'mobile_app',
          'subscription_date': DateTime.now().toIso8601String(),
        },
      );
      
      if (mounted) {
        setState(() => _isProcessing = false);
        
        if (result['success'] == true) {
          _showSuccess('Subscription created successfully!');
          await Future.delayed(const Duration(seconds: 2));
          if (mounted) {
            context.go('/dashboard');
          }
        } else {
          _showError(result['message'] ?? 'Subscription failed');
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isProcessing = false);
        _showError('Error: ${e.toString()}');
      }
    }
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
      ),
    );
  }
  
  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.success,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Choose Your Plan',
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Select a plan that works for you',
                    style: AppTextStyles.h4,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'All plans include GPS verification, session tracking, and compliance reporting.',
                    style: AppTextStyles.body2.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 32),
                  
                  // Plans
                  ..._plans.map((plan) => _buildPlanCard(plan)).toList(),
                  
                  const SizedBox(height: 24),
                  
                  // Features comparison
                  Text(
                    'What\'s included',
                    style: AppTextStyles.h5,
                  ),
                  const SizedBox(height: 16),
                  _buildFeatureItem('GPS check-in/check-out', true),
                  _buildFeatureItem('Session tracking', true),
                  _buildFeatureItem('Basic reports', true),
                  _buildFeatureItem('Email support', true),
                  _buildFeatureItem('Biometric verification', false, 'Professional+'),
                  _buildFeatureItem('AI legal assistant', false, 'Professional+'),
                  _buildFeatureItem('Client management', false, 'Professional+'),
                  _buildFeatureItem('Advanced analytics', false, 'Enterprise'),
                  _buildFeatureItem('API access', false, 'Enterprise'),
                  _buildFeatureItem('24/7 support', false, 'Enterprise'),
                ],
              ),
            ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
  
  Widget _buildPlanCard(Map<String, dynamic> plan) {
    final planId = plan['plan_id'] as String;
    final name = plan['name'] as String;
    final description = plan['description'] as String?;
    final amount = plan['amount'] as num;
    final interval = plan['interval'] as String? ?? 'month';
    final features = List<String>.from(plan['features'] ?? []);
    
    final bool isPopular = planId == 'professional';
    final bool isProcessingThis = _isProcessing && _selectedPlanId == planId;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        border: Border.all(
          color: isPopular ? AppColors.primary : AppColors.border,
          width: isPopular ? 2 : 1,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: VCCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Popular badge
            if (isPopular)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'MOST POPULAR',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.onPrimary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            if (isPopular) const SizedBox(height: 16),
            
            // Plan name
            Text(
              name,
              style: AppTextStyles.h4,
            ),
            const SizedBox(height: 8),
            
            // Description
            if (description != null)
              Text(
                description,
                style: AppTextStyles.body2.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            const SizedBox(height: 16),
            
            // Price
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '\$${amount.toStringAsFixed(2)}',
                  style: AppTextStyles.h2.copyWith(
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(width: 8),
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text(
                    '/ $interval',
                    style: AppTextStyles.body2.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Features
            ...features.map((feature) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      Icon(
                        Icons.check_circle,
                        color: AppColors.success,
                        size: 20,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          feature,
                          style: AppTextStyles.body2,
                        ),
                      ),
                    ],
                  ),
                )),
            const SizedBox(height: 16),
            
            // Subscribe button
            VCButton(
              text: isProcessingThis ? 'Processing...' : 'Subscribe',
              onPressed: isProcessingThis ? null : () => _subscribe(planId),
              isLoading: isProcessingThis,
              isPrimary: isPopular,
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildFeatureItem(String feature, bool included, [String? requiredPlan]) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(
            included ? Icons.check_circle : Icons.cancel,
            color: included ? AppColors.success : AppColors.textSecondary,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              feature,
              style: AppTextStyles.body2.copyWith(
                color: included ? AppColors.textPrimary : AppColors.textSecondary,
              ),
            ),
          ),
          if (!included && requiredPlan != null)
            Text(
              requiredPlan,
              style: AppTextStyles.caption.copyWith(
                color: AppColors.primary,
              ),
            ),
        ],
      ),
    );
  }
}

