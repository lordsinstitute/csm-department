import 'package:flutter/material.dart';

/// Color tokens from design/design_tokens.md section 1. Do not hardcode colors
/// anywhere else in the app -- add a token here first.
class AppColors {
  AppColors._();

  static const Color primary = Color(0xFF16548C);
  static const Color primaryDark = Color(0xFF0F3D61);
  static const Color primaryTint = Color(0xFFE9F1F8);

  static const Color background = Color(0xFFF4F6F8);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFD8DEE4);

  static const Color textPrimary = Color(0xFF1A202C);
  static const Color textSecondary = Color(0xFF5A6572);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color disabledBg = Color(0xFFC7D4E0);

  static const Color success = Color(0xFF1E7B44);
  static const Color successTint = Color(0xFFE6F4EC);
  static const Color successTintText = Color(0xFF14532D);

  static const Color warning = Color(0xFFB45309);
  static const Color warningTint = Color(0xFFFEF3C7);
  static const Color warningTintText = Color(0xFF7C3A03);

  static const Color error = Color(0xFFB3261E);
  static const Color errorTint = Color(0xFFFDECEA);
  static const Color errorTintText = Color(0xFF7F1D1D);
}
