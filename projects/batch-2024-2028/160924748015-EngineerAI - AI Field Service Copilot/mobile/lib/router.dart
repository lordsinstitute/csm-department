import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'core/theme/colors.dart';
import 'core/theme/typography.dart';
import 'features/auth/splash_screen.dart';
import 'features/home/home_screen.dart';
import 'features/selection_screens/department_screen.dart';
import 'features/selection_screens/machine_screen.dart';
import 'features/selection_screens/problem_screen.dart';

/// Every route from plan §8-9. Screens not yet built (Session 5+) render a
/// labeled placeholder so the router shell is complete from Day 1.
final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', builder: (context, state) => const SplashScreen()),
    GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
    GoRoute(
      path: '/departments',
      builder: (context, state) => const DepartmentScreen(),
    ),
    GoRoute(
      path: '/departments/:departmentId/machines',
      builder: (context, state) => MachineScreen(
        departmentId: state.pathParameters['departmentId']!,
      ),
    ),
    GoRoute(
      path: '/machines/:machineId/problems',
      builder: (context, state) => ProblemScreen(
        machineId: state.pathParameters['machineId']!,
      ),
    ),
    GoRoute(
      path: '/photo-capture',
      builder: (context, state) => const _PlaceholderScreen(label: 'Photo Capture'),
    ),
    GoRoute(
      path: '/vision-loading',
      builder: (context, state) => const _PlaceholderScreen(label: 'Vision Analysis'),
    ),
    GoRoute(
      path: '/questions',
      builder: (context, state) => const _PlaceholderScreen(label: 'Guided Questions'),
    ),
    GoRoute(
      path: '/diagnosis-loading',
      builder: (context, state) => const _PlaceholderScreen(label: 'Diagnosis'),
    ),
    GoRoute(
      path: '/root-cause',
      builder: (context, state) => const _PlaceholderScreen(label: 'Root Cause Analysis'),
    ),
    GoRoute(
      path: '/repair-instructions',
      builder: (context, state) => const _PlaceholderScreen(label: 'Repair Instructions'),
    ),
    GoRoute(
      path: '/repair-checklist',
      builder: (context, state) => const _PlaceholderScreen(label: 'Repair Checklist'),
    ),
    GoRoute(
      path: '/report',
      builder: (context, state) => const _PlaceholderScreen(label: 'Report Preview'),
    ),
    GoRoute(
      path: '/history',
      builder: (context, state) => const _PlaceholderScreen(label: 'Inspection History'),
    ),
    GoRoute(
      path: '/history/:inspectionId',
      builder: (context, state) => _PlaceholderScreen(
        label: 'Inspection Detail (${state.pathParameters['inspectionId']})',
      ),
    ),
  ],
);

class _PlaceholderScreen extends StatelessWidget {
  final String label;

  const _PlaceholderScreen({required this.label});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: Text(label)),
      body: Center(
        child: Text(
          '$label -- coming soon',
          style: AppTypography.body.copyWith(color: AppColors.textSecondary),
        ),
      ),
    );
  }
}
