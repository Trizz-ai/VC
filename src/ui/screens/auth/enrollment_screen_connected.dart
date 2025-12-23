import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:camera/camera.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/vc_button.dart';
import '../../../../frontend/lib/core/services/biometric_service.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// Enrollment screen with facial recognition - Connected to Backend
class EnrollmentScreenConnected extends StatefulWidget {
  const EnrollmentScreenConnected({Key? key}) : super(key: key);
  
  @override
  State<EnrollmentScreenConnected> createState() => _EnrollmentScreenConnectedState();
}

class _EnrollmentScreenConnectedState extends State<EnrollmentScreenConnected> {
  bool _isEnrolling = false;
  CameraController? _cameraController;
  List<CameraDescription>? _cameras;
  bool _isCameraInitialized = false;
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  Future<void> _initializeCamera() async {
    try {
      // Get available cameras
      _cameras = await availableCameras();
      
      if (_cameras != null && _cameras!.isNotEmpty) {
        // Use front camera for face enrollment
        final frontCamera = _cameras!.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.front,
          orElse: () => _cameras!.first,
        );
        
        _cameraController = CameraController(
          frontCamera,
          ResolutionPreset.medium,
          enableAudio: false,
        );
        
        await _cameraController!.initialize();
        
        if (mounted) {
          setState(() {
            _isCameraInitialized = true;
          });
        }
      }
    } catch (e) {
      // Handle camera initialization error
      print('Camera initialization error: $e');
    }
  }
  
  Future<void> _handleEnrollFace() async {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      _showError('Camera not ready');
      return;
    }
    
    setState(() => _isEnrolling = true);
    
    try {
      // Capture image
      final image = await _cameraController!.takePicture();
      final imageBytes = await image.readAsBytes();
      
      // Get biometric service
      final apiService = Provider.of<ApiService>(context, listen: false);
      final biometricService = BiometricService(apiService);
      
      // Enroll face
      final result = await biometricService.enrollFace(
        Uint8List.fromList(imageBytes),
        metadata: {
          'enrollment_date': DateTime.now().toIso8601String(),
          'device_type': 'mobile',
        },
      );
      
      if (mounted) {
        setState(() => _isEnrolling = false);
        
        if (result['success'] == true) {
          _showSuccess('Face enrolled successfully!');
          // Navigate to dashboard
          await Future.delayed(const Duration(seconds: 1));
          if (mounted) {
            context.go('/dashboard');
          }
        } else {
          _showError(result['message'] ?? 'Enrollment failed');
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isEnrolling = false);
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
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
        title: const Text('Enrollment'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 32),
              
              // Instructions
              Text(
                'Center your face',
                style: AppTextStyles.h3,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Make sure your face is fully visible and well-lit to enroll successfully.',
                style: AppTextStyles.body1.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              
              // Camera Preview / Facial Recognition Area
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: AppColors.primary,
                      width: 2,
                    ),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(14),
                    child: _buildCameraPreview(),
                  ),
                ),
              ),
              const SizedBox(height: 32),
              
              // Enroll Button
              VCButton(
                text: _isEnrolling ? 'Enrolling Face...' : 'Enroll Face',
                onPressed: _isEnrolling ? null : _handleEnrollFace,
                isLoading: _isEnrolling,
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildCameraPreview() {
    if (!_isCameraInitialized || _cameraController == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: AppColors.primary),
            const SizedBox(height: 16),
            Text(
              'Initializing camera...',
              style: AppTextStyles.body1.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      );
    }
    
    return Stack(
      fit: StackFit.expand,
      children: [
        // Camera preview
        CameraPreview(_cameraController!),
        
        // Face outline overlay
        Center(
          child: Container(
            width: 250,
            height: 300,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.primary,
                width: 3,
                style: BorderStyle.solid,
              ),
            ),
          ),
        ),
        
        // Instructions overlay
        Positioned(
          bottom: 24,
          left: 0,
          right: 0,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.6),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'Position your face within the circle',
              style: AppTextStyles.body2.copyWith(
                color: Colors.white,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ],
    );
  }
}



