import 'package:flutter/material.dart';

import '../core/theme/colors.dart';
import '../core/theme/spacing.dart';
import '../core/theme/typography.dart';

/// Filled primary/main-CTA button per design_tokens.md section 4.
/// Pressed -> primaryDark, disabled -> disabledBg (onPressed == null).
class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;

  const PrimaryButton({super.key, required this.label, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: AppSpacing.primaryButtonHeight,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ButtonStyle(
          elevation: const WidgetStatePropertyAll(0),
          shape: WidgetStatePropertyAll(
            RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusButton),
            ),
          ),
          foregroundColor: const WidgetStatePropertyAll(AppColors.onPrimary),
          backgroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.disabled)) return AppColors.disabledBg;
            if (states.contains(WidgetState.pressed)) return AppColors.primaryDark;
            return AppColors.primary;
          }),
        ),
        child: Text(label, style: AppTypography.bodyBold),
      ),
    );
  }
}
