import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'core/theme/colors.dart';
import 'core/theme/typography.dart';
import 'router.dart';

// Provide these via --dart-define-from-file=dart_define.json (see
// dart_define.example.json for the keys). API_BASE_URL is read separately in
// core/api_client.dart with its own default for the Android emulator.
const String _supabaseUrl = String.fromEnvironment('SUPABASE_URL');
const String _supabaseAnonKey = String.fromEnvironment('SUPABASE_ANON_KEY');

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: _supabaseUrl, publishableKey: _supabaseAnonKey);
  runApp(const ProviderScope(child: EngineerAIApp()));
}

class EngineerAIApp extends StatelessWidget {
  const EngineerAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'EngineerAI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          primary: AppColors.primary,
          error: AppColors.error,
          surface: AppColors.surface,
        ),
        textTheme: const TextTheme(
          displayLarge: AppTypography.display,
          headlineMedium: AppTypography.headline,
          titleLarge: AppTypography.title,
          bodyLarge: AppTypography.body,
          bodyMedium: AppTypography.body,
          labelLarge: AppTypography.label,
          bodySmall: AppTypography.caption,
        ).apply(
          bodyColor: AppColors.textPrimary,
          displayColor: AppColors.textPrimary,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: AppColors.surface,
          foregroundColor: AppColors.textPrimary,
          elevation: 0,
        ),
      ),
      routerConfig: appRouter,
    );
  }
}
