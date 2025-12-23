import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/vc_button.dart';
import '../../widgets/vc_text_field.dart';
import '../../../../frontend/lib/core/services/api_service.dart';
import '../../../../frontend/lib/core/models/contact.dart';

/// Create professional account screen for attorneys and court officials
class CreateProfessionalAccountScreen extends StatefulWidget {
  const CreateProfessionalAccountScreen({Key? key}) : super(key: key);
  
  @override
  State<CreateProfessionalAccountScreen> createState() => _CreateProfessionalAccountScreenState();
}

class _CreateProfessionalAccountScreenState extends State<CreateProfessionalAccountScreen> {
  final _formKey = GlobalKey<FormState>();
  final _institutionController = TextEditingController();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _credentialsController = TextEditingController();
  final _workEmailController = TextEditingController();
  final _workPhoneController = TextEditingController();
  final _extensionController = TextEditingController();
  bool _joinTrustLedger = false;
  bool _isLoading = false;
  
  @override
  void dispose() {
    _institutionController.dispose();
    _firstNameController.dispose();
    _lastNameController.dispose();
    _credentialsController.dispose();
    _workEmailController.dispose();
    _workPhoneController.dispose();
    _extensionController.dispose();
    super.dispose();
  }
  
  Future<void> _handleCreateAccount() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);
      
      final apiService = Provider.of<ApiService>(context, listen: false);
      
      try {
        // Create professional contact
        final request = ContactCreateRequest(
          email: _workEmailController.text.trim(),
          firstName: _firstNameController.text.trim(),
          lastName: _lastNameController.text.trim(),
          phone: _workPhoneController.text.trim(),
          consentGranted: true,
        );
        
        await apiService.createContact(request);
        
        if (mounted) {
          setState(() => _isLoading = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Professional account created successfully'),
              backgroundColor: AppColors.success,
            ),
          );
          context.go('/professional/dashboard');
        }
      } catch (e) {
        if (mounted) {
          setState(() => _isLoading = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to create account: ${e.toString()}'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
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
        title: const Text('Create Professional Account'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Institution Field
                VCTextField(
                  label: 'Institution or Professional',
                  hint: 'Institution or Professional',
                  controller: _institutionController,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter institution or professional name';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                
                // Mandate Administrator Section
                Text(
                  'Mandate Administrator',
                  style: AppTextStyles.h6,
                ),
                const SizedBox(height: 16),
                
                // First Name and Last Name Row
                Row(
                  children: [
                    Expanded(
                      child: VCTextField(
                        label: 'First name',
                        hint: 'First name',
                        controller: _firstNameController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Required';
                          }
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: VCTextField(
                        label: 'Last name',
                        hint: 'Last name',
                        controller: _lastNameController,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Required';
                          }
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                
                // Credentials (Optional)
                VCTextField(
                  label: 'Credentials (optional)',
                  hint: 'Credentials (optional)',
                  controller: _credentialsController,
                ),
                const SizedBox(height: 16),
                
                // Work Email
                VCTextField(
                  label: 'Work email',
                  hint: 'Work email',
                  controller: _workEmailController,
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: Icons.email_outlined,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter work email';
                    }
                    if (!value.contains('@')) {
                      return 'Please enter a valid email';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                // Work Phone and Extension Row
                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: VCTextField(
                        label: 'Work phone number',
                        hint: 'Work phone number',
                        controller: _workPhoneController,
                        keyboardType: TextInputType.phone,
                        prefixIcon: Icons.phone_outlined,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Required';
                          }
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: VCTextField(
                        label: 'Ext. (optional)',
                        hint: 'Ext. (optional)',
                        controller: _extensionController,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                
                // Trust Ledger Checkbox
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Checkbox(
                      value: _joinTrustLedger,
                      onChanged: (value) {
                        setState(() => _joinTrustLedger = value ?? false);
                      },
                      activeColor: AppColors.primary,
                    ),
                    Expanded(
                      child: Text(
                        'Join the Trust Ledger of Verified Attorneys',
                        style: AppTextStyles.body2,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                
                // Create Account Button
                VCButton(
                  text: 'Create Account',
                  onPressed: _isLoading ? null : _handleCreateAccount,
                  isLoading: _isLoading,
                  width: double.infinity,
                ),
                const SizedBox(height: 24),
                
                // Sign In Link
                Center(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Already have an account? ',
                        style: AppTextStyles.body2,
                      ),
                      TextButton(
                        onPressed: () {
                          context.pop();
                        },
                        child: Text(
                          'Sign In',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

