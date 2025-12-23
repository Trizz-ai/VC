import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:verified_compliance/features/auth/screens/onboarding_screen.dart';
import 'package:verified_compliance/features/auth/screens/login_screen.dart';
import 'package:verified_compliance/features/auth/screens/registration_screen.dart';
import 'package:verified_compliance/features/dashboard/screens/dashboard_screen.dart';
import 'package:verified_compliance/features/settings/screens/settings_screen.dart';
import 'package:verified_compliance/features/profile/screens/profile_edit_screen.dart';
import 'package:verified_compliance/features/offline/screens/offline_queue_screen.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  // Helper function to wrap widget with MaterialApp and theme
  Widget wrapWithApp(Widget screen) {
    return MaterialApp(
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: screen,
    );
  }

  group('Screen Screenshots - Working Screens', () {
    testWidgets('Onboarding Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const OnboardingScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(OnboardingScreen),
        matchesGoldenFile('goldens/onboarding_screen.png'),
      );
    });

    testWidgets('Login Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const LoginScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(LoginScreen),
        matchesGoldenFile('goldens/login_screen.png'),
      );
    });

    testWidgets('Registration Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const RegistrationScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(RegistrationScreen),
        matchesGoldenFile('goldens/registration_screen.png'),
      );
    });

    testWidgets('Dashboard Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const DashboardScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(DashboardScreen),
        matchesGoldenFile('goldens/dashboard_screen.png'),
      );
    });

    testWidgets('Settings Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const SettingsScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(SettingsScreen),
        matchesGoldenFile('goldens/settings_screen.png'),
      );
    });

    testWidgets('Profile Edit Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const ProfileEditScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(ProfileEditScreen),
        matchesGoldenFile('goldens/profile_edit_screen.png'),
      );
    });

    testWidgets('Offline Queue Screen Screenshot', (WidgetTester tester) async {
      await tester.pumpWidget(wrapWithApp(const OfflineQueueScreen()));
      await tester.pumpAndSettle();
      
      await expectLater(
        find.byType(OfflineQueueScreen),
        matchesGoldenFile('goldens/offline_queue_screen.png'),
      );
    });
  });
}
