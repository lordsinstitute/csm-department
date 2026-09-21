import 'package:flutter/material.dart';

import '../core/theme/colors.dart';
import '../core/theme/spacing.dart';
import '../core/theme/typography.dart';

class SelectionGridItem {
  final String id;
  final String title;
  final IconData icon;

  const SelectionGridItem({
    required this.id,
    required this.title,
    this.icon = Icons.precision_manufacturing,
  });
}

/// Shared grid used by the department/machine/problem selection screens.
class SelectionGrid extends StatelessWidget {
  final List<SelectionGridItem> items;
  final ValueChanged<String> onSelect;

  const SelectionGrid({super.key, required this.items, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.all(AppSpacing.screenPaddingHorizontal),
      itemCount: items.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: AppSpacing.cardGap,
        crossAxisSpacing: AppSpacing.cardGap,
        childAspectRatio: 1.1,
      ),
      itemBuilder: (context, index) {
        final item = items[index];
        return _SelectionCard(item: item, onTap: () => onSelect(item.id));
      },
    );
  }
}

class _SelectionCard extends StatelessWidget {
  final SelectionGridItem item;
  final VoidCallback onTap;

  const _SelectionCard({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.surface,
      borderRadius: BorderRadius.circular(AppSpacing.radiusCard),
      child: InkWell(
        borderRadius: BorderRadius.circular(AppSpacing.radiusCard),
        onTap: onTap,
        child: Container(
          constraints: const BoxConstraints(
            minHeight: AppSpacing.selectionCardMinHeight,
          ),
          padding: const EdgeInsets.all(AppSpacing.md),
          decoration: BoxDecoration(
            border: Border.all(color: AppColors.border),
            borderRadius: BorderRadius.circular(AppSpacing.radiusCard),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircleAvatar(
                radius: 20,
                backgroundColor: AppColors.primaryTint,
                child: Icon(item.icon, color: AppColors.primary),
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                item.title,
                style: AppTypography.title.copyWith(color: AppColors.textPrimary),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
