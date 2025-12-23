import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'package:frontend/main.dart' as app;
import 'package:frontend/features/auth/providers/auth_provider.dart';
import 'package:frontend/features/sessions/providers/session_provider.dart';
import 'package:frontend/features/meetings/providers/meeting_provider.dart';
import 'package:frontend/core/services/api_service.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Complete User Journey Integration Tests', () {
    testWidgets('New user registration and login flow', (WidgetTester tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle();

      // Should be on onboarding screen
      expect(find.text('Get Started'), findsOneWidget);
      
      // Tap Get Started
      await tester.tap(find.text('Get Started'));
      await tester.pumpAndSettle();

      // Should navigate to login screen
      expect(find.text('Login'), findsOneWidget);
      
      // Tap "Don't have an account? Register"
      await tester.tap(find.text('Register'));
      await tester.pumpAndSettle();

      // Should be on registration screen
      expect(find.text('Create Account'), findsOneWidget);
      
      // Fill registration form
      final emailField = find.byKey(Key('registration_email'));
      final passwordField = find.byKey(Key('registration_password'));
      final firstNameField = find.byKey(Key('registration_first_name'));
      final lastNameField = find.byKey(Key('registration_last_name'));
      final consentCheckbox = find.byKey(Key('consent_checkbox'));
      
      await tester.enterText(emailField, 'testuser@example.com');
      await tester.enterText(passwordField, 'SecurePass123!');
      await tester.enterText(firstNameField, 'Test');
      await tester.enterText(lastNameField, 'User');
      await tester.tap(consentCheckbox);
      await tester.pumpAndSettle();

      // Submit registration
      await tester.tap(find.text('Register'));
      await tester.pumpAndSettle(Duration(seconds: 3));

      // Should navigate to dashboard after successful registration
      expect(find.text('Dashboard'), findsOneWidget);
    });

    testWidgets('Meeting discovery and session creation flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Assume user is already logged in for this test
      // Navigate to meetings screen
      await tester.tap(find.byIcon(Icons.search));
      await tester.pumpAndSettle();

      // Should be on meetings screen
      expect(find.text('Meetings'), findsOneWidget);
      
      // Tap on nearby tab
      await tester.tap(find.text('Nearby'));
      await tester.pumpAndSettle(Duration(seconds: 2));

      // Should show meetings or empty state
      // If meetings exist, tap on first one
      final meetingCard = find.byType(Card).first;
      if (tester.any(meetingCard)) {
        await tester.tap(meetingCard);
        await tester.pumpAndSettle();

        // Should be on meeting detail screen
        expect(find.text('Meeting Details'), findsOneWidget);
        
        // Tap Start Session button
        await tester.tap(find.text('Start Session'));
        await tester.pumpAndSettle(Duration(seconds: 2));

        // Should navigate to session detail screen
        expect(find.text('Check In'), findsOneWidget);
      }
    });

    testWidgets('Session check-in and check-out flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to active session (if exists)
      await tester.tap(find.byIcon(Icons.access_time));
      await tester.pumpAndSettle();

      // If active session exists
      if (tester.any(find.text('Active Session'))) {
        // Tap check-in button
        await tester.tap(find.text('Check In'));
        await tester.pumpAndSettle(Duration(seconds: 2));

        // Should show success message
        expect(find.byType(SnackBar), findsOneWidget);
        
        // Wait a moment then check-out
        await tester.pump(Duration(seconds: 5));
        
        // Tap check-out button
        await tester.tap(find.text('Check Out'));
        await tester.pumpAndSettle(Duration(seconds: 2));

        // Should show success message
        expect(find.byType(SnackBar), findsOneWidget);
      }
    });

    testWidgets('Session history viewing', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to sessions screen
      await tester.tap(find.text('Sessions'));
      await tester.pumpAndSettle();

      // Should show session history screen
      expect(find.text('Session History'), findsOneWidget);
      
      // Should show sessions or empty state
      // If sessions exist, tap on first one
      final sessionCard = find.byType(Card).first;
      if (tester.any(sessionCard)) {
        await tester.tap(sessionCard);
        await tester.pumpAndSettle();

        // Should show session detail
        expect(find.byIcon(Icons.timeline), findsOneWidget);
      }
    });

    testWidgets('Profile management flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Should be on settings screen
      expect(find.text('Settings'), findsOneWidget);
      
      // Tap Edit Profile
      await tester.tap(find.text('Edit Profile'));
      await tester.pumpAndSettle();

      // Should be on profile edit screen
      expect(find.text('Edit Profile'), findsOneWidget);
      
      // Update first name
      final firstNameField = find.byKey(Key('profile_first_name'));
      await tester.enterText(firstNameField, 'Updated');
      await tester.pumpAndSettle();

      // Save changes
      await tester.tap(find.text('Save'));
      await tester.pumpAndSettle(Duration(seconds: 2));

      // Should navigate back and show success
      expect(find.byType(SnackBar), findsOneWidget);
    });

    testWidgets('Offline queue management', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Tap Offline Queue
      await tester.tap(find.text('Offline Queue'));
      await tester.pumpAndSettle();

      // Should show offline queue screen
      expect(find.text('Offline Queue'), findsOneWidget);
      
      // Should show queue status
      expect(find.byKey(Key('queue_status')), findsOneWidget);
    });

    testWidgets('Search meetings functionality', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to meetings
      await tester.tap(find.text('Meetings'));
      await tester.pumpAndSettle();

      // Tap search button
      await tester.tap(find.byIcon(Icons.search));
      await tester.pumpAndSettle();

      // Enter search query
      final searchField = find.byType(TextField);
      await tester.enterText(searchField, 'AA Meeting');
      await tester.pumpAndSettle(Duration(seconds: 2));

      // Should show search results
      expect(find.byType(ListView), findsOneWidget);
    });

    testWidgets('Pull to refresh functionality', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Go to dashboard
      expect(find.text('Dashboard'), findsOneWidget);
      
      // Pull to refresh
      await tester.drag(find.byType(RefreshIndicator), Offset(0, 300));
      await tester.pumpAndSettle(Duration(seconds: 2));

      // Should refresh data
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('Logout flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Tap Logout
      await tester.tap(find.text('Logout'));
      await tester.pumpAndSettle();

      // Should show confirmation dialog
      expect(find.text('Are you sure you want to logout?'), findsOneWidget);
      
      // Confirm logout
      await tester.tap(find.text('Logout'));
      await tester.pumpAndSettle(Duration(seconds: 2));

      // Should navigate to login screen
      expect(find.text('Login'), findsOneWidget);
    });
  });

  group('Error Handling Tests', () {
    testWidgets('Invalid login credentials', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to login
      await tester.tap(find.text('Get Started'));
      await tester.pumpAndSettle();

      // Enter invalid credentials
      await tester.enterText(find.byKey(Key('login_email')), 'invalid@example.com');
      await tester.enterText(find.byKey(Key('login_password')), 'wrongpassword');
      await tester.pumpAndSettle();

      // Tap login
      await tester.tap(find.text('Login'));
      await tester.pumpAndSettle(Duration(seconds: 2));

      // Should show error message
      expect(find.byType(SnackBar), findsOneWidget);
      expect(find.text('Login'), findsOneWidget); // Still on login screen
    });

    testWidgets('Network error handling', (WidgetTester tester) async {
      // This test would require mocking network calls
      // Placeholder for network error test
      app.main();
      await tester.pumpAndSettle();
      
      // Test implementation depends on your error handling setup
    });
  });

  group('GPS and Location Tests', () {
    testWidgets('Location permission request', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Check location permission status
      expect(find.text('Location'), findsOneWidget);
    });
  });
}



