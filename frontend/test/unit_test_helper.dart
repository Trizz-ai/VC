import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../lib/core/services/api_service.dart';
import '../lib/core/services/auth_service.dart';
import '../lib/core/services/location_service.dart';
import '../lib/core/services/storage_service.dart';
import '../lib/features/auth/providers/auth_provider.dart';
import '../lib/features/sessions/providers/session_provider.dart';
import '../lib/features/meetings/providers/meeting_provider.dart';

// Test helper functions for real implementations
class TestHelper {
  static Widget createTestApp({
    required Widget child,
    List<ChangeNotifierProvider>? providers,
  }) {
    return MaterialApp(
      home: providers != null && providers.isNotEmpty
          ? MultiProvider(
              providers: providers,
              child: child,
            )
          : child,
    );
  }

  static Widget createTestAppWithProviders({
    required Widget child,
    ApiService? apiService,
    AuthService? authService,
    LocationService? locationService,
    StorageService? storageService,
  }) {
    final providers = <ChangeNotifierProvider>[];
    
    if (storageService != null) {
      providers.add(
        ChangeNotifierProvider<StorageService>(
          create: (_) => storageService,
        ),
      );
    }
    
    if (authService != null) {
      providers.add(
        ChangeNotifierProvider<AuthService>(
          create: (_) => authService,
        ),
      );
    }
    
    if (apiService != null) {
      providers.add(
        ChangeNotifierProvider<ApiService>(
          create: (_) => apiService,
        ),
      );
    }
    
    if (locationService != null) {
      providers.add(
        ChangeNotifierProvider<LocationService>(
          create: (_) => locationService,
        ),
      );
    }
    
    return createTestApp(
      child: child,
      providers: providers,
    );
  }

  static Future<void> setupSharedPreferences() async {
    // Use real SharedPreferences instead of mock
    // Initialize with real SharedPreferences instance
    await SharedPreferences.getInstance();
  }

  static Future<void> setupRealServices() async {
    // Setup real services for testing
    await setupSharedPreferences();
  }

  static Widget createTestWidget({
    required Widget child,
    List<ChangeNotifierProvider>? providers,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: providers != null && providers.isNotEmpty
            ? MultiProvider(
                providers: providers,
                child: child,
              )
            : child,
      ),
    );
  }

  static Widget createTestScreen({
    required Widget screen,
    List<ChangeNotifierProvider>? providers,
  }) {
    return MaterialApp(
      home: providers != null && providers.isNotEmpty
          ? MultiProvider(
              providers: providers,
              child: screen,
            )
          : screen,
    );
  }

  static Future<void> setupRealDatabase() async {
    // Setup real database for testing
    // This would initialize a real test database
    // instead of using mocks
  }

  static Future<void> setupRealLocationServices() async {
    // Setup real location services for testing
    // This would initialize real location services
    // instead of using mocks
  }

  static Future<void> setupRealApiServices() async {
    // Setup real API services for testing
    // This would initialize real API services
    // instead of using mocks
  }

  static Future<void> setupRealAuthServices() async {
    // Setup real authentication services for testing
    // This would initialize real auth services
    // instead of using mocks
  }

  static Future<void> setupAllRealServices() async {
    // Setup all real services for testing
    await setupSharedPreferences();
    await setupRealDatabase();
    await setupRealLocationServices();
    await setupRealApiServices();
    await setupRealAuthServices();
  }

  static Widget createTestAppWithRealServices({
    required Widget child,
  }) {
    return MaterialApp(
      home: MultiProvider(
        providers: [
          ChangeNotifierProvider<StorageService>(
            create: (_) => StorageService(),
          ),
          ChangeNotifierProvider<AuthService>(
            create: (_) => AuthService(),
          ),
          ChangeNotifierProvider<ApiService>(
            create: (_) => ApiService(),
          ),
          ChangeNotifierProvider<LocationService>(
            create: (_) => LocationService(),
          ),
          ChangeNotifierProvider<AuthProvider>(
            create: (_) => AuthProvider(),
          ),
          ChangeNotifierProvider<SessionProvider>(
            create: (_) => SessionProvider(),
          ),
          ChangeNotifierProvider<MeetingProvider>(
            create: (_) => MeetingProvider(),
          ),
        ],
        child: child,
      ),
    );
  }

  static Future<void> cleanupRealServices() async {
    // Cleanup real services after testing
    // This would clean up any real resources
    // that were created during testing
  }

  static Future<void> resetRealDatabase() async {
    // Reset real database after testing
    // This would reset the real test database
    // to a clean state
  }

  static Future<void> resetRealLocationServices() async {
    // Reset real location services after testing
    // This would reset the real location services
    // to a clean state
  }

  static Future<void> resetRealApiServices() async {
    // Reset real API services after testing
    // This would reset the real API services
    // to a clean state
  }

  static Future<void> resetRealAuthServices() async {
    // Reset real authentication services after testing
    // This would reset the real auth services
    // to a clean state
  }

  static Future<void> resetAllRealServices() async {
    // Reset all real services after testing
    await cleanupRealServices();
    await resetRealDatabase();
    await resetRealLocationServices();
    await resetRealApiServices();
    await resetRealAuthServices();
  }
}