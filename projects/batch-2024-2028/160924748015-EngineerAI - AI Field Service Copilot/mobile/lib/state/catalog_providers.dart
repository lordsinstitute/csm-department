import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api_client.dart';
import '../models/inspection_models.dart';
import '../models/reference_models.dart';

final departmentsProvider = FutureProvider<List<Department>>((ref) async {
  final response = await ApiClient.instance.dio.get('/departments');
  return (response.data as List)
      .map((e) => Department.fromJson(e as Map<String, dynamic>))
      .toList();
});

final machinesProvider = FutureProvider.family<List<Machine>, String>(
  (ref, departmentId) async {
    final response = await ApiClient.instance.dio.get(
      '/departments/$departmentId/machines',
    );
    return (response.data as List)
        .map((e) => Machine.fromJson(e as Map<String, dynamic>))
        .toList();
  },
);

final problemsProvider = FutureProvider.family<List<Problem>, String>(
  (ref, machineId) async {
    final response = await ApiClient.instance.dio.get(
      '/machines/$machineId/problems',
    );
    return (response.data as List)
        .map((e) => Problem.fromJson(e as Map<String, dynamic>))
        .toList();
  },
);

final historyProvider = FutureProvider<List<InspectionSummary>>((ref) async {
  final response = await ApiClient.instance.dio.get('/inspections');
  return (response.data as List)
      .map((e) => InspectionSummary.fromJson(e as Map<String, dynamic>))
      .toList();
});
