import 'package:dio/dio.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

/// Local backend default assumes an Android emulator talking to a host machine
/// running uvicorn on localhost:8000. Override with
/// --dart-define=API_BASE_URL=... for a physical device or the deployed URL.
const String _apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

/// Single Dio client for all backend calls, with the current Supabase JWT
/// attached to every request.
class ApiClient {
  ApiClient._internal() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final session = Supabase.instance.client.auth.currentSession;
          if (session != null) {
            options.headers['Authorization'] = 'Bearer ${session.accessToken}';
          }
          handler.next(options);
        },
      ),
    );
  }

  static final ApiClient instance = ApiClient._internal();

  final Dio _dio = Dio(BaseOptions(baseUrl: _apiBaseUrl));

  Dio get dio => _dio;
}
