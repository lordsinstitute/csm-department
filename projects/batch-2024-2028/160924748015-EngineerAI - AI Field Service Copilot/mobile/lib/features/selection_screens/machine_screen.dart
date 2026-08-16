import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/colors.dart';
import '../../shared_widgets/selection_grid.dart';
import '../../state/catalog_providers.dart';
import '../../state/inspection_session.dart';

class MachineScreen extends ConsumerWidget {
  final String departmentId;

  const MachineScreen({super.key, required this.departmentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final machinesAsync = ref.watch(machinesProvider(departmentId));
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Select Machine')),
      body: machinesAsync.when(
        data: (machines) => SelectionGrid(
          items: machines
              .map((m) => SelectionGridItem(id: m.id, title: m.name))
              .toList(),
          onSelect: (id) {
            ref.read(inspectionSessionProvider.notifier).selectMachine(id);
            context.go('/machines/$id/problems');
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            Center(child: Text('Failed to load machines: $error')),
      ),
    );
  }
}
