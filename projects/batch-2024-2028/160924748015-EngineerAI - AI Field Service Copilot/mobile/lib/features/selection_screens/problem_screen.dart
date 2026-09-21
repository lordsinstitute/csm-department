import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/colors.dart';
import '../../shared_widgets/selection_grid.dart';
import '../../state/catalog_providers.dart';
import '../../state/inspection_session.dart';

class ProblemScreen extends ConsumerWidget {
  final String machineId;

  const ProblemScreen({super.key, required this.machineId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final problemsAsync = ref.watch(problemsProvider(machineId));
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Select Problem')),
      body: problemsAsync.when(
        data: (problems) => SelectionGrid(
          items: problems
              .map((p) => SelectionGridItem(id: p.id, title: p.name))
              .toList(),
          onSelect: (id) {
            ref.read(inspectionSessionProvider.notifier).selectProblem(id);
            context.go('/photo-capture');
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            Center(child: Text('Failed to load problems: $error')),
      ),
    );
  }
}
