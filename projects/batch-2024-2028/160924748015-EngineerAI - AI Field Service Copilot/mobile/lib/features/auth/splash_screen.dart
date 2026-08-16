import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/colors.dart';
import '../../core/theme/spacing.dart';
import '../../core/theme/typography.dart';
import '../../shared_widgets/primary_button.dart';
import '../../state/auth_notifier.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  bool _loading = false;

  Future<void> _continue() async {
    setState(() => _loading = true);
    try {
      await signInAnonymously();
      if (mounted) context.go('/home');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.precision_manufacturing,
                size: 72,
                color: AppColors.primary,
              ),
              const SizedBox(height: AppSpacing.md),
              Text(
                'EngineerAI',
                style: AppTypography.display.copyWith(color: AppColors.textPrimary),
              ),
              const SizedBox(height: AppSpacing.xl),
              PrimaryButton(
                label: _loading ? 'Signing in...' : 'Continue',
                onPressed: _loading ? null : _continue,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
