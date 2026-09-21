import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/colors.dart';
import '../../shared_widgets/selection_grid.dart';
import '../../state/catalog_providers.dart';

class DepartmentScreen extends ConsumerWidget {
  const DepartmentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final departmentsAsync = ref.watch(departmentsProvider);
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Select Department')),
      body: departmentsAsync.when(
        data: (departments) => SelectionGrid(
          items: departments
              .map((d) => SelectionGridItem(id: d.id, title: d.name))
              .toList(),
          onSelect: (id) => context.go('/departments/$id/machines'),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            Center(child: Text('Failed to load departments: $error')),
      ),
    );
  }
}
