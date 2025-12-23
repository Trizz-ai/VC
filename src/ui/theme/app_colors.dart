import 'package:flutter/material.dart';

/// Color palette for Verified Compliance dark mode
/// Based on Material Design 3 dark theme guidelines
class AppColors {
  // Primary Colors
  static const Color primary = Color(0xFF2563EB); // Blue-600
  static const Color primaryLight = Color(0xFF3B82F6); // Blue-500
  static const Color primaryDark = Color(0xFF1E40AF); // Blue-700
  
  // Secondary Colors
  static const Color secondary = Color(0xFF10B981); // Green-500
  static const Color secondaryLight = Color(0xFF34D399); // Green-400
  static const Color secondaryDark = Color(0xFF059669); // Green-600
  
  // Background Colors
  static const Color background = Color(0xFF0F172A); // Slate-900
  static const Color surface = Color(0xFF1E293B); // Slate-800
  static const Color surfaceVariant = Color(0xFF334155); // Slate-700
  
  // Text Colors
  static const Color textPrimary = Color(0xFFF1F5F9); // Slate-100
  static const Color textSecondary = Color(0xFF94A3B8); // Slate-400
  static const Color textTertiary = Color(0xFF64748B); // Slate-500
  static const Color textDisabled = Color(0xFF475569); // Slate-600
  
  // On Colors (text on colored backgrounds)
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onSecondary = Color(0xFFFFFFFF);
  static const Color onSurface = Color(0xFFF1F5F9);
  static const Color onBackground = Color(0xFFF1F5F9);
  static const Color onError = Color(0xFFFFFFFF);
  
  // Status Colors
  static const Color success = Color(0xFF10B981); // Green-500
  static const Color warning = Color(0xFFF59E0B); // Amber-500
  static const Color error = Color(0xFFEF4444); // Red-500
  static const Color info = Color(0xFF3B82F6); // Blue-500
  
  // Icon Colors
  static const Color iconPrimary = Color(0xFFF1F5F9);
  static const Color iconSecondary = Color(0xFF94A3B8);
  static const Color iconDisabled = Color(0xFF475569);
  
  // Input Colors
  static const Color inputBackground = Color(0xFF1E293B); // Slate-800
  static const Color inputBorder = Color(0xFF334155); // Slate-700
  static const Color inputFocused = Color(0xFF2563EB); // Primary
  
  // Divider
  static const Color divider = Color(0xFF334155); // Slate-700
  
  // Chip / Badge Colors
  static const Color chipBackground = Color(0xFF334155); // Slate-700
  static const Color chipSelected = Color(0xFF2563EB); // Primary
  
  // Map Colors
  static const Color mapPinUser = Color(0xFF3B82F6); // Blue-500
  static const Color mapPinMeeting = Color(0xFF8B5CF6); // Purple-500
  static const Color mapPinVerified = Color(0xFF10B981); // Green-500
  
  // Chart Colors
  static const List<Color> chartColors = [
    Color(0xFF3B82F6), // Blue
    Color(0xFF10B981), // Green
    Color(0xFF8B5CF6), // Purple
    Color(0xFFF59E0B), // Amber
    Color(0xFFEC4899), // Pink
    Color(0xFF06B6D4), // Cyan
  ];
  
  // Gradient Colors
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF2563EB), Color(0xFF1E40AF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient successGradient = LinearGradient(
    colors: [Color(0xFF10B981), Color(0xFF059669)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient errorGradient = LinearGradient(
    colors: [Color(0xFFEF4444), Color(0xFFDC2626)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  // Shadow Colors
  static const Color shadowLight = Color(0x1A000000);
  static const Color shadowMedium = Color(0x33000000);
  static const Color shadowDark = Color(0x4D000000);
  
  // Overlay Colors
  static const Color overlayLight = Color(0x0DFFFFFF);
  static const Color overlayMedium = Color(0x1AFFFFFF);
  static const Color overlayDark = Color(0x33FFFFFF);
  
  // Special Colors
  static const Color verified = Color(0xFF10B981); // Green-500
  static const Color pending = Color(0xFFF59E0B); // Amber-500
  static const Color failed = Color(0xFFEF4444); // Red-500
  static const Color cancelled = Color(0xFF64748B); // Slate-500
}



